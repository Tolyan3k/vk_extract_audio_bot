import asyncio
import contextlib
from asyncio import Semaphore, sleep
from collections.abc import (
    AsyncGenerator,
)
from itertools import batched
from pathlib import Path

from loguru import logger
from vk_api import VkApiError
from vkwave.bots import SimpleBotEvent

from vk_extract_audio_bot.data_types import (
    AudioConvertSettings,
    VideoDownloadSettings,
    VkVideoPlatform,
)
from vk_extract_audio_bot.db import (
    models,
)
from vk_extract_audio_bot.db.service import (
    Audios,
    Videos,
)
from vk_extract_audio_bot.errors import (
    VideoActuallyIsNotVideoError,
    VideoIsConvertingError,
    VideoTooLongError,
    VkExtractAudioBotError,
)
from vk_extract_audio_bot.settings import (
    CONFIG,
    CONSTANTS,
)
from vk_extract_audio_bot.user_messages import (
    CONVERT_MANY_ALL_FAILED,
    CONVERT_MANY_ALL_SUCCESS,
    CONVERT_MANY_PART_SUCCESS,
    CONVERT_ONE_SUCCESS,
    PROCESSING_START,
    PROCESSING_START_SOON,
    QUEUE_CHECK,
    VIDEO_NOT_SUPPORT,
    VIDEOS_NOT_FOUND,
    queue_current_position,
)
from vk_extract_audio_bot.utils import (
    MessageQueue,
    Video,
    VideoConverter,
)
from vk_extract_audio_bot.utils.vk.handlers import (
    MessageEventHandler,
    ReplyMessageHandler,
)
from vk_extract_audio_bot.utils.vk.utils import (
    get_video_attachments_from_message,
)
from vk_extract_audio_bot.vk_apis import (
    vk_android_api,
    vk_archive_group_api,
    vk_audio_api,
)


MSG_QUEUE = MessageQueue()
WORKERS_SEMAPHORE = Semaphore(CONFIG.WORKER_COUNT)


async def process_vk_video(
    vk_video_obj: dict,
    video_file_name: str,
) -> models.Audio | None:
    video = vk_video_obj

    if video.get("converting"):
        raise VideoIsConvertingError
    if video.get("duration") is None:
        raise VideoActuallyIsNotVideoError
    if video["duration"] > CONFIG.VIDEO_MAX_DURATION:
        raise VideoTooLongError

    find_video = Videos.find_with(video["owner_id"], video["id"])
    if find_video:
        logger.info(f"Нашёл ранее попадавшееся видео {find_video}")
        return Videos.find_audio(find_video.id)

    video_content_id = str(video["owner_id"]) + "_" + str(video["id"])
    logger.info(f"Начинаю обработку видео {video_content_id}")

    if video.get("access_key"):
        video_content_id += "_" + str(video["access_key"])

    audio_db = await process_non_converted_vk_video(
        video_content_id,
        vk_video_obj,
        video_file_name,
    )

    if audio_db:
        video_create = models.VideoCreate(
            owner_id=video["owner_id"], video_id=video["id"],
        )
        video_db = Videos.create(video_create)
        Videos.set_audio(video_db.id, audio_db.id)
        logger.info(f"Добавил аудиозапись {audio_db} в базу данных")

    try:
        return audio_db
    finally:
        logger.success(f"Видео {video} обработано")


