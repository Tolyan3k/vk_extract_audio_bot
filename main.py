"""TODO."""

import contextlib
import queue
import secrets
import threading
from pathlib import Path
from time import sleep

from loguru import logger
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotEventType

import __init__
import user_messages
from bot_types.audio_convert_settings import AudioConvertSettings
from bot_types.audio_info import AudioInfo
from bot_types.video_download_settings import VideoDownloadSettings
from bot_types.vk_video_platform import VkVideoPlatform
from config import (
    AUDIO_MIN_DURATION,
    BOT_WORK_DIRS,
    VIDEO_MAX_DURATION,
    VIDEO_MIN_DURATION,
    VK_ARCHIVE_GROUP_ID,
    VK_MAIN_GROUP_ID,
    VK_MAIN_GROUP_URL,
    VK_MAX_ATTACHMENTS,
)
from services.converter_service import ConverterService
from services.video_service import VideoService
from services.vk_audio_service import VkAudioService
from services.vk_message_service import VkMesasgeService

GROUP_CHAT_START_ID = 2000000000
MSG_PROCCESSING_START_DELAY = 5

unprocessed_msgs_queue = queue.Queue()
processing_queue = queue.Queue()


def is_converted_vk_video(vk_video_content_id: str) -> bool:
    """TODO.

    Args:
    ----
        vk_video_content_id (str): _description_

    Returns:
    -------
        bool: _description_

    """
    db = __init__.converted_videos_content_id_to_audio_content_id.get_value()

    return dict(db).get(vk_video_content_id) is not None


def process_converted_vk_video(video_content_id: str) -> str | None:
    """TODO.

    Args:
    ----
        video_content_id (str): _description_

    Returns:
    -------
        Optional[str]: _description_

    """
    db = __init__.converted_videos_content_id_to_audio_content_id.get_value()
    return dict(db)[video_content_id]


def process_non_converted_vk_video(
    video_content_id: str,
    vk_video_obj: dict,
    video_file_name: str,
) -> str | None:
    """TODO.

    Args:
    ----
        video_content_id (str): _description_
        vk_video_obj (dict): _description_
        video_file_name (str): _description_

    Returns:
    -------
        Optional[str]: _description_

    """
    response = __init__.vk_audio_api.method(
        "video.get",
        owner_id=vk_video_obj["owner_id"],
        videos=f"{video_content_id}",
    )["response"]

    video = response["items"][0]

    player_link = get_player_link_from_vk_video_obj(video)

    audio_file_name = None
    audio_content_id = None
    try:
        if video.get("platform") == VkVideoPlatform.VK.value:
            video_info = VideoService.get_video_info_from_vk_video(video)
            video_info.author = get_author_name(video_info)
        else:
            video_info = VideoService.get_video_info(player_link)

        video_file_name = VideoService.download_video(
            player_link,
            VideoDownloadSettings(
                VIDEO_MIN_DURATION,
                VIDEO_MAX_DURATION,
                None,
                f"{video_file_name}",
            ),
            video_info,
        )

        if ConverterService.has_audio(video_file_name):
            audio_convert_settings = AudioConvertSettings(AUDIO_MIN_DURATION)
            audio_file_name = ConverterService.convert_video_to_audio(
                video_file_name,
                audio_convert_settings,
            )
            audio_file_path = BOT_WORK_DIRS["audios"] + f"/{audio_file_name}"
            audio_content_id = VkAudioService.upload_audio(
                audio_file_path,
                AudioInfo(
                    artist=video_info.author,
                    title=video_info.title,
                    is_public=video_info.is_public,
                ),
            )
    except Exception as error:
        logger.info(f"Не удалось обработать видео {video_file_name}")
        logger.info(f"Ошибка: {error}")
        return None
    finally:
        Path.unlink(
            BOT_WORK_DIRS["videos"] + f"/{video_file_name}",
            missing_ok=True,
        )
        Path.unlink(
            BOT_WORK_DIRS["audios"] + f"/{audio_file_name}",
            missing_ok=True,
        )

    archive_group_content_id = None
    try:
        archive_group_content_id = VkAudioService.add_audio(
            audio_content_id,
            VK_ARCHIVE_GROUP_ID,
        )
        if archive_group_content_id:
            archive_group_content_id = (
                "-" + VK_ARCHIVE_GROUP_ID + "_" + str(archive_group_content_id)
            )
    except Exception:
        with contextlib.suppress(Exception):
            VkAudioService.delete_audio(audio_content_id)
    return archive_group_content_id


