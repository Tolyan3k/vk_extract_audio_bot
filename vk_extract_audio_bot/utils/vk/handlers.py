from vkwave.bots import SimpleBotEvent

from vk_extract_audio_bot.errors import (
    VkExtractAudioBotError,
)
from vk_extract_audio_bot.settings import (
    CONSTANTS,
)


class ReplyMessageHandler:

    def __init__(
        self, event: SimpleBotEvent, cmid: int | None = None,
    ) -> None:
        self._event = event
        self._cmid = cmid
        self._message = None
        self._attachments = []

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, new_message: str) -> None:
        self._message = new_message

    @property
    def attachments(self) -> list[str]:
        return self._attachments

    @attachments.setter
    def attachments(self, new_attachments: list[str]) -> None:
        if len(new_attachments) > CONSTANTS.VK_MAX_ATTACHMENTS:
            error_msg = (
                "Can't add more than"
                f" {CONSTANTS.VK_MAX_ATTACHMENTS} attachments."
            )
            raise VkExtractAudioBotError(error_msg)
        self._attachments = new_attachments

    async def commit(self) -> None:
        if not self._message and len(self._attachments) == 0:
            error_msg = "Message is empty. Nothing to reply."
            raise VkExtractAudioBotError(error_msg)
        if not self._cmid:
            msg_resp = await self._event.reply(
                message=self._message, attachment=",".join(self._attachments),
            )
            self._cmid = msg_resp.response
        else:
            await self._event.edit(
                message=self._message,
                attachment=",".join(self._attachments),
                message_id=self._cmid,
                keep_forward_messages=True,
            )

    def empty(self) -> bool:
        return not self._message and not self._attachments


class MessageEventHandler:
    # pylint: disable=R0903
    def __init__(self, event: SimpleBotEvent) -> None:
        self._event = event

    def create_reply_handler(
        self,
    ) -> ReplyMessageHandler:
        return ReplyMessageHandler(self._event)
