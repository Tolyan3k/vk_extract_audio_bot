"""TODO."""

import shutil
from pathlib import Path

import ffmpeg
from moviepy.editor import VideoFileClip
from pydantic import AnyUrl, BaseModel

from .downloader import DownloadedFile, Downloader
from .extra import File


class AudioFile(BaseModel):
    """TODO.

    Args:
    ----
        BaseModel (_type_): _description_

    """

    original: DownloadedFile
    audiofile: File


class ExtractorOptions(BaseModel):
    """TODO.

    Args:
    ----
        BaseModel (_type_): _description_

    """

    bitrate: int
    hz: int
    max_size: int


class AudioExtractor:
    """TODO.

    Raises
    ------
        ValueError: _description_

    Returns
    -------
        _type_: _description_

    """

    @staticmethod
    def extract_from_url(url: AnyUrl, temp: File, to: File) -> AudioFile:
        """TODO.

        Args:
        ----
            url (AnyUrl): _description_
            temp (File): _description_
            to (File): _description_

        Returns:
        -------
            AudioFile: _description_

        """
        if temp == to:
            msg = "Temp file path and target file path must differ"
            raise ValueError(msg)
        any_f = Downloader.download_any(url, temp, DownloadedFile.Type.AUDIO)
        aud_f = AudioExtractor.extract_from_file(any_f, to)
        Path.unlink(Path(temp.get_str()))
        return aud_f

    @staticmethod
    def extract_from_file(f: DownloadedFile, to: File) -> AudioFile:
        """TODO.

        Args:
        ----
            f (DownloadedFile): _description_
            to (File): _description_

        Raises:
        ------
            ValueError: _description_

        Returns:
        -------
            AudioFile: _description_

        """
        if f.filepath == to:
            msg = "Downloaded file path and target file path must have differents paths"
            raise ValueError(
                msg,
            )
        if f.filetype == DownloadedFile.Type.AUDIO:
            if f.filepath != to:
                shutil.copyfile(f.filepath.get_str(), to.get_str())
        else:    # VIDEO
            AudioExtractor._extract_audio(f.filepath, to)
        return AudioFile(original=f, audiofile=to)

    @staticmethod
    def _has_audio(file: File) -> bool:
        probe = ffmpeg.probe(file.get_str())
        if "streams" in probe:
            for stream in probe["streams"]:
                if stream["codec_type"] == "audio":
                    return True
        return False

    @staticmethod
    def _extract_audio(vid_f: File, to: File) -> None:
        v_clip = VideoFileClip(vid_f.get_str())
        a_clip = v_clip.audio
        a_clip.write_audiofile(to.get_str())
        v_clip.close()
        a_clip.close()
        return to
