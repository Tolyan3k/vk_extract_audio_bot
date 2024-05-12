# ruff: noqa: ERA001
# fmt: off
# yapf: disable

from pydantic import NonNegativeInt, validate_call

from .settings import CONFIG


QUEUE_CHECK = (
    "👀Проверяю очередь сообщений👀"
)

QUEUE_PUSH = ""

PROCESSING_START_SOON = (
    "⌛Обработка скоро начнётся⌛"
)

PROCESSING_START = (
    "⚙️Начинаю обработку⚙️"
)

CONVERT_UNDEFINED_ERROR = (
    "⚠️Во время конвертации видео произошла непредвиденная ошибка⚠️"
)

VIDEOS_NOT_FOUND = (
    r"Не нашёл вложений с видео[¯\_(ツ)_/¯]"
)

VIDEO_NOT_SUPPORT = "❌Не удалось извлечь аудио❌"

VIDEO_CONVERTING = "🐢ВК не успел обработать видео, попробуйте позже ещё раз🐢"

VIDEO_TOO_LONG = (
    f"⏱️Видео слишком длинное (>{int(CONFIG.VIDEO_MAX_DURATION / 60)} минут)⏱️"
)

VIDEO_HAVE_NO_AUDIO = (
    "🔇Видео не содержит аудио🔇"
)

CONVERT_MANY_PART_SUCCESS = (
    "😜Удалось извлечь аудио только из некоторых видео😜"
)

CONVERT_MANY_ALL_SUCCESS = "✅Все аудио извлечены✅"

CONVERT_ONE_SUCCESS = "✅Аудио извлечено✅"

CONVERT_MANY_ALL_FAILED = (
    "😔Не получилось извлечь аудио ни из одного видео😔"
)


@validate_call
def queue_current_position(position: NonNegativeInt) -> str:
    return (
        "🗃️Отправил в очередь🗃️"
        f"\nТекущая позиция: {position}."
    )
