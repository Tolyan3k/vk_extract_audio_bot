from pathlib import Path

from loguru import logger
from vkwave.bots import (
    SimpleLongPollBot,
)

from vk_extract_audio_bot import db
from vk_extract_audio_bot.routers import (
    DIRECT_ROUTER,
)
from vk_extract_audio_bot.settings import (
    CONFIG,
)


ROUTERS = [DIRECT_ROUTER]

logger.info("Инициализация рабочих директорий")
for bot_dir in CONFIG.BOT_WORK_DIRS.values():
    Path(bot_dir).mkdir(exist_ok=True, parents=True)

logger.info("Инициализация бота и роутеров")
bot = SimpleLongPollBot(
    tokens=[CONFIG.VK_MAIN_GROUP_TOKEN],
    group_id=CONFIG.VK_MAIN_GROUP_ID,
)
for router in ROUTERS:
    bot.dispatcher.add_router(router)

logger.info("Инициализация БД")
db.init_db()

logger.info("Запуск бота")
bot.run_forever()