def get_author_name(video_info: object) -> str:
    """TODO.

    Args:
    ----
        video_info (_type_): _description_

    Returns:
    -------
        _type_: _description_

    """
    author = "Неизвестен (временно)"

    session_api = __init__.vk_archive_group_api_session.get_api()
    try:
        if video_info.author < 0:
            group_objs = session_api.groups.getById(
                group_ids=f"{-video_info.author}",
            )
            group_obj = group_objs[0]
            author = group_obj["name"]
        elif video_info.author > 0:
            user_objs = session_api.users.get(user_ids=f"{video_info.author}")
            user_obj = user_objs[0]
            author = user_obj["first_name"] + " " + user_obj["last_name"]
    except Exception as error:
        logger.info("Во время поиска автора произошла ошибка")
        logger.info(error)

    return author


def get_player_link_from_vk_video_obj(video: dict) -> str:
    """TODO.

    Args:
    ----
        video (_type_): _description_

    Returns:
    -------
        _type_: _description_

    """
    if video.get("platform") == VkVideoPlatform.VK.value:
        for key in dict(video["files"]):
            if "hls" in key:
                player_link = video["files"][key]
                break
    elif video.get("platform") == VkVideoPlatform.YOUTUBE.value:
        player_link = video["player"]
    return player_link


def process_vk_video(
    vk_video_obj: dict,
    video_file_name: str,
) -> tuple[str | None,
           bool]:
    """TODO.

    Args:
    ----
        vk_video_obj (dict): _description_
        video_file_name (str): _description_

    Returns:
    -------
        tuple[Optional[str], bool]: _description_

    """
    video = vk_video_obj

    if (video.get("converting") or video.get("duration") is None
            or video.get("duration") > VIDEO_MAX_DURATION):
        return None

    video_id = str(video["owner_id"]) + "_" + str(video["id"])

    if is_converted_vk_video(video_id):
        logger.info(f"Нашёл ранее сконвертированное аудио для видео {video_id}")
        return process_converted_vk_video(video_id), False

    logger.info(f"Начинаю обработку видео {video_id}")

    if video.get("access_key"):
        video_id += "_" + str(video["access_key"])

    archive_group_content_id = process_non_converted_vk_video(
        video_id,
        vk_video_obj,
        video_file_name,
    )

    if archive_group_content_id:
        db = __init__.converted_videos_content_id_to_audio_content_id.get_value(
        )
        db = dict(db)

        video_id = video_id.split("_")
        video_id = "_".join([video_id[0], video_id[1]])
        db.setdefault(video_id, archive_group_content_id)

        __init__.converted_videos_content_id_to_audio_content_id.set_value(db)

        logger.info("Добавил content_id сконвертированного аудио в базу данных")

    return archive_group_content_id, True


def send_replied_msg_else_not(vk_session: VkApi, **send_msg_args) -> dict:
    # ruff: noqa: ANN003
    """TODO.

    Args:
    ----
        vk_session (VkApi): _description_
        send_msg_args: _description_

    Returns:
    -------
        dict: _description_

    """
    try:
        return vk_session.method("messages.send", send_msg_args)
    except Exception:
        if send_msg_args.get("reply_to"):
            send_msg_args.pop("reply_to")

        return vk_session.method("messages.send", send_msg_args)


