from enum import StrEnum

import pydantic
from loguru import logger
from pydantic import (
    AnyUrl,
    BaseModel,
    FilePath,
    NewPath,
    validate_call,
)
from yt_dlp import YoutubeDL


class VideoInfo(BaseModel):
    url: AnyUrl
    video_id: str
    extractor: str
    formats: list = []

    author: str
    title: str
    duration: float

    def get_name(self) -> str:
        return f"{self.extractor}_{self.video_id}"


class DownloadedFile(BaseModel):

    class Type(StrEnum):
        AUDIO = "bestaudio"
        VIDEO = "best"

    original_info: VideoInfo
    filetype: Type
    file: FilePath


Type = DownloadedFile.Type


class Downloader:

    @staticmethod
    @pydantic.validate_call
    def get_video_info(
        url: AnyUrl,
    ) -> VideoInfo:
        video_info = None
        with YoutubeDL() as yt_dlp:
            # ruff: noqa: FBT003
            video_info = yt_dlp.extract_info(str(url), False)
        return Downloader._to_video_info(video_info)

    @staticmethod
    def _to_video_info(
        yt_dlp_video_info: dict,
    ) -> VideoInfo:
        vi = yt_dlp_video_info
        return VideoInfo(
            url=vi["original_url"],
            video_id=vi["id"],
            extractor=vi["extractor"],
            author=vi["uploader"],
            title=vi["title"],
            duration=vi["duration"],
        )

    @staticmethod
    @validate_call
    def download_any(
        info: AnyUrl | VideoInfo,
        to: NewPath | FilePath,
        try_first: DownloadedFile.Type,
    ) -> DownloadedFile:
        download_order = [Type.AUDIO, Type.VIDEO]
        if download_order[0] != try_first:
            download_order.reverse()
        errors = []
        for media_type in download_order:
            # ruff: noqa: PERF203
            try:
                return Downloader._download(info, to, media_type)
            # pylint: disable=W0718
            except Exception as err:
                errors.append(err)
        # pylint: disable=W0719
        raise Exception(errors)

    @staticmethod
    @validate_call
    def download_video(
        info: AnyUrl | VideoInfo,
        to: NewPath | FilePath,
    ) -> DownloadedFile:
        return Downloader._download(info, to, Type.VIDEO)

    @staticmethod
    @validate_call
    def download_audio(
        info: AnyUrl | VideoInfo,
        to: NewPath | FilePath,
    ) -> DownloadedFile:
        return Downloader._download(info, to, Type.AUDIO)

    @staticmethod
    def _download(
        info: AnyUrl | VideoInfo,
        to: NewPath | FilePath,
        filetype: DownloadedFile.Type,
    ) -> DownloadedFile:
        # ruff: noqa: ARG004
        if isinstance(info, VideoInfo):
            return Downloader._download_video_info(info, to, filetype)
        return Downloader._download_url(info, to, filetype)

    @staticmethod
    def _download_url(
        url: AnyUrl,
        to: NewPath | FilePath,
        filetype: Type,
    ) -> DownloadedFile:
        logger.debug(locals())
        video_info = Downloader.get_video_info(str(url))
        return Downloader._download_video_info(video_info, to, filetype)

    @staticmethod
    def _download_video_info(
        video_info: VideoInfo,
        to: NewPath | FilePath,
        filetype: Type,
    ) -> DownloadedFile:
        logger.debug(locals())
        ydl_opts = {
            "format": str(filetype),
            "outtmpl": f"{to.absolute()}",
            "overwrites": True,
        }
        with YoutubeDL(ydl_opts) as yt_dlp:
            yt_dlp.download([f"{video_info.url}"])
        return DownloadedFile(
            original_info=video_info, file=to, filetype=filetype,
        )
