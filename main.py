from typing import Optional
from pprint import pprint
from time import sleep
import random
import os

from vk_api.bot_longpoll import VkBotEventType
import Messages

from bot_types.VideoDownloadSettings import VideoDownloadSettings
from bot_types.AudioConvertSettings import AudioConvertSettings
from services.ConverterService import ConverterService
from services.VkMessageService import VkMesasgeService
from bot_types.VkVideoPlatform import VkVideoPlatform
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

    audio_file_name = None
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
        print(f"Не удалось обработать видео {video_file_name}")
        return None
    finally:
        if os.path.exists(config.DIRS['videos'] + f'/{video_file_name}'):
            os.remove(config.DIRS['videos'] + f'/{video_file_name}')
        if audio_file_name and os.path.exists(config.DIRS['audios'] + f'/{audio_file_name}'):
            os.remove(config.DIRS['audios'] + f'/{audio_file_name}')

    try:
        archive_group_content_id = VkAudioService.add_audio(audio_content_id, config.VK_ARCHIVE_GROUP_ID)
        VkAudioService.delete_audio(audio_content_id)
    except:
        return None

    return archive_group_content_id


def send_audios_to_user(msg: dict, videos: list[dict], vk_audio_content_ids: list[str]):
    msg_text = ""
    if len(videos) == 1 and not len(vk_audio_content_ids):
        msg_text = Messages.video_not_support()
    elif len(videos) > 1:
        if len(vk_audio_content_ids) and len(videos) - len(vk_audio_content_ids):
            msg_text = Messages.failed_to_convert_part_many()
        elif not len(vk_audio_content_ids):
            msg_text = Messages.failed_to_convert_all_many()
    
    for part in range(0, parts := (len(vk_audio_content_ids) + config.VK_MAX_ATTACHMENTS) // config.VK_MAX_ATTACHMENTS):
        try:
            __init__.vk_main_group_api_session.get_api().messages.send(
                message= f"[{part + 1}/{parts}]" if parts > 1 else msg_text,
                reply_to= msg['id'],
                attachment= "audio" \
                    + ",audio".join(vk_audio_content_ids[config.VK_MAX_ATTACHMENTS * part: min(config.VK_MAX_ATTACHMENTS * (part + 1), len(vk_audio_content_ids))]),
                user_id= msg['peer_id'],
                random_id= random.randint(0, 1 << 31),
            )
            pass
        except:
            __init__.vk_main_group_api_session.get_api().messages.send(
                message= f"[{part + 1}/{parts}]" if parts > 1 else msg_text,
                attachment= "audio" \
                    + ",audio".join(vk_audio_content_ids[config.VK_MAX_ATTACHMENTS * part: min(config.VK_MAX_ATTACHMENTS * (part + 1), len(vk_audio_content_ids))]),
                user_id= msg['peer_id'],
                random_id= random.randint(0, 1 << 31),
            )
            pass

    try:
        if len(vk_audio_content_ids) > 10:
            __init__.vk_main_group_api_session.get_api().messages.send(
                message= msg_text,
                reply_to= msg['id'],
                user_id= msg['peer_id'],
                random_id= random.randint(0, 1 << 31),
            )
        pass
    except:
        if len(vk_audio_content_ids) > 10:
            __init__.vk_main_group_api_session.get_api().messages.send(
                message= msg_text,
                user_id= msg['peer_id'],
                random_id= random.randint(0, 1 << 31),
            )
        pass


def process_msg(msg):
    if msg is None:
        return
    elif msg['from_id'] == -int(config.VK_MAIN_GROUP_ID):
        return

    video_attachments = VkMesasgeService.get_video_attachments_from_message(msg)
    # video_links = VkMesasgeService.get_video_links_from_text(msg)

    videos = video_attachments

    if not len(videos):
        __init__.vk_main_group_api_session.get_api().messages.send(
            message= Messages.videos_not_found(),
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
    
    send_audios_to_user(msg, videos, vk_audio_content_ids)


def process_unanswered_messages():
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


def process_longpoll():
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


while True:
    try:
        print("Запуск бота...")

        process_unanswered_messages()
        process_longpoll()
        pass
    except Exception as unpredicted_error:
        print("\n" * 2 + "#" * 30 + "\n" * 2 + "Произошла непредвиденная ошибка.")
        pprint(unpredicted_error)
        print("\n" * 2 + "#" * 30 + "\n")
        print("Перезапуск бота..." + "\n")
