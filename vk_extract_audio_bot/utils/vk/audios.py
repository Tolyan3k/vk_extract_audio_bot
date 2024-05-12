from typing import overload

import pydantic
from vk_api import VkApi
from vk_api.upload import VkUpload

from vk_extract_audio_bot.utils.vk.android import (
    VkAndroidApi,
)
from vk_extract_audio_bot.utils.vk.responses import (
    AudioAddResponse,
    AudioDeleteResponse,
    AudioEditResponse,
    AudioUploadResponse,
)

from ._utils import get_method_params


class VkAudios:

    def __init__(
        self,
        vk_android_api_session: VkAndroidApi,
        vk_api_session: VkApi,
    ) -> None:
        self._vk_audio_api = vk_android_api_session
        self._vk_api = vk_api_session

    @pydantic.validate_call
    def upload(
        self,
        filepath: pydantic.FilePath,
        artist: str | None = None,
        title: str | None = None,
    ) -> AudioUploadResponse:
        upload_response = VkUpload(self._vk_api).audio(
            audio=str(filepath), artist=artist, title=title,
        )
        return AudioUploadResponse(**upload_response)

    @pydantic.validate_call
    def delete(
        self,
        owner_id: int,
        audio_id: pydantic.PositiveInt,
    ) -> AudioDeleteResponse:
        # pylint: disable=W0613
        params = get_method_params(locals())
        response = self._vk_audio_api.method(
            "audio.delete",
            **params,
        )
        return AudioDeleteResponse(**response)

    @overload
    def add(
        self,
        owner_id: int,
        audio_id: pydantic.PositiveInt,
    ) -> AudioAddResponse:
        ...

    @overload
    def add(
        self,
        owner_id: int,
        audio_id: pydantic.PositiveInt,
        group_id: pydantic.PositiveInt,
    ) -> AudioAddResponse:
        ...

    @pydantic.validate_call
    def add(
        self,
        owner_id: int,
        audio_id: pydantic.PositiveInt,
        group_id: pydantic.PositiveInt | None = None,
    ) -> AudioAddResponse:
        # pylint: disable=W0613
        params = get_method_params(locals())
        response = self._vk_audio_api.method("audio.add", **params)
        return AudioAddResponse(**response)

    @pydantic.validate_call
    def edit(
        self,
        owner_id: int,
        audio_id: pydantic.PositiveInt,
        artist: str | None = None,
        title: str | None = None,
        text: str | None = None,
        genre_id: pydantic.PositiveInt | None = None,
        no_search: bool | None = None,
    ) -> AudioEditResponse:
        # ruff: noqa: FBT001,PLR0913
        # pylint: disable=W0613,R0913
        params = get_method_params(locals())
        if "no_search" in params:
            params["no_search"] = int(no_search)
        response = self._vk_audio_api.method("audio.edit", **params)
        return AudioEditResponse(**response)
