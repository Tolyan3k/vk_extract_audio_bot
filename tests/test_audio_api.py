from collections.abc import Generator
from tempfile import NamedTemporaryFile

import pytest
from loguru import logger
from pydantic import FilePath

from tests.common import (
    VIDEO_URLS_UNITED,
)
from vk_extract_audio_bot.settings import (
    CONFIG,
)
from vk_extract_audio_bot.utils.extractor import (
    AudioExtractor,
)
from vk_extract_audio_bot.vk_apis import (
    vk_audio_api,
)


@pytest.fixture(params=[VIDEO_URLS_UNITED[0]])
def mp3_file(
    tmp_file,
    tmp_path,
    request: pytest.FixtureRequest,
) -> Generator[FilePath]:
    """Фикстура для настоящего MP3-файла"""
    video_url = request.param
    with NamedTemporaryFile(dir=tmp_path, delete_on_close=False) as tf:
        tf.close()
        yield AudioExtractor.extract_from_url(video_url, tf, tmp_file).audiofile


@pytest.mark.parametrize(
    ("owner_id", "audio_id"), [(-1 * CONFIG.VK_ARCHIVE_GROUP_ID, 456240694)],
)
def test_add_delete_to_user(owner_id, audio_id) -> None:
    """
    Проверка: добавление и удаление аудиозаписи в библиотеке пользователя.

    Ожидание:
    1. Код ответа от VK API при добавлении больше 0,
    т.е. вернулся `id` добавленной аудиозаписи.
    2. Код ответа при удалении равен 1.
    """
    audio_add = vk_audio_api.add(owner_id, audio_id)
    audio_del = vk_audio_api.delete(
        CONFIG.VK_USER_ID,
        audio_add.response,
    )
    assert audio_add.response > 0
    assert audio_del.response == 1


@pytest.mark.parametrize(
    ("owner_id", "audio_id", "group_id"),
    [(138136673, 456242750, CONFIG.VK_ARCHIVE_GROUP_ID)],
)
def test_add_delete_to_group(owner_id, audio_id, group_id) -> None:
    """
    Проверка: добавление и удаление аудиозаписи в библиотеке группы.

    Ожидание:
    1. Код ответа от VK API при добавлении больше 0,
    т.е. вернулся `id` добавленной аудиозаписи.
    2. Код ответа при удалении равен 1.
    """
    audio_add = vk_audio_api.add(owner_id, audio_id, group_id)
    audio_del = vk_audio_api.delete(
        group_id,
        audio_add.response,
    )
    assert audio_add.response > 0
    assert audio_del.response == 1


@pytest.mark.parametrize(
    ("owner_id", "audio_id"), [(-1 * CONFIG.VK_ARCHIVE_GROUP_ID, 1)],
)
def test_add_to_user_wrong_audio_id(owner_id, audio_id) -> None:
    """
    Попытка: добавление несуществующей записи в библиотеку пользователя.

    Ожидание: ответ от VK API равен 0.
    """
    audio_add = vk_audio_api.add(owner_id, audio_id)
    assert audio_add.response == 0


@pytest.mark.parametrize(("owner_id", "audio_id"), [(CONFIG.VK_USER_ID, 228)])
def test_del_from_user_wrong_audio_id(owner_id, audio_id) -> None:
    """
    Попытка: удаление несуществующей аудиозаписи из библиотеки пользователя.

    Ожидание: ответ VK API равен 1.

    P.S. Он вообще всегда равен 1, абсолютно всегда, без исключений.
    Своего рода `noexcept` добряк.
    """
    audio_del = vk_audio_api.delete(owner_id, audio_id)
    assert audio_del.response == 1


@pytest.mark.parametrize(
    ("owner_id", "audio_id", "group_id"),
    [(CONFIG.VK_USER_ID, 1, CONFIG.VK_ARCHIVE_GROUP_ID)],
)
def test_add_to_group_wrong_audio_id(owner_id, audio_id, group_id) -> None:
    """
    Попытка: добавление несуществующей записи в библиотеку группы.

    Ожидание: ответ от VK API равен 0.
    """
    audio_add = vk_audio_api.add(owner_id, audio_id, group_id)
    assert audio_add.response == 0


@pytest.mark.parametrize(
    ("owner_id", "audio_id"), [(CONFIG.VK_ARCHIVE_GROUP_ID, 228)],
)
def test_del_from_group_wrong_audio_id(owner_id, audio_id) -> None:
    """
    Попытка: удаление несуществующей аудиозаписи из библиотеки группы.

    Ожидание: ответ VK API равен 1.

    P.S. Он вообще всегда равен 1, абсолютно всегда, без исключений.
    Своего рода `noexcept` добряк.
    """
    audio_del = vk_audio_api.delete(owner_id, audio_id)
    assert audio_del.response == 1


@pytest.mark.skip(reason="Waste VK 'audio uploads per day' limits")
def test_upload_delete(
    mp3_file,
) -> None:
    """
    Проверка: загрузка новой аудиозаписи в ВК.

    Ожидание: аудио загрузилось и затем удалено.
    """
    audio_upload = vk_audio_api.upload(mp3_file)
    logger.debug(audio_upload)
    vk_audio_api.delete(
        audio_upload.owner_id,
        audio_upload.id,
    )
