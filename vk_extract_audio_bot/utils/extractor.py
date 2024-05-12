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
        temp: NewPath | FilePath,
        to: NewPath | FilePath,
    ) -> AudioFile:
        if temp == to:
            msg = "Temp file path and target file path must differ"
            raise ValueError(msg)
        any_f = Downloader.download_any(
            url,
            temp,
            DownloadedFile.Type.AUDIO,
        )
        return AudioExtractor.extract_from_file(any_f, to)

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
        match f.filetype:
            case DownloadedFile.Type.AUDIO:
                a_clip = AudioFileClip(str(f.file))
                AudioExtractor._write_audioclip_to_mp3(a_clip, to)
            case DownloadedFile.Type.VIDEO:
                AudioExtractor._extract_audio_from_video(f.file, to)
            case _:    # pytest-cov: no cover
                # pylint: disable=W0133
                ValueError()
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
        vid_f: FilePath,
        to: NewPath | FilePath,
    ) -> None:
        v_clip = VideoFileClip(str(vid_f.absolute()))
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