def send_audios_to_user(
    msg: dict,
    videos: list[dict],
    vk_audio_content_ids: list[str],
) -> None:
    """TODO.

    Args:
    ----
        msg (dict): _description_
        videos (list[dict]): _description_
        vk_audio_content_ids (list[str]): _description_

    """
    error_msg_text = ""
    if len(videos) == 1 and len(vk_audio_content_ids) == 0:
        error_msg_text = user_messages.video_not_support()
    elif len(videos) > 1:
        if len(vk_audio_content_ids) and len(videos,
                                             ) - len(vk_audio_content_ids):
            error_msg_text = user_messages.failed_to_convert_part_many()
        elif len(vk_audio_content_ids) == 0:
            error_msg_text = user_messages.failed_to_convert_all_many()

    parts = (
        len(vk_audio_content_ids) + (VK_MAX_ATTACHMENTS - 1)
    ) // VK_MAX_ATTACHMENTS
    for part in range(parts):
        real_magic_num = 2    # переименую чуть позже, надо понять, для чего это
        message = f"[{part + 1}/{parts}]" if parts >= real_magic_num else error_msg_text
        audio_start_index = VK_MAX_ATTACHMENTS * part
        audio_end_index = min(
            VK_MAX_ATTACHMENTS * (part + 1),
            len(vk_audio_content_ids),
        )

        send_replied_msg_else_not(
            __init__.vk_main_group_api_session,
            message=message,
            reply_to=msg["id"],
            attachment="audio" + ",audio".join(
                vk_audio_content_ids[audio_start_index:audio_end_index],
            ),
            user_id=msg["peer_id"],
            random_id=secrets.randbelow(1 << 31),
        )

    if error_msg_text and (len(vk_audio_content_ids) > VK_MAX_ATTACHMENTS
                           or parts == 0):
        send_replied_msg_else_not(
            __init__.vk_main_group_api_session,
            message=error_msg_text,
            reply_to=msg["id"],
            user_id=msg["peer_id"],
            random_id=secrets.randbelow(1 << 31),
        )


def need_process_msg(msg: dict | None) -> bool:
    """TODO.

    Args:
    ----
        msg (_type_): _description_

    Returns:
    -------
        _type_: _description_

    """
    if (msg is None or msg["from_id"] == -int(VK_MAIN_GROUP_ID)
            or msg["peer_id"] >= GROUP_CHAT_START_ID):
        return False
    return True


def process_msg(msg: dict | None) -> None:
    """TODO.

    Args:
    ----
        msg (_type_): _description_

    """
    if not need_process_msg(msg):
        return

    video_attachments = VkMesasgeService.get_video_attachments_from_message(msg)

    videos = video_attachments

    if len(videos) == 0:
        send_replied_msg_else_not(
            __init__.vk_main_group_api_session,
            message=user_messages.videos_not_found(),
            reply_to=msg["id"],
            user_id=msg["peer_id"],
            random_id=secrets.randbelow(1 << 31),
        )
        return

    send_replied_msg_else_not(
        __init__.vk_main_group_api_session,
        message=user_messages.start_processing_message(),
        reply_to=msg["id"],
        user_id=msg["peer_id"],
        random_id=secrets.randbelow(1 << 31),
    )

    vk_audio_content_ids = []
    for video_id, video in enumerate(videos):
        try:
            archive_group_content_id, new_video = process_vk_video(
                video,
                f"{msg['id']}_{video_id}",
            )
        except Exception as error:
            logger.info(
                f"Во время обработки видео {video} произошла ошибка.",
            )
            logger.info(error)
            archive_group_content_id = None

        if archive_group_content_id:
            vk_audio_content_ids.append(str(archive_group_content_id))
            edit_vk_audio_if_video_public_or_non_vk(
                videos,
                video_id,
                archive_group_content_id,
                new_video,
            )

    send_audios_to_user(msg, videos, vk_audio_content_ids)


def edit_vk_audio_if_video_public_or_non_vk(
    videos: list[dict],
    video_id: str,
    archive_group_content_id: int,
    is_new_video: bool,
) -> None:
    """TODO.

    Args:
    ----
        videos (_type_): _description_
        video_id (_type_): _description_
        archive_group_content_id (_type_): _description_
        is_new_video (_type_): _description_

    """
    is_video_public = videos[video_id].get("is_private") is None
    is_platform_vk = videos[video_id].get("platform") is None

    if is_new_video and (is_video_public or not is_platform_vk):
        VkAudioService.edit_audio(
            archive_group_content_id,
            new_text=VK_MAIN_GROUP_URL,
            search_visibility=True,
        )


def process_msg_new(msg_id: str) -> None:
    """TODO.

    Args:
    ----
        msg_id (_type_): _description_

    """
    logger.info("Получил письмо с id = " + str(msg_id))
    msg = VkMesasgeService.get_message_by_id(
        __init__.vk_main_group_api_session,
        msg_id,
    )

    try:
        process_msg(msg)
    except Exception:
        __init__.error_message_ids += [msg_id]
        logger.info(
            f"Не удалось обработать сообщение с id = {msg_id}. Перехожу к следующему сообщению.",
        )

    __init__.last_answered_msg_id.set_value(msg_id)
    logger.info("Обработал письмо с id = " + str(msg_id))


