# pylint: disable=W0621,
import ffmpeg
import pytest
from loguru import logger

from vk_extract_audio_bot.utils.downloader import (
    DownloadedFile,
    VideoInfo,
)
from vk_extract_audio_bot.utils.extractor import (
    AudioExtractor,
)

from .common import (
    VIDEO_URLS_NOT_SUPPORTS_ONLY_AUDIO,
    VIDEO_URLS_SUPPORTS_ONLY_AUDIO,
    VIDEO_URLS_UNITED,
)
from .conftest import tmp_file
from .fixture_types import (
    TmpFile,
    TmpFileRequest,
)


mp3_file = tmp_file
"""
    Фикстура-дубль `tmp_file`, чтобы можно было одновременно использовать
    2 временных файла в одном тесте без написания лишнего кода.
"""


@pytest.mark.parametrize("video_url", VIDEO_URLS_UNITED)
def test_extract_from_url_temp_file_eq_target_fail(
    video_url,
    tmp_file: TmpFile,
):
    """
    ## Входные данные:
    1. `video_url` - URL-ссылка на действительное видео.
    1. `tmp_file` - файл.

    ## Описание:
    Попытка получить аудио-файл, передав один файл в качестве временного
    и итогового.

    ## Ожидание:
    Ошибка валидации данных.
    """
    file = tmp_file.file
    with pytest.raises(ValueError):
        AudioExtractor.extract_from_url(video_url, file, file)


def test_extract_from_file_dl_file_eq_target_fail(
    tmp_file: TmpFile,
):
    """
    ## Входные данные:
    1. `tmp_file` - файл.

    ## Описание:
    Попытка получить аудио-файл, передав файл с видео в качестве итогового.

    ## Ожидание:
    Ошибка валидации данных.
    """
    target_file = tmp_file.file
    dl_file = DownloadedFile(
        original_info=VideoInfo(
            url="http://good.url",
            video_id="42",
            extractor="42",
            author="42",
            title="42",
            duration=42.0,
        ),
        filetype=DownloadedFile.Type.VIDEO,
        file=tmp_file.file,
    )
    with pytest.raises(ValueError):
        AudioExtractor.extract_from_file(dl_file, target_file)


@pytest.mark.parametrize(
    "tmp_file", [
        TmpFileRequest(create=False, suffix=".mp4"),
        TmpFileRequest(suffix=".mp4"),
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "mp3_file", [
        TmpFileRequest(),
        TmpFileRequest(suffix=".mp3"),
        TmpFileRequest(create=False, suffix=".mp3"),
    ],
    indirect=True,
)
class TestExtractor:
    """Тестирование класса `AudioExtractor` c валидными данными."""

    @pytest.mark.parametrize(
        "video_url",
        VIDEO_URLS_NOT_SUPPORTS_ONLY_AUDIO,
    )
    def test_extract_from_url_download_video(
        self,
        video_url,
        tmp_file: TmpFile,
        mp3_file: TmpFile,
    ):
        """
        ## Входные данные:
        1. `video_url` - URL-ссылка на действительное видео.
        1. `tmp_file` - файл.
        1. `mp3_file` - файл, отличный по пути от `tmp_file`.

        ## Описание:
        Извлечение аудио-файл из видео по URL-ссылке,
        через которую нельзя скачать аудио-файл отдельно от видео.

        ## Ожидание:
        Аудио-файл формата MP3.
        """
        af = AudioExtractor.extract_from_url(
            video_url,
            tmp_file.file,
            mp3_file.file,
        )
        assert ffmpeg.probe(af.audiofile)["streams"][0]["codec_name"] == "mp3"

    @pytest.mark.parametrize(
        "video_url",
        VIDEO_URLS_SUPPORTS_ONLY_AUDIO,
    )
    def test_extract_from_url_audio_only(
        self,
        video_url,
        tmp_file: TmpFile,
        mp3_file: TmpFile,
    ):
        """
        ## Входные данные:
        1. `video_url` - URL-ссылка на действительное видео.
        1. `tmp_file` - файл.
        1. `mp3_file` - файл, отличный по пути от `tmp_file`.

        ## Описание:
        Извлечение аудио-файл из видео по URL-ссылке,
        через которую также можно скачать аудио-файл отдельно от видео.

        ## Ожидание:
        Аудио-файл формата mp3
        """
        af = AudioExtractor.extract_from_url(
            video_url,
            tmp_file.file,
            mp3_file.file,
        )
        logger.debug(ffmpeg.probe(af.audiofile))
        assert ffmpeg.probe(af.audiofile)["streams"][0]["codec_name"] == "mp3"
