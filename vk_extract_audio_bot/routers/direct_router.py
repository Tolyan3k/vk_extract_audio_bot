from loguru import logger
from vkwave.bots import (
    DefaultRouter,
    MessageFromConversationTypeFilter,
    SimpleBotEvent,
    simple_bot_message_handler,
)

from vk_extract_audio_bot.user_messages import (
    CONVERT_UNDEFINED_ERROR,
)

from ._utils import (
    extract_audio_handler,
)


DIRECT_ROUTER = DefaultRouter()


@simple_bot_message_handler(
    DIRECT_ROUTER,
    MessageFromConversationTypeFilter("from_direct"),
)
async def extract_audio(
    event: SimpleBotEvent,
) -> None:
    try:
        logger.info(f"Получил сообщение c id: {event.object.object.message.id}")
        async for user_response in extract_audio_handler(event):
            await user_response.commit()
        logger.info(
            f"Обработал сообщение c id: {event.object.object.message.id}",
        )
    # pylint: disable=W0718
    except Exception:
        event.reply(
            message=CONVERT_UNDEFINED_ERROR,
        )
