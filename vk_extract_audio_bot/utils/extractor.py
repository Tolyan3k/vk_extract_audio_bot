import tempfile

import ffmpeg
import pydantic
from moviepy.editor import (
    AudioFileClip,
    VideoFileClip,
)
from pydantic import (
    AnyUrl,
    BaseModel,
    FilePath,
    NewPath,
)

from .downloader import (
    DownloadedFile,
    Downloader,
)


class AudioFile(BaseModel):
    original: DownloadedFile
    audiofile: FilePath


class ExtractorOptions(BaseModel):
    bitrate: int
    hz: int
    max_size: int


class AudioExtractor:

    @staticmethod
    @pydantic.validate_call
    def extract_from_url(
        url: AnyUrl,
        to: NewPath | FilePath,
        temp: NewPath | FilePath | None = None,
    ) -> AudioFile:
        if temp == to:
            msg = "Temp file path and target file path must differ"
            raise ValueError(msg)
        any_file = None
        if temp is None:
            with tempfile.NamedTemporaryFile(mode="wb", delete_on_close=False,
                                             dir=tempfile.gettempdir(),
                                             ) as temp_file:
                temp_file.close()
                any_file = Downloader.download_any(
                    url,
                    temp_file,
                    DownloadedFile.Type.AUDIO,
                )
        else:
            any_file = Downloader.download_any(
                url,
                temp_file,
                DownloadedFile.Type.AUDIO,
            )
        return AudioExtractor.extract_from_file(any_file, to)

    @staticmethod
    @pydantic.validate_call
    def extract_from_file(
        f: DownloadedFile,
        to: NewPath | FilePath,
    ) -> AudioFile:
        if f.file == to:
            msg = (
                "Downloaded file path"
                " and target file path"
                " must have differents"
                " paths"
            )
            raise ValueError(msg)
        if not AudioExtractor._has_audio(f.file):
            msg = "Downloaded video have no audiotrack."
            raise ValueError(msg)
        match f.filetype:
            case DownloadedFile.Type.AUDIO:
                a_clip = AudioFileClip(str(f.file))
                AudioExtractor._write_audioclip_to_mp3(a_clip, to)
            case DownloadedFile.Type.VIDEO:
                AudioExtractor._extract_audio_from_video(f.file, to)
            case _:    # pytest-cov: no cover
                msg = "Неподдерживаемый файл"
                raise ValueError(msg)
        return AudioFile(original=f, audiofile=to)

    @staticmethod
    @pydantic.validate_call
    def _has_audio(
        file: FilePath,
    ) -> bool:    # pytest-cov: no cover
        probe = ffmpeg.probe(str(file.absolute()))
        if "streams" in probe:
            for stream in probe["streams"]:
                if stream["codec_type"] == "audio":
                    return True
        return False

    @staticmethod
    @pydantic.validate_call
    def _extract_audio_from_video(
        video_file: FilePath,
        to: NewPath | FilePath,
    ) -> None:
        v_clip = VideoFileClip(str(video_file.absolute()))
        AudioExtractor._write_audioclip_to_mp3(v_clip.audio, to)
        v_clip.close()

    @staticmethod
    def _write_audioclip_to_mp3(
        clip: AudioFileClip,
        to: NewPath | FilePath,
    ) -> None:
        clip.write_audiofile(
            str(to.absolute()),
            codec="libmp3lame",
            ffmpeg_params=["-f", "mp3"],
        )
        clip.close()
