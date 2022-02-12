from typing import Optional
from pprint import pprint
from time import sleep
import random
import os

from vk_api.bot_longpoll import VkBotEventType

from bot_types.VideoDownloadSettings import VideoDownloadSettings
from bot_types.AudioConvertSettings import AudioConvertSettings
from services.ConverterService import ConverterService
from services.VkMessageService import VkMesasgeService
from bot_enums.VkVideoPlatform import VkVideoPlatform
from services.VkAudioService import VkAudioService
from services.VideoService import VideoService
from bot_types.AudioInfo import AudioInfo
import __init__
import config


def process_vk_video(vk_video_obj: dict, video_file_name: str) -> Optional[str]:
    video = vk_video_obj
    player_link = ""

    if video.get("converting") or video.get("duration") == None or video.get("duration") > config.VIDEO_MAX_DURATION:
        return None

    if video.get('platform') == VkVideoPlatform.VK.value \
        or video.get('platform') == VkVideoPlatform.YOUTUBE.value:
            player_link = __init__.vk_user_session.get_api().video.get(
                owner_id= video['owner_id'],
                videos= f"{video['owner_id']}_{video['id']}_{video['access_key']}",
            )['items'][0]['player']
    else:
        return None

    try:
        video_info = VideoService.get_video_info(player_link)
        video_file_name = VideoService.download_video(
            player_link, 
            VideoDownloadSettings(config.VIDEO_MIN_DURATION, config.VIDEO_MAX_DURATION, None, f"{video_file_name}")
        )
        audio_file_name = ConverterService.convert_video_to_audio(video_file_name, AudioConvertSettings(config.AUDIO_MIN_DURATION))
        audio_content_id = VkAudioService.upload_audio(config.DIRS['audios'] + f'/{audio_file_name}', AudioInfo(
            artist=video_info.author,
            title=video_info.title,
        ))
    except:
        return None
    finally:
        if os.path.exists(config.DIRS['videos'] + f'/{video_file_name}'):
            os.remove(config.DIRS['videos'] + f'/{video_file_name}')
        if os.path.exists(config.DIRS['audios'] + f'/{audio_file_name}'):
            os.remove(config.DIRS['audios'] + f'/{audio_file_name}')

    archive_group_content_id = VkAudioService.add_audio(audio_content_id, config.VK_ARCHIVE_GROUP_ID)
    VkAudioService.delete_audio(audio_content_id)

    return archive_group_content_id


def process_msg(msg):
    if msg is None:
        return
    elif msg['from_id'] == -int(config.VK_MAIN_GROUP_ID):
        return

    videos = VkMesasgeService.get_videos_from_message(msg)

    if not len(videos):
        __init__.vk_main_group_api_session.get_api().messages.send(
            message= 'Не удалось найти видео в сообщении',
            reply_to= msg['id'],
            user_id= msg['peer_id'],
            random_id= random.randint(0, 1 << 31),
        )
        return
    
    vk_audio_content_ids = []
    for video_id in range(0, len(videos)):
        archive_group_content_id = process_vk_video(videos[video_id], f"{msg['id']}_{video_id}")

        if archive_group_content_id:
            vk_audio_content_ids.append(archive_group_content_id)
    
    msg_text = ""
    if len(videos) == 1 and not len(vk_audio_content_ids):
        msg_text = "К сожалению, данное видео не поддерживается ботом.\n" \
            + "Возможно, видео слишком длинное, либо его платформа не поддерживается.\n" \
            + "Также возможно, что музыка из этого видео блокируется правообладателями("
    elif len(videos) > 1:
        if len(vk_audio_content_ids) and len(videos) - len(vk_audio_content_ids):
            msg_text = "К сожалению, часть видео не удалось сконвертировать.\n" \
                + "Возможно, некоторые видео слишком длинные (> 10 минут), либо их платформа не поддерживается."
        elif not len(vk_audio_content_ids):
            msg_text = "К сожалению, боту не удалось сконвертировать в аудио ни одно видео.\n" \
                + "Это может быть связяно с тем, что платформы этих видео сейчас не поддерживаются ботом, либо " \
                + "видео длиннее 10 минут."
    
    for part in range(0, parts := (len(vk_audio_content_ids) + config.VK_MAX_ATTACHMENTS) // config.VK_MAX_ATTACHMENTS):
        __init__.vk_main_group_api_session.get_api().messages.send(
            message= f"[{part + 1}/{parts}]" if parts > 1 else msg_text,
            reply_to= msg['id'],
            attachment= "audio" \
                + ",audio".join(vk_audio_content_ids[config.VK_MAX_ATTACHMENTS * part: min(config.VK_MAX_ATTACHMENTS * (part + 1), len(vk_audio_content_ids))]),
            user_id= msg['peer_id'],
            random_id= random.randint(0, 1 << 31),
        )
    
    if len(vk_audio_content_ids) > 10:
        __init__.vk_main_group_api_session.get_api().messages.send(
            message= msg_text,
            reply_to= msg['id'],
            user_id= msg['peer_id'],
            random_id= random.randint(0, 1 << 31),
        )
    

# __В случае временного отключения бота__
# Обрабатываем все неотвеченные сообщения, начиная с самых старых, до тех пор, пока не останется неотвеченных сообщений
print('Начинаю проверять неотвеченные сообщения.' + f' Текущий id последнего отвеченного сообщения = {__init__.last_answered_msg_id}')

get_last_unanswered_msg_id = lambda: __init__.vk_main_group_api_session.get_api().messages.getConversations(
    count= 1
)['items'][0]['last_message']['id']

while __init__.last_answered_msg_id != (last_unanswered_msg_id := get_last_unanswered_msg_id()):
    for msg_id in range(int(__init__.last_answered_msg_id.__str__()) + 1, last_unanswered_msg_id + 1):
        msg = VkMesasgeService.get_message_by_id(__init__.vk_main_group_api_session, msg_id)
        try:
            process_msg(msg)
        except Exception as error:
            pprint(error)
            __init__.error_message_ids += [msg_id]
            print(f"Не удалось обработать сообщение с id = {msg_id}. Перехожу к следующему сообщению.")

        __init__.last_answered_msg_id.set_value(msg_id)

print('Закончил проверять неотвеченные сообщения.' + f' Id последнего отвеченного сообщения = {__init__.last_answered_msg_id}')

# __Штатная работа__
# Последующие новые сообщения обрабатываем с помощью лонгполла
print('Начинаю получать сообщения через лонгполл')
for event in __init__.vk_bot_longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        print('Получил письмо с id = ' + str(event.message.id))
        sleep(1)
        msg = VkMesasgeService.get_message_by_id(__init__.vk_main_group_api_session, event.message.id)
        try:
            process_msg(msg)
        except Exception as error:
            pprint(error)
            __init__.error_message_ids += [event.message.id]
            print(f"Не удалось обработать сообщение с id = {event.message.id}. Перехожу к следующему сообщению.")
        __init__.last_answered_msg_id.set_value(event.message.id)
        print('Обработал письмо с id = ' + str(event.message.id))
