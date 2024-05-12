import pydantic
from vkwave.types.objects import (
    AudioAudio,
    BaseBoolInt,
)


class AudioUploadResponseAds(pydantic.BaseModel):
    content_id: str
    duration: pydantic.PositiveInt
    account_age_type: pydantic.PositiveInt


class AudioUploadResponse(AudioAudio):
    ads: AudioUploadResponseAds
    is_explicit: bool
    is_licensed: bool
    short_videos_allowed: bool
    stories_allowed: bool
    stories_cover_allowed: bool


class AudioAddResponse(pydantic.BaseModel):
    response: pydantic.NonNegativeInt = pydantic.Field(
        alias="response",
        description=(
            "ID добавленной аудиозаписи"
            " или 0, если произошла"
            " ошибка при добавлении"
        ),
    )
    """
    ID добавленной аудиозаписи или 0,
    если произошла ошибка при добавлении
    """


class AudioDeleteResponse(pydantic.BaseModel):
    response: BaseBoolInt = pydantic.Field(
        alias="response",
        description="Результат удаления аудиозаписи. В среднем всегда 1",
    )
    """
    Результат удаления аудиозаписи.
    В среднем всегда 1
    """


class AudioEditResponse(pydantic.BaseModel):
    response: pydantic.NonNegativeInt = pydantic.Field(
        alias="response",
        description=(
            "If lyrics were entered by"
            " the user, returns"
            " `lyrics_id`. Otherwise,"
            " returns 0."
        ),
    )
    """
    If lyrics were entered by the user, returns `lyrics_id`.
    Otherwise, returns 0.
    """