async def process_non_converted_vk_video(
    video_content_id: str,
    vk_video_obj: dict,
    video_file_name: str,
) -> models.Audio | None:
    response = vk_android_api.method(
        "video.get",
        owner_id=vk_video_obj["owner_id"],
        videos=f"{video_content_id}",
    )["response"]

    video: dict = response["items"][0]

    player_link = get_player_link_from_vk_video_obj(video)

    audio_file_name = None
    vk_audio = None
    try:
        if video.get("platform") == VkVideoPlatform.VK.value:
            video_info = Video.get_info_from_vk_video(video)
            video_info.author = get_author_name(video_info)
        else:
            video_info = Video.get_info(player_link)

        video_file_name = await asyncio.get_event_loop().run_in_executor(
            None,
            Video.download,
            player_link,
            VideoDownloadSettings(
                min_duration=CONFIG.VIDEO_MIN_DURATION,
                max_duration=CONFIG.VIDEO_MAX_DURATION,
                max_size=None,
                file_name=f"{video_file_name}",
            ),
            video_info,
        )

        if VideoConverter.has_audio(video_file_name):
            audio_convert_settings = AudioConvertSettings(
                CONSTANTS.VK_AUDIO_MIN_DURATION,
            )
            audio_file_name = await asyncio.get_event_loop().run_in_executor(
                None,
                VideoConverter.convert_video_to_audio,
                video_file_name,
                audio_convert_settings,
            )
            audio_file_path = (
                CONFIG.BOT_WORK_DIRS["audios"] + f"/{audio_file_name}"
            )
            vk_audio = vk_audio_api.upload(
                audio_file_path,
                video_info.author,
                video_info.title,
            )
    # pylint: disable=W0718
    except Exception as error:
        logger.info(f"Не удалось обработать видео {video_file_name}")
        logger.error(str(error))
        return None
    finally:
        Path.unlink(
            Path(CONFIG.BOT_WORK_DIRS["videos"] + f"/{video_file_name}"),
            missing_ok=True,
        )
        Path.unlink(
            Path(CONFIG.BOT_WORK_DIRS["audios"] + f"/{audio_file_name}"),
            missing_ok=True,
        )

    archive_group_audio_id = None
    audio_create: models.AudioCreate = None
    audio_db: models.Audio = None
    with contextlib.suppress(Exception):
        archive_group_audio_id = vk_audio_api.add(
            vk_audio.owner_id,
            vk_audio.id,
            CONFIG.VK_ARCHIVE_GROUP_ID,
        ).response
        logger.info(f"Добавил аудио {audio_file_name} в группу")
        if archive_group_audio_id:
            audio_create = models.AudioCreate(
                owner_id=-1 * CONFIG.VK_ARCHIVE_GROUP_ID,
                audio_id=archive_group_audio_id,
            )
            audio_db = Audios.create(audio_create)
            logger.info(
                f"Добавил запись об аудио {audio_file_name} в БД: {audio_db}",
            )
    vk_audio_api.delete(
        vk_audio.owner_id,
        vk_audio.id,
    )
    return audio_db


def get_player_link_from_vk_video_obj(
    video: dict,
) -> str:
    try:
        if "hls" in video["files"] and ".mycdn.me" in video["files"]["hls"]:
            return video["files"]["hls"]
        return video["player"]
    finally:
        logger.debug(video)


def get_author_name(
    video_info: object,
) -> str:
    author = "Неизвестен (временно)"

    session_api = vk_archive_group_api.get_api()
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
    except VkApiError as error:
        logger.error(f"Во время поиска автора произошла ошибка: {error}")

    return author


def edit_vk_audio_if_video_public_or_non_vk(
    video: dict,
    audio_owner_id: int,
    audio_id: int,
) -> None:
    is_video_public = video.get("is_private") is None
    is_platform_vk = video.get("platform") is None

    if is_video_public or not is_platform_vk:
        vk_audio_api.edit(
            audio_owner_id,
            audio_id,
            text=CONFIG.VK_MAIN_GROUP_URL,
            no_search=True,
        )
    logger.success("")


