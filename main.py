from pprint import pprint
from vk_api.bot_longpoll import VkBotEventType
import random
import os

from bot_enums.VkVideoPlatform import VkVideoPlatform
from bot_types.VideoDownloadSettings import VideoDownloadSetting
from services.ConverterService import ConverterService
from services.VkMessageService import VkMesasgeService
from services.VkAudioService import VkAudioService
from services.VideoService import VideoService
from bot_types.AudioInfo import AudioInfo
import __init__
import config


def process_msg(msg):
    if msg['from_id'] == -int(config.VK_MAIN_GROUP_ID):
        return

    videos = VkMesasgeService.get_videos_from_message(msg)

    if len(videos) == 0:
        __init__.vk_main_group_api_session.get_api().messages.send(
            message= 'Не удалось найти видео в сообщении',
            reply_to= msg['id'],
            user_id= msg['peer_id'],
            random_id= random.randint(0, 1 << 31),
        )
    
    vk_audio_content_ids = []
    vk_unsupported_videos_count = 0
    for video in videos:
        player_link = ""
        
        if not video.get('platform'):
            if video.get('converting') \
                or not video.get('duration') or 5 >= video['duration'] <= 600:
                vk_unsupported_videos_count += 1

            player_link = __init__.vk_user_session.get_api().video.get(
                owner_id= video['owner_id'],
                videos= f"{video['owner_id']}_{video['id']}_{video['access_key']}",
            )['items'][0]['player']

        elif video.get('platform') == VkVideoPlatform.YOUTUBE:
            vk_unsupported_videos_count += 1
        else:
            vk_unsupported_videos_count += 1

        video_info = VideoService.get_video_info(player_link)
        video_file_name = VideoService.download_video(player_link, VideoDownloadSetting(5, 600, 500))
        audio_file_name = ConverterService.convert_video_to_audio(video_file_name)
        audio_content_id = VkAudioService.upload_audio(config.DIRS['audios'] + f'/{audio_file_name}', AudioInfo(
            artist=video_info.author,
            title=video_info.title,
        ))
        os.remove(config.DIRS['videos'] + f'/{video_file_name}')
        os.remove(config.DIRS['audios'] + f'/{audio_file_name}')

        archive_group_content_id = VkAudioService.add_audio(audio_content_id, config.VK_ARCHIVE_GROUP_ID)
        VkAudioService.delete_audio(audio_content_id)

        vk_audio_content_ids.append(archive_group_content_id)
    
    msg_text = ""
    if len(videos):
        if len(vk_audio_content_ids) and vk_unsupported_videos_count:
            msg_text = "К сожалению, в аудио удалось сконвертировать только часть видео" \
                + ", т.к. на данный момент бот поддерживает только видео ВКонтакте.\n" \
                + "Также бот пока может конвертировать видео длиною от 5 секунд до 10 минут."
        elif not len(vk_audio_content_ids):
            msg_text = "К сожалению, боту не удалось сконвертировать в аудио ни одно видео.\n" \
                + "Это может быть связяно с тем, что платформы этих видео сейчас не поддерживаются ботом, либо " \
                + "длина видео выходит за рамки длины: от 5 секунд до 10 минут."

    __init__.vk_main_group_api_session.get_api().messages.send(
        message= msg_text,
        reply_to= msg['id'],
        attachment= "audio" + ",audio".join(vk_audio_content_ids),
        user_id= msg['peer_id'],
        random_id= random.randint(0, 1 << 31),
    )

# __В случае временного отключения бота__
# Обрабатываем все неотвеченные сообщения, начиная с самых старых, до тех пор, пока не останется неотвеченных сообщений
print('Начинаю проверять неотвеченные сообщения.' + f' Текущий id = {__init__.last_answered_msg_id}')

msg = VkMesasgeService.get_message_by_id(__init__.vk_main_group_api_session, __init__.last_answered_msg_id + 1)
while msg:
    try:
        process_msg(msg)
    except Exception as error:
        pprint(error)
        print(f"Не удалось обработать сообщение с id = {msg['id']}. Перехожу к следующему сообщению.")
    __init__.last_answered_msg_id.set_value(msg['id'])

    msg = VkMesasgeService.get_message_by_id(__init__.vk_main_group_api_session, __init__.last_answered_msg_id + 1)

print('Закончил проверять неотвеченные сообщения.' + f' Последний id = {__init__.last_answered_msg_id}')

# __Штатная работа__
# Последующие новые сообщения обрабатываем с помощью лонгполла
print('Начинаю получать сообщения через лонгполл')
for event in __init__.vk_bot_longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = VkMesasgeService.get_message_by_id(__init__.vk_main_group_api_session, event.message.id)
        print('Получил письмо с id = ' + str(event.message.id))
        process_msg(msg)
        __init__.last_answered_msg_id.set_value(msg['id'])
        print('Обработал письмо с id = ' + str(event.message.id))
        print('Значение id последнего отвеченого сообщения = ' + str(__init__.last_answered_msg_id))
