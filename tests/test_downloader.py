import ffmpeg
import pytest

from tests.common import (
    VIDEO_URLS_NOT_SUPPORTS_ONLY_AUDIO,
    VIDEO_URLS_SUPPORTS_ONLY_AUDIO,
    VIDEO_URLS_UNITED,
    VIDEOS_WITH_VINFO_UNITED,
)
from tests.fixture_types import (
    TmpFile,
    TmpFileRequest,
)
from vk_extract_audio_bot.utils.downloader import (
    DownloadedFile,
    Downloader,
    Type,
)


@pytest.mark.parametrize(("video_url", "video_info"), VIDEOS_WITH_VINFO_UNITED)
def test_get_info_works(video_url, video_info):
    """
    ## Входные данные:
    1. `video_url` - URL-ссылка на действительное видео.

    ## Описание:
        Функция не падает с ошибкой.

    ## Ожидание:
        Данные о видео получены.

    ### P.S.
    Следует добавить хотя бы ожидаемые данные,
    но для экономии времени будем считать, что всё работает как надо,
    иначе бы завалились все тесты ниже.
    """
    assert video_info == Downloader.get_video_info(video_url)


@pytest.mark.parametrize("video_url", VIDEO_URLS_UNITED)
def test_download_video_dir_instead_file(video_url, tmp_path):
    """
    ## Входные данные:
    1. `video_url` - URL-ссылка на действительное видео.
    1. `tmp_path` - существующая директория

    ## Описание:
    Передача директории в качестве пути для выходного файла.

    ## Ожидание:
        Ошибка валидации входных данных.
    """
    with pytest.raises(ValueError):
        Downloader.download_video(video_url, tmp_path)


@pytest.mark.parametrize(
    "tmp_file",
    [TmpFileRequest(), TmpFileRequest(create=False)],
    indirect=True,
)
class TestDownloader:
    """
    Тестирование класса `Downloader`.

    Для каждого теста параметризуется 2 варианта пути для выходного файла:
    1. Файл уже создан
    2. Файл ещё не создан
    """

    @pytest.mark.parametrize(
        "video_url",
        VIDEO_URLS_NOT_SUPPORTS_ONLY_AUDIO,
    )
    def test_download_audio_fail(
        self,
        video_url,
        tmp_file: TmpFile,
    ):
        """
        ## Входные данные:
        1. `video_url` - URL-ссылка на действительное видео.
        1. `tmp_file` - файл.

        ## Описание:
        Cкачать отдельно аудио дорожку из видео,
        которые не предоставляют такой возможности.

        ## Ожидание:
        Ошибка во время попытки скачать аудио.
        """
        with pytest.raises(Exception):
            Downloader.download_audio(video_url, tmp_file.file)

    @pytest.mark.parametrize("video_url", VIDEO_URLS_UNITED)
    def test_download_video(
        self,
        video_url,
        tmp_file: TmpFile,
    ):
        """
        ## Входные данные:
        1. `video_url` - URL-ссылка на действительное видео.
        1. `tmp_file` - файл.

        ## Описание:
        Скачивание видео.

        ## Ожидание:
        Видео скачалось, файл имеет ненулевой размер и формат mp4.

        ### P.S.
        Проверку формата сделаю позже, т.к. пока всё работает,
        иначе бы тесты `test_extractor.py` завершались бы ошибкой.
        """
        dl_file = Downloader.download_video(video_url, tmp_file.file)
        assert (
            ffmpeg.probe(str(dl_file.file),
                                    )["streams"][0]["codec_type"] == "video"
        )

    @pytest.mark.parametrize(
        "video_url",
        VIDEO_URLS_SUPPORTS_ONLY_AUDIO,
    )
    def test_download_audio(
        self,
        video_url,
        tmp_file: TmpFile,
    ):
        """
        ## Входные данные:
        1. `video_url` - URL-ссылка на действительное видео с возможностью
        отдельно скачать аудио-дорожку.
        1. `tmp_file` - файл.

        ## Описание:
        Скачивание только аудио дорожки из видео которые это поддерживают.

        ## Ожидание:
        Выходной файл имеет только аудио дорожку.

        ### P.S.
        Здесь тоже только проверка на размер файла, но оно работает,
        причины те же, что и тестом выше.
        """
        dl_file = Downloader.download_audio(video_url, tmp_file.file)
        assert (
            ffmpeg.probe(str(dl_file.file),
                                    )["streams"][0]["codec_type"] == "audio"
        )

    @pytest.mark.parametrize("video_url", VIDEO_URLS_SUPPORTS_ONLY_AUDIO)
    def test_try_first_audio_support(
        self,
        video_url,
        tmp_file: TmpFile,
    ):
        """
        ## Описание:
        Проверка функции `Downloader.download_any` на скачивание
        с приоритетом только аудио-дорожки.

        ## Ожидание:
        Скачается только аудио-дорожка.

        ## Входные данные:
        - URL-ссылка на видео с поддержкой скачивания только аудио-дорожки.
        """
        dl_file = Downloader.download_any(video_url, tmp_file.file, Type.AUDIO)
        ffprobe_res = ffmpeg.probe(str(dl_file.file))
        assert len(ffprobe_res["streams"]) == 1
        assert ffprobe_res["streams"][0]["codec_type"] == "audio"

    @pytest.mark.parametrize("video_url", VIDEO_URLS_UNITED)
    def test_try_first_video(
        self,
        video_url,
        tmp_file: TmpFile,
    ):
        """
        ## Входные данные:
        1. `video_url` - URL-ссылка на действительное видео.
        1. `tmp_file` - файл.

        ## Описание:
        Скачать либо видео целиком, либо только аудио-дорожку
        с приоритетом видео.

        ## Ожидание:
        Непустой выходной файл - только видео.

        ### P.S.
        Здесь тоже только проверка на размер файла, но оно работает,
        причины те же, что и тестом выше.
        """
        dl_file = Downloader.download_any(
            video_url, tmp_file.file, try_first=DownloadedFile.Type.VIDEO,
        )
        assert (
            ffmpeg.probe(str(dl_file.file),
                                    )["streams"][0]["codec_type"] == "video"
        )