def get_last_unanswered_msg_id(vk_session: VkApi) -> int:
    """TODO.

    Args:
    ----
        vk_session (VkApi): _description_

    Returns:
    -------
        _type_: _description_

    """
    return vk_session.get_api().messages.getConversations(
        count=1,
    )["items"][0]["last_message"]["id"]


def process_unanswered_messages() -> None:
    """TODO."""
    logger.info(
        "Начинаю проверять неотвеченные сообщения."
        " Текущий id последнего отвеченного сообщения"
        f" = {__init__.last_answered_msg_id}",
    )

    last_unanswered_msg_id = get_last_unanswered_msg_id(
        __init__.vk_main_group_api_session,
    )
    for msg_id in range(
            int(str(__init__.last_answered_msg_id)) + 1,
            last_unanswered_msg_id + 1,
    ):
        send_msg_if_queued(msg_id)
        unprocessed_msgs_queue.put(msg_id)

    logger.info(
        "Закончил проверять неотвеченные сообщения."
        f" Id последнего отвеченного сообщения = {__init__.last_answered_msg_id}",
    )


def get_right_messages_word(num: int) -> str:
    """TODO.

    Args:
    ----
        num (_type_): _description_

    Returns:
    -------
        _type_: _description_

    """
    word = ""

    if num % 10 == 1:
        word = "сообщение"
    elif num % 10 in range(2, 4 + 1):
        word = "сообщения"
    elif num % 10 in range(5, 9 + 1):
        word = "сообщений"

    return word


def send_msg_if_queued(msg_id: str, msg_peer_id: int | None = None) -> None:
    """TODO.

    Args:
    ----
        msg_id (_type_): _description_
        msg_peer_id (_type_, optional): _description_. Defaults to None.

    """
    msg = VkMesasgeService.get_message_by_id(
        __init__.vk_main_group_api_session,
        msg_id,
    )
    if not need_process_msg(msg):
        return

    msg_peer_id = msg["peer_id"]

    count = unprocessed_msgs_queue.qsize()
    # Странная строчка - не помню, зачем её написал
    count += (
        1 if processing_queue.qsize() else 0
    )    # 1 if not processing_queue.qsize() else 0

    if count:
        send_replied_msg_else_not(
            __init__.vk_main_group_api_session,
            message=" ".join(
                [
                    "Отправил сообщение в очередь ожидания.",
                    "Очередь перед этим сообщением:",
                    f"{count} {get_right_messages_word(count)}.",
                ],
            ),
            reply_to=msg_id,
            user_id=msg_peer_id,
            random_id=secrets.randbelow(1 << 31),
        )


def process_longpoll() -> None:
    """TODO."""
    logger.info("Начинаю получать сообщения через лонгполл")

    for event in __init__.vk_bot_longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            msg_id = event.message.id
            msg_peer_id = event.message.peer_id
            # Чтобы вложение успело прогрузиться, если пользователь пришлёт только ссылку
            sleep(MSG_PROCCESSING_START_DELAY)
            send_msg_if_queued(msg_id, msg_peer_id)
            unprocessed_msgs_queue.put(msg_id)


def convert_processor() -> None:
    """TODO."""
    while True:
        msg_id = unprocessed_msgs_queue.get()
        processing_queue.put(msg_id)
        process_msg_new(msg_id)
        processing_queue.get()


def run_longpoll() -> None:
    """TODO."""
    try:
        logger.info("Запуск бота...")
        process_longpoll()
    except Exception:
        logger.info(
            "\n" * 2 + "#" * 30 + "\n" * 2 + "Произошла непредвиденная ошибка.",
        )
        logger.info("\n" * 2 + "#" * 30 + "\n")
        logger.info("Перезапуск бота..." + "\n")


def main_bot() -> None:
    """TODO."""
    while True:
        run_longpoll()


functions_to_threads = [convert_processor, main_bot]
threads = []

for function in functions_to_threads:
    thread = threading.Thread(target=function)
    thread.start()
    threads.append(thread)
