from collections.abc import (
    AsyncGenerator,
)

from loguru import logger
from vkwave.types.objects import (
    MessagesForeignMessage,
    MessagesMessage,
    MessagesMessageAttachment,
    MessagesMessageAttachmentType,
    VideoVideoFull,
)


async def attachments_iter(
    message: MessagesMessage,
    attachment_types: list[MessagesMessageAttachmentType],
) -> AsyncGenerator[MessagesMessageAttachment]:
    messages: list[MessagesMessage | MessagesForeignMessage] = [message]
    while messages:
        msg = messages.pop(0)
        messages.extend(msg.fwd_messages)
        for attachment in filter(lambda a: a.type in attachment_types,
                                 msg.attachments,
                                 ):
            yield attachment


async def videos_iter(
    message: MessagesMessage,
) -> AsyncGenerator[VideoVideoFull]:
    video_attachments_gen = attachments_iter(
        message, [MessagesMessageAttachmentType.VIDEO],
    )
    async for video_attachment in video_attachments_gen:
        yield video_attachment.video


def get_video_attachments_from_message(
    vk_msg: dict,
) -> list:
    videos = []

    def _iter_find_video(
        vk_msg: dict,
    ) -> None:
        if not isinstance(vk_msg, dict):
            return
        for key in vk_msg:
            if key == "video":
                videos.append(vk_msg[key])
            elif isinstance(vk_msg[key], dict):
                _iter_find_video(vk_msg[key])
            elif isinstance(vk_msg[key], list):
                for list_elem in vk_msg[key]:
                    _iter_find_video(list_elem)

    _iter_find_video(vk_msg)

    try:
        return videos
    finally:
        logger.success("")