async def send_audios(
    event_hdr: MessageEventHandler,
    reply_msg_hdr: ReplyMessageHandler,
    videos: list[dict],
    vk_audios: list[models.Audio],
) -> AsyncGenerator[ReplyMessageHandler, None, None]:
    logger.info(
        "Приступаю к отправке"
        " аудиозаписей: кол-во видео:"
        f" {len(videos)}, кол-во"
        " аудиозаписей:"
        f" {len(vk_audios)}",
    )
    if len(videos) == 1:
        if len(vk_audios) == 0:
            reply_msg_hdr.message = VIDEO_NOT_SUPPORT
            yield reply_msg_hdr
            return
        vk_audio = vk_audios.pop()
        reply_msg_hdr.message = CONVERT_ONE_SUCCESS
        reply_msg_hdr.attachments = [
            f"audio{vk_audio.owner_id}_{vk_audio.audio_id}",
        ]
        yield reply_msg_hdr
    else:
        batches: list[list[models.Audio]] = list(
            batched(
                vk_audios,
                CONSTANTS.VK_MAX_ATTACHMENTS,
            ),
        )
        if len(batches) == 1:
            reply_msg_hdr.attachments = [
                f"audio{a.owner_id}_{a.audio_id}" for a in batches[0]
            ]
        else:
            for (batch_num, batch,
                 ) in enumerate(batches, 1):
                reply_msg_hdr.message = f"[{batch_num}/{len(batches)}]"
                reply_msg_hdr.attachments = [
                    f"audio{a.owner_id}_{a.audio_id}" for a in batch
                ]
                yield reply_msg_hdr
                reply_msg_hdr = event_hdr.create_reply_handler()

        if len(vk_audios) and len(vk_audios) < len(videos):
            reply_msg_hdr.message = CONVERT_MANY_PART_SUCCESS
        elif len(vk_audios) == 0:
            reply_msg_hdr.message = CONVERT_MANY_ALL_FAILED
        else:
            reply_msg_hdr.message = CONVERT_MANY_ALL_SUCCESS
        yield reply_msg_hdr
    logger.info("Завершил отправку аудизаписей")


async def extract_audio_handler(
    event: SimpleBotEvent,
) -> AsyncGenerator[ReplyMessageHandler, None, None]:
    # pylint: disable=R0914
    # "Отправка" сообщения в очередь
    event_hdr = MessageEventHandler(event)
    reply_msg_hdr = event_hdr.create_reply_handler()
    reply_msg_hdr.message = QUEUE_CHECK
    yield reply_msg_hdr
    work_start_delay_timer = asyncio.create_task(
        sleep(CONFIG.MSG_PROCCESSING_DELAY),
    )
    msg_id = event.object.object.message.id
    await MSG_QUEUE.put(msg_id)
    async for position in MSG_QUEUE.listen_positions(msg_id):
        reply_msg_hdr.message = queue_current_position(position)
        yield reply_msg_hdr
    reply_msg_hdr.message = PROCESSING_START_SOON
    yield reply_msg_hdr

    async with WORKERS_SEMAPHORE:
        await work_start_delay_timer
        await MSG_QUEUE.pop()
        msg_resp_raw = await event.api_ctx.messages.get_by_id(
            message_ids=[msg_id], return_raw_response=True,
        )
        msg = msg_resp_raw["response"]["items"][0]
        videos = get_video_attachments_from_message(msg)
        if len(videos) == 0:
            reply_msg_hdr.message = VIDEOS_NOT_FOUND
            yield reply_msg_hdr
            return

        reply_msg_hdr.message = PROCESSING_START
        yield reply_msg_hdr

        vk_audios: list[models.Audio] = []
        audio_db: models.Audio = None
        for video_id, video in enumerate(videos):
            # ruff: noqa: PERF203
            try:
                audio_db = await process_vk_video(
                    video,
                    f"{msg['id']}_{video_id}",
                )
                if audio_db:
                    vk_audios.append(audio_db)
                    if audio_db:
                        edit_vk_audio_if_video_public_or_non_vk(
                            video,
                            audio_db.owner_id,
                            audio_db.audio_id,
                        )
            except VkExtractAudioBotError as bot_error:
                logger.error(str(bot_error))
            # pylint: disable=W0718
            except Exception as error:
                logger.info(
                    "Во время"
                    " обработки видео"
                    f" {video} произошла"
                    f" ошибка: {error}",
                )
    # Отправка аудиозаписей пользователю
    async for user_response in send_audios(event_hdr, reply_msg_hdr, videos,
                                           vk_audios):
        yield user_response
