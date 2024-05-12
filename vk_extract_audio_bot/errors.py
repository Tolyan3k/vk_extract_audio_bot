from .user_messages import (
    VIDEO_CONVERTING,
    VIDEO_HAVE_NO_AUDIO,
    VIDEO_TOO_LONG,
    VIDEOS_NOT_FOUND,
)


class VkExtractAudioBotError(Exception):

    def __init__(
        self, *args: object, user_message: str | None = None,
    ) -> None:
        super().__init__(*args)
        self.user_message = user_message


class VideoTooLongError(VkExtractAudioBotError):

    def __init__(
        self,
        *args: object,
        user_message: str | None = VIDEO_TOO_LONG,
    ) -> None:
        super().__init__(
            *args, user_message=user_message,
        )


class VideoIsConvertingError(VkExtractAudioBotError):

    def __init__(
        self,
        *args: object,
        user_message: str | None = VIDEO_CONVERTING,
    ) -> None:
        super().__init__(
            *args, user_message=user_message,
        )


class VideoActuallyIsNotVideoError(VkExtractAudioBotError):

    def __init__(
        self,
        *args: object,
        user_message: str | None = VIDEOS_NOT_FOUND,
    ) -> None:
        super().__init__(
            *args, user_message=user_message,
        )


class VideoHaveNoAudioError(VkExtractAudioBotError):

    def __init__(
        self,
        *args: object,
        user_message: str | None = VIDEO_HAVE_NO_AUDIO,
    ) -> None:
        super().__init__(
            *args, user_message=user_message,
        )


__all__ = [
    "VkExtractAudioBotError", "VideoTooLongError", "VideoIsConvertingError",
    "VideoActuallyIsNotVideoError",
]
