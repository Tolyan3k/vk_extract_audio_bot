"""TODO
"""

from enum import Enum

from loguru import logger
from pydantic import AnyUrl, BaseModel
from yt_dlp import YoutubeDL

from .extra import File


class VideoInfo(BaseModel):
    """TODO

    Args:
    ----
        BaseModel (_type_): _description_

    Returns:
    -------
        _type_: _description_

    """

    url: AnyUrl
    video_id: str
    extractor: str
    formats: list = []

    author: str
    title: str
    duration: float

    def get_name(self):
        """TODO

        Returns
        -------
            _type_: _description_

        """
        return f"{self.extractor}_{self.video_id}"

    @staticmethod
    def _to_video_info(yt_dlp_video_info: dict):
        vi = yt_dlp_video_info
        return VideoInfo(
            url=vi["original_url"],
            video_id=vi["id"],
            extractor=vi["extractor"],
            author=vi["uploader"],
            title=vi["title"],
            duration=vi["duration"],
        )


class DownloadedFile(BaseModel):
    """TODO

    Args:
    ----
        BaseModel (_type_): _description_

    """

    class Type(Enum):
        """TODO

        Args:
        ----
            Enum (_type_): _description_

        """

        AUDIO = "bestaudio"
        VIDEO = "best"

    original_info: VideoInfo
    filepath: File
    filetype: Type


Type = DownloadedFile.Type


class Downloader:
    """TODO

    Raises
    ------
        Exception: _description_

    Returns
    -------
        _type_: _description_

    """

    @staticmethod
    def get_video_info(url: AnyUrl) -> VideoInfo:
        """TODO

        Args:
        ----
            url (AnyUrl): _description_

        Returns:
        -------
            VideoInfo: _description_

        """
        video_info = None
        with YoutubeDL() as yt_dlp:
            video_info = yt_dlp.extract_info(url, False)
        return VideoInfo._to_video_info(video_info)

    @staticmethod
    def download_any(
        info: AnyUrl | VideoInfo,
        to: File,
        try_first: Type,
    ) -> DownloadedFile:
        """TODO

        Args:
        ----
            info (AnyUrl | VideoInfo): _description_
            to (File): _description_
            try_first (Type): _description_

        Raises:
        ------
            Exception: _description_

        Returns:
        -------
            DownloadedFile: _description_

        """
        order = [Type.AUDIO, Type.VIDEO]
        if order[0] != try_first:
            order.reverse()
        errors = []
        for type in order:
            try:
                return Downloader._download(info, to, type)
            except Exception as err:
                errors.append(err)
        raise Exception(errors)

    @staticmethod
    def download_video(info: AnyUrl | VideoInfo, to: File) -> DownloadedFile:
        """TODO

        Args:
        ----
            info (AnyUrl | VideoInfo): _description_
            to (File): _description_

        Returns:
        -------
            DownloadedFile: _description_

        """
        return Downloader._download(info, to, Type.VIDEO)

    @staticmethod
    def download_audio(info: AnyUrl | VideoInfo, to: File) -> DownloadedFile:
        """TODO

        Args:
        ----
            info (AnyUrl | VideoInfo): _description_
            to (File): _description_

        Returns:
        -------
            DownloadedFile: _description_

        """
        return Downloader._download(info, to, Type.AUDIO)

    @staticmethod
    def _download(
        info: AnyUrl | VideoInfo,
        to: File,
        filetype: Type,
    ) -> DownloadedFile:
        if type(info) is VideoInfo:
            return Downloader._download_vinfo(info, to, filetype)
        else:
            return Downloader._download_url(info, to, filetype)

    @staticmethod
    def _download_url(url: AnyUrl, to: File, filetype: Type) -> DownloadedFile:
        logger.info(locals())
        video_info = Downloader.get_video_info(url)
        return Downloader._download_vinfo(video_info, to, filetype)

    @staticmethod
    def _download_vinfo(
        video_info: VideoInfo,
        to: File,
        filetype: Type,
    ) -> DownloadedFile:
        logger.info(locals())
        file = DownloadedFile(
            original_info=video_info,
            filepath=to,
            filetype=filetype,
        )
        ydl_opts = {
            "format": file.filetype.value,
            "outtmpl": f"{file.filepath}",
        }
        with YoutubeDL(ydl_opts) as yt_dlp:
            yt_dlp.download([f"{video_info.url}"])
        return file
