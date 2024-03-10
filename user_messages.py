"""TODO
"""

import config


def start_processing_message() -> str:
    """TODO

    Returns
    -------
        str: _description_

    """
    return "Начинаю обработку сообщения..."


def undefined_convert_error() -> str:
    """TODO

    Returns
    -------
        str: _description_

    """
    return "Произошла непредвиденная ошибка во время конвертации сообщения."


def videos_not_found() -> str:
    """TODO

    Returns
    -------
        str: _description_

    """
    return "Не удалось найти видео в сообщении"


def video_not_support() -> str:
    """TODO

    Returns
    -------
        str: _description_

    """
    return " ".join(
        [
            "К сожалению, данное видео не поддерживается ботом.",
            "Или возможно, что оно не содержит аудио.",
        ]
    )
    # return "К сожалению, данное видео не поддерживается ботом.\n" \
    #         + "Возможно, видео слишком длинное, либо его платформа не поддерживается.\n" \
    #         + "Также возможно, что музыка из этого видео блокируется правообладателями("


def failed_to_convert_part_many() -> str:
    """TODO

    Returns
    -------
        str: _description_

    """
    return (
        "К сожалению, часть видео не удалось сконвертировать.\n" +
        "Возможно, некоторые видео слишком длинные (> " +
        str(config.VIDEO_MAX_DURATION / 60) +
        " минут), либо их платформа не поддерживается."
    )


def failed_to_convert_all_many() -> str:
    """TODO

    Returns
    -------
        str: _description_

    """
    msg = "К сожалению, боту не удалось сконвертировать в аудио ни одно видео.\n"
    msg += " ".join(
        [
            "Это может быть связяно с тем, что платформы этих видео сейчас",
            "не поддерживаются ботом, либо видео длиннее",
            str(config.VIDEO_MAX_DURATION / 60),
            "минут.",
        ]
    )
    return msg
