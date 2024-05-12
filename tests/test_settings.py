# ruff: noqa: S106, S107, PLR0913, E501, A002
import itertools
from collections.abc import Generator
from pathlib import Path

import pytest
from loguru import logger
from pydantic import SecretStr, ValidationError

from tests.fixture_types import TmpFile, TmpFileRequest
from vk_extract_audio_bot.settings import (
    ConfigEnv,
    ConfigYaml,
    ConfigYamlGroup,
    ConfigYamlSettings,
    ConfigYamlUser,
)


@pytest.fixture()
def user_creds() -> Generator[ConfigYamlUser.Credentials]:
    """
    Фикстура с валидными данными для входа в аккаунт ВК.

    P.S. Валидные не значит настоящие.
    """
    return create_user_creds()


@pytest.fixture()
def user_audio_client() -> Generator[ConfigYamlUser.AudioClient]:
    """
    Фикстура с валидными данными приложения для работы с аудиозаписями ВК.

    P.S. Валидные не значит настоящие.
    """
    return create_user_ac()


def create_user_creds(
    login: str = "login",
    password: str = "password",
    two_fa: str = "two_fa",
) -> ConfigYamlUser.Credentials:
    """
    Вспомогательная функция, которая экономит пару строк
    при создании объекта `ConfigYamlUser.Credentials`.
    """
    creds = {
        "login": login,
        "password": password,
        "2fa": two_fa,
    }
    return ConfigYamlUser.Credentials.model_validate(creds)


def create_user_ac(
    secret: str = "secret",
    token="token",
) -> ConfigYamlUser.AudioClient:
    """
    Вспомогательная функция, которая экономит пару секунд
    при создании объекта `ConfigYamlUser.AudioClient`.
    """
    return ConfigYamlUser.AudioClient(secret=secret, token=token)


valid_dirs = list(
    itertools.chain(
        *[[Path(path)] for path in [
            ".",
            "./'not existing path'/dir",
        ]],
    ),
)
"""Список валидных путей для директорий."""


class TestConfigEnv:
    """
    Тестирование класса `ConfigEnv`, который содержит настройки
    переменных среды
    """

    @pytest.mark.parametrize(
        "tmp_file",
        [TmpFileRequest(create=False)],
        indirect=True,
    )
    def test_not_existing_file_fail(self, tmp_file: TmpFile):
        """
        ## Описание
        Попытка инициализировать конфигурацию,
        передав путь к несуществующему файлу.

        ## Входные данные
        1. `tmp_file` - несуществующий файл.

        ## Ожидание:
        Ошибка валидации входных данных.
        """
        with pytest.raises(ValidationError):
            ConfigEnv(CONFIG=tmp_file.file)

    def test_dir_instead_file_fail(self, tmp_path):
        """
        ## Описание:
        Попытка инициализировать конфигурацию,
        передав путь к папке к папке вместо пути к файлу.

        ## Входные данные:
        1. `tmp_path` - существующая директория.

        ## Ожидание:
        Ошибка валидации входных данных.
        """
        with pytest.raises(ValidationError):
            ConfigEnv(CONFIG=tmp_path)

    def test_existing_file(self, tmp_file: TmpFile):
        """
        ## Описание:
        Попытка инициализировать конфигурацию,
        передав путь к папке к папке вместо пути к файлу.

        ## Входные данные:
        1. `tmp_file` - существующий файл.

        Ожидание:
        Конфигурация инициализировалась без ошибок.
        """
        cfg = ConfigEnv(CONFIG=tmp_file.file)
        cfg.yaml_config_file.exists()
        assert tmp_file.file == cfg.yaml_config_file


class TestConfigYamlSettings:
    """
    Тестирование класса `ConfigYamlSettings`.

    Класс содержит настройки бота:
    рабочие директории, база данных, ограничения на длину видео и т.п.
    """

    @pytest.mark.parametrize(
        ("config", "expected"),
        [
            (
                ConfigYamlSettings(),
                {
                    "work_dirs": {
                        "main": str(Path()),
                        "data": str(Path("./data")),
                        "audios": str(Path("./temp/audios")),
                        "videos": str(Path("./temp/videos")),
                    },
                    "msg_processing_delay": 5,
                    "worker_count": 1,
                    "db_url": f"sqlite:///{Path("./data")!s}/database.db",
                    "video_min_duration": 0,
                    "video_max_duration": 1800,
                },
            ),
        ],
    )
    def test_defaults(self, config: ConfigYamlSettings, expected):
        """
        ## Описание:
        Проверка на соответствие значениям по умолчанию

        ## Входные данные:
        - `config` - объект с настройками бота, инициализированный значениями
        по умолчанию

        ## Ожидание:
        Полное соответствие значениям по умолчанию.
        """
        assert config.model_dump(mode="json") == expected

    @pytest.mark.parametrize("main", valid_dirs)
    def test_change_only_main_dir(self, main: Path):
        """
        ## Описание:
        Проверка выбора рабочих директорий по умолчанию:
        если задана только главная директория `main`,
        то все остальные директории будут поддиректориями главной

        ## Входные данные:
        - `main` - произвольный путь к главной директории

        ## Ожидание:
        Все директории наследуют путь от главной
        """
        work_dir = ConfigYamlSettings.WorkDirs(main=main)
        for dir_path in dict(work_dir).values():
            dir_path: Path
            assert dir_path.is_relative_to(main)

    @pytest.mark.parametrize("main", [None, *valid_dirs])
    @pytest.mark.parametrize("data", [None, *valid_dirs])
    @pytest.mark.parametrize("audios", [None, *valid_dirs])
    @pytest.mark.parametrize("videos", [None, *valid_dirs])
    def test_valid_work_defaults(self, main: Path, data, audios, videos):
        """
        ## Описание:
        Проверка выбора рабочих директорий по умолчанию:
        если значение по умолчанию для не главной (`data`, `audios`,
        `videos`) директории изменено, то они не должны реагировать
        на изменение главной директории, т.е. стать независимыми, иначе
        наследуют путь от `main`

        ## Входные данные:
        - `main` - произвольный путь к главной директории бота.
        - `data` - произвольный путь к директории бота для базы данных.
        - `audios` - произвольный путь к директории бота для временного хранения
        аудиозаписей.
        - `videos` - произвольный путь к директории бота для временного хранения
        видео.

        ## Ожидание:
        В соответствии с описанием.
        """
        wd_all = {
            "main": main,
            "data": data,
            "audios": audios,
            "videos": videos,
        }
        wd_not_none = {}
        [
            wd_not_none.setdefault(k,v)
            for k, v
            in wd_all.items() if v is not None
        ]
        wd = ConfigYamlSettings.WorkDirs.model_validate(wd_not_none)
        wd_default = ConfigYamlSettings.WorkDirs()
        for wd_all_name, wd_all_val in wd_all.items():
            wd_all_val: Path
            wd_val: Path = dict(wd)[wd_all_name]
            if wd_all_val is None and main is None:
                assert wd_val == dict(wd_default)[wd_all_name]
            elif wd_all_val is None and main:
                assert wd_val.relative_to(main)
            elif wd_all_val:
                assert wd_val == wd_all_val

    @pytest.mark.parametrize("main", [None, "tmp_file"])
    @pytest.mark.parametrize("data", [None, "tmp_file"])
    @pytest.mark.parametrize("audios", [None, "tmp_file"])
    @pytest.mark.parametrize("videos", [None, "tmp_file"])
    def test_file_instead_dir_fail(
        self,
        main,
        data,
        audios,
        videos,
        request: pytest.FixtureRequest,
    ):
        """
        ## Описание:
        Попытка передать путь к файлу вместо пути к папке.

        ## Входные данные:
        - `main` - произвольный путь к главной директории бота.
        - `data` - произвольный путь к директории бота для базы данных.
        - `audios` - произвольный путь к директории бота для временного хранения
        аудиозаписей.
        - `videos` - произвольный путь к директории бота для временного хранения
        видео.

        Ожидание:
        Ошибка валидации данных.
        """
        wd_all = {
            "main": main,
            "data": data,
            "audios": audios,
            "videos": videos,
        }
        wd_not_none = {}
        for k, v in wd_all.items():
            if v is not None:
                tmp_file: TmpFile = request.getfixturevalue(v)
                wd_not_none[k] = str(tmp_file.file.absolute())
        if not wd_not_none:
            return
        with pytest.raises(ValidationError):
            ConfigYamlSettings.WorkDirs.model_validate(wd_not_none)

    @pytest.mark.parametrize("msg_proc_delay", [None, -1, 0.2])
    @pytest.mark.parametrize("worker_count", [None, -1, 0, 0.1, 1.1])
    @pytest.mark.parametrize("db_url", [None, 1234, ""])
    @pytest.mark.parametrize("video_min_duration", [None, -1, 0.2])
    @pytest.mark.parametrize("video_max_duration", [None, -1, 0, 0.1, 1.1])
    def test_settings_fail(
        self,
        msg_proc_delay,
        worker_count,
        db_url,
        video_min_duration,
        video_max_duration,
    ):
        """
        ## Описание:
        Попытка передать неправильные параметры при инициализации настроек.

        ## Входные данные:
        - `msg_proc_delay` - число не соответствующее целому неотрицательному.
        - `worker_count` - число не соответствующее целому положительному.
        - `db_url` - не строка, или пустая строка.
        - `video_min_duration` - число не соответствующее целому неотрицательному.
        - `video_max_duration` - число не соответствующее целому положительному.

        ## Ожидание:
        Ошибка во время валидации данных.
        """
        wd_all = {
            "msg_processing_delay": msg_proc_delay,
            "worker_count": worker_count,
            "db_url": db_url,
            "video_min_duration": video_min_duration,
            "video_max_duration": video_max_duration,
        }
        wd_not_none = {}
        [
            wd_not_none.setdefault(k,v)
            for k, v
            in wd_all.items() if v is not None
        ]
        if not wd_not_none:
            return
        with pytest.raises(ValidationError):
            ConfigYamlSettings.model_validate(wd_not_none)

    @pytest.mark.parametrize("msg_proc_delay", [None, -42, 0.42])
    @pytest.mark.parametrize("worker_count", [None, -42, 0, 0.42])
    @pytest.mark.parametrize("db_url", [None, 42, ""])
    @pytest.mark.parametrize("video_min_duration", [None, -42, 0.42])
    @pytest.mark.parametrize("video_max_duration", [None, -42, 0, 0.42])
    def test_settings_set_invalid_value_fail(
        self,
        msg_proc_delay,
        worker_count,
        db_url,
        video_min_duration,
        video_max_duration,
    ):
        """
        ## Описание:
        Попытка изменить текущий объект с настройками на неправильные
        значения.

        ## Входные данные:
        - `msg_proc_delay` - число не соответствующее целому неотрицательному.
        - `worker_count` - число не соответствующее целому положительному.
        - `db_url` - не строка, или пустая строка.
        - `video_min_duration` - число не соответствующее целому неотрицательному.
        - `video_max_duration` - число не соответствующее целому положительному.

        ## Ожидание:
        Ошибка во время валидации входных данных.
        """
        sets = ConfigYamlSettings()
        with pytest.raises(ValidationError):
            sets.msg_processing_delay = msg_proc_delay
        with pytest.raises(ValidationError):
            sets.worker_count = worker_count
        with pytest.raises(ValidationError):
            sets.db_url = db_url
        with pytest.raises(ValidationError):
            sets.video_min_duration = video_min_duration
        with pytest.raises(ValidationError):
            sets.video_max_duration = video_max_duration

    @pytest.mark.parametrize("video_min_duration", [42])
    @pytest.mark.parametrize("video_max_duration", [1, 41])
    def test_video_min_dur_gt_max_dur(
        self,
        video_min_duration,
        video_max_duration,
    ):
        """
        ## Описание:
        Попытка задать минимальную длину видео больше, чем максимальную.

        ## Ожидание:
        Ошибка при валидации данных.

        ## Входные данные:
        - `video_min_duration` - целое положительное число,
        строго большее `video_max_duration`.
        - `video_max_duration` - целое положительное число,
        строго меньшее `video_min_duration`.
        """
        sets = ConfigYamlSettings()
        with pytest.raises(ValidationError):
            # ruff: noqa: PT012
            sets.video_min_duration = video_min_duration
            sets.video_max_duration = video_max_duration
        with pytest.raises(ValidationError):
            # ruff: noqa: PT012
            sets.video_max_duration = video_max_duration
            sets.video_min_duration = video_min_duration

    @pytest.mark.parametrize("msg_proc_delay", [0, 42])
    @pytest.mark.parametrize("worker_count", [1, 42])
    @pytest.mark.parametrize("db_url", ["42"])
    @pytest.mark.parametrize("video_min_duration", [0, 42])
    @pytest.mark.parametrize("video_max_duration", [42])
    def test_settings_set_valid_value(
        self,
        msg_proc_delay,
        worker_count,
        db_url,
        video_min_duration,
        video_max_duration,
    ):
        """
        ## Описание:
        Задание валидных параметров в существующем объекте.

        ## Ожидание:
        Параметры объекта изменены и соответствую новым значениям.

        ## Входные данные:
        - `msg_proc_delay` - целое неотрицательное число.
        - `worker_count` - целое положительное число.
        - `db_url` - непустая строка.
        - `video_min_duration` - целое неотрицательное число.
        - `video_max_duration` - целов положительное число.
        """
        sets = ConfigYamlSettings()
        sets.msg_processing_delay = msg_proc_delay
        sets.worker_count = worker_count
        sets.db_url = db_url
        sets.video_min_duration = video_min_duration
        sets.video_max_duration = video_max_duration
        assert sets.msg_processing_delay == msg_proc_delay
        assert sets.worker_count == worker_count
        assert sets.db_url == SecretStr(db_url)
        assert sets.video_min_duration == video_min_duration
        assert sets.video_max_duration == video_max_duration


class TestConfigYamlGroup:
    """
    Тестирование класса `ConfigYamlGroup`.

    Класс содержит объект группы ВК: id группы, её тип относительно бота
    и токены для работы с этой группой
    """

    @pytest.mark.parametrize("id", [42, "42"])
    @pytest.mark.parametrize(
        "type",
        [
            "main",
            "archive",
            ConfigYamlGroup.Type.ARCHIVE,
            ConfigYamlGroup.Type.MAIN,
        ],
    )
    def test_no_tokens_fail(self, id, type):
        """
        ## Описание:
        Создание объекта без хотя бы одного токена.

        ## Ожидание:
        Ошибка валидации данных.

        ## Входные данные:
        - `id` - валидный id пользователя.
        - `type` - валидный тип группы.
        - `tokens` - пустой список предполагаемых токенов.
        """
        with pytest.raises(ValidationError):
            ConfigYamlGroup(type=type, id=id, tokens=[])

    @pytest.mark.parametrize("id", [42, "42"])
    @pytest.mark.parametrize(
        "type",
        [
            "main",
            "archive",
            ConfigYamlGroup.Type.ARCHIVE,
            ConfigYamlGroup.Type.MAIN,
        ],
    )
    @pytest.mark.parametrize("tokens", [["42", "42"], ["42", "24", "42"]])
    def test_tokens_assign_list(self, id, type, tokens):
        """
        ## Описание:
        Присвоение объекту токенов, содержащих дубли.

        ## Ожидание:
        Объект содержит только уникальные токены.

        ## Входные данные:
        - `id` - валидный id для объекта `ConfigYamlGroup`.
        - `type` - валидный тип группы для объекта `ConfigYamlGroup`.
        - `tokens` - список строк, содержащий повторяющиеся значения.
        """
        cfg = ConfigYamlGroup(type=type, id=id, tokens=tokens)
        cfg.tokens = tokens
        assert isinstance(cfg.tokens, set)
        assert cfg.tokens == set(map(SecretStr, tokens))

    @pytest.mark.parametrize("id", [42, "42"])
    @pytest.mark.parametrize(
        "type",
        [
            "main",
            "archive",
            ConfigYamlGroup.Type.ARCHIVE,
            ConfigYamlGroup.Type.MAIN,
        ],
    )
    @pytest.mark.parametrize("tokens", [["42", "42"], ["42", "24", "42"]])
    def test_non_unique_tokens(self, id, type, tokens):
        """
        ## Описание:
        Инициализация объекта списком токенов, содержащих дубли.

        ## Ожидание:
        объект содержит только уникальные токены.

        ## Входные данные:
        - `id` - валидный id для объекта `ConfigYamlGroup`.
        - `type` - валидный тип группы для объекта `ConfigYamlGroup`.
        - `tokens` - список строк, содержащий повторяющиеся значения.
        """
        cfg = ConfigYamlGroup(type=type, id=id, tokens=tokens)
        assert set(map(SecretStr, tokens)) == cfg.tokens

    @pytest.mark.parametrize("id", [42, "42"])
    @pytest.mark.parametrize(
        "type",
        [
            "main",
            "archive",
            ConfigYamlGroup.Type.ARCHIVE,
            ConfigYamlGroup.Type.MAIN,
        ],
    )
    @pytest.mark.parametrize("tokens", [["42"], ["42", "24"]])
    def test_add_non_unique_token(self, id, type, tokens):
        """
        ## Описание:
        Добавление в объект токенов, которые уже в нём содержатся.

        ## Ожидание:
        объект содержит только уникальные токены.

        ## Входные данные:
        - `id` - валидный id для объекта `ConfigYamlGroup`.
        - `type` - валидный тип группы для объекта `ConfigYamlGroup`.
        - `tokens` - список строк.
        """
        cfg = ConfigYamlGroup(type=type, id=id, tokens=tokens)
        cfg.tokens = cfg.tokens.union(tokens)
        assert set(map(SecretStr, tokens)) == cfg.tokens

    @pytest.mark.parametrize("id", [42, "42"])
    @pytest.mark.parametrize(
        "type",
        [
            "main",
            "archive",
            ConfigYamlGroup.Type.ARCHIVE,
            ConfigYamlGroup.Type.MAIN,
        ],
    )
    @pytest.mark.parametrize("tokens", [["42"], ["42", "24"]])
    def test_create_valid(self, id, type, tokens):
        """
        ## Описание:
        Создание объекта.

        ## Ожидание:
        объект создан.

        ## Входные данные:
        - `id` - валидный id для объекта `ConfigYamlGroup`.
        - `type` - валидный тип группы для объекта `ConfigYamlGroup`.
        - `tokens` - список строк.
        """
        cfg = ConfigYamlGroup(type=type, id=id, tokens=tokens)
        assert cfg.id == int(id)
        assert cfg.type == type
        assert cfg.tokens == set(map(SecretStr, tokens))


class TestConfigYamlUserCredentials:
    """
    Тестирование класса `ConfigYamlUser.Credentials`.

    Класс содержит пользовательские данных для входа в ВК.
    """

    @pytest.mark.parametrize("login", [None, ""])
    @pytest.mark.parametrize("password", ["42"])
    @pytest.mark.parametrize("two_fa", [None, "42"])
    def test_empty_login_fail(self, login, password, two_fa):
        """
        ## Описание:
        Инициализация с пустым логином.

        ## Ожидание:
        Ошибка.

        ## Входные данные:
        - `login` - не строка и не положительно число, либо пустая строка.
        - `password` - валидный пароль для объекта `ConfigYamlUser.Credentials`.
        - `two_fa` - валидный секретный код 2fa для
        объекта `ConfigYamlUser.Credentials`.
        """
        creds = {
            "login": login,
            "password": password,
            "2fa": two_fa,
        }
        with pytest.raises(ValidationError):
            ConfigYamlUser.Credentials.model_validate(creds)

    @pytest.mark.parametrize("login", ["42", 42])
    @pytest.mark.parametrize("password", [None, ""])
    @pytest.mark.parametrize("two_fa", [None, "42"])
    def test_empty_password_fail(self, login, password, two_fa):
        """
        ## Описание:
        Инициализация с пустым паролем.

        ## Ожидание:
        Ошибка.

        ## Входные данные:
        - `login` - валидный логин для объекта `ConfigYamlUser.Credentials`.
        - `password` - не строка или пустая строка.
        - `two_fa` - валидный секретный код 2fa для
        объекта `ConfigYamlUser.Credentials`.
        """
        creds = {
            "login": login,
            "password": password,
            "2fa": two_fa,
        }
        with pytest.raises(ValidationError):
            ConfigYamlUser.Credentials.model_validate(creds)

    @pytest.mark.parametrize("login", ["42", 42])
    @pytest.mark.parametrize("password", ["42"])
    @pytest.mark.parametrize("two_fa", [42, ""])
    def test_invalid_two_fa_fail(self, login, password, two_fa):
        """
        ## Описание:
        Инициализация с невалидным секретным ключом
        двухфакторной аутентификации.

        ## Ожидание:
        Ошибка

        ## Входные данные:
        - `login` - валидный логин для объекта `ConfigYamlUser.Credentials`.
        - `password` - валидный пароль для объекта `ConfigYamlUser.Credentials`.
        - `two_fa` - не пустой элемент и не строка или пустая строка.
        """
        creds = {
            "login": login,
            "password": password,
            "2fa": two_fa,
        }
        with pytest.raises(ValidationError):
            ConfigYamlUser.Credentials.model_validate(creds)

    @pytest.mark.parametrize("login", [None, ""])
    @pytest.mark.parametrize("password", [None, "", 42])
    @pytest.mark.parametrize("two_fa", [42, ""])
    def test_change_to_invalid_fail(self, login, password, two_fa):
        """
        ## Описание:
        Попытка изменить поле на невалидное.

        ## Ожидание:
        Ошибка.

        ## Входные данные:
        - валидный объект `ConfigYamlUser.Credentials`
        - `login` - не строка и не положительно число, либо пустая строка.
        - `password` - не строка или пустая строка.
        - `two_fa` - не пустой элемент и не строка или пустая строка.
        """
        creds = ConfigYamlUser.Credentials.model_validate(
            {
                "login": "login",
                "password": "password",
                "2fa": "two_fa",
            },
        )
        with pytest.raises(ValidationError):
            creds.login = login
        with pytest.raises(ValidationError):
            creds.password = password
        with pytest.raises(ValidationError):
            creds.two_fa = two_fa

    @pytest.mark.parametrize("login", ["42", 42])
    @pytest.mark.parametrize("password", ["42"])
    @pytest.mark.parametrize("two_fa", [None, "42"])
    def test_valid_two_fa(self, login, password, two_fa):
        """
        ## Описание:
        Инициализация с валидным секретным ключом
        двухфакторной аутентификации.

        ## Ожидание:
        Инициализации прошла успешно.

        ## Входные данные:
        - `login` - валидный логин для объекта `ConfigYamlUser.Credentials`.
        - `password` - валидный пароль для объекта `ConfigYamlUser.Credentials`.
        - `two_fa` - `None`, либо непустая строка.
        """
        creds = {
            "login": str(login),
            "password": password,
            "2fa": two_fa,
        }
        cfg_creds = ConfigYamlUser.Credentials.model_validate(creds)
        assert creds == cfg_creds.model_dump(mode="json", by_alias=True)

class TestConfigYamlUserAudioClient:
    """
    Тестирование класса `ConfigYamlUser.AudioClient`.

    Класс содержит код приложения и токен с доступом к аудизаписям ВК.
    """

    @pytest.mark.parametrize("token", [None, "", 42])
    def test_invalid_secret_fail(self, token):
        """
        ## Описание:
        Инициализация объекта с невалидным токеном.

        ## Ожидание:
        Ошибка валидации входных данных.

        ## Входные данные:
        - валидная строка для поля `secret` объекта `ConfigYamlUser.AudioClient`.
        - `token` - не строка, или пустая строка.
        """
        with pytest.raises(ValidationError):
            ConfigYamlUser.AudioClient(secret="secret", token=token)

    @pytest.mark.parametrize("secret", [None, "", 42])
    @pytest.mark.parametrize("token", [None, "", 42])
    def test_change_on_invalid_fail(self, secret, token):
        """
        ## Описание:
        Попытка изменения полей объекта на невалидные значения.

        ## Ожидание:
        Ошибка валидации после изменения данных.

        ## Входные данные:
        - валидный объект `ConfigYamlUser.AudioClient`
        - `secret` - не строка, или пустая строка.
        - `token` - не строка, или пустая строка.
        """
        ac = ConfigYamlUser.AudioClient(secret="secret", token="token")
        with pytest.raises(ValidationError):
            ac.secret = secret
        with pytest.raises(ValidationError):
            ac.token = token

class TestConfigYamlUser:
    """
    Тестирование класса `ConfigYamlUser`.

    Класс содержит данные пользователя, для работы с ВК API.
    """

    def test_create_user_no_creds_and_audio_fail(self):
        """
        ## Описание:
        Попытка инициализации объекта без данных о приложении с доступом
        к аудиозаписям или хотя бы данных для входа в аккаунт.

        ## Ожидание:
        Ошибка валидации входных данных.

        ## Входные данные:
        - валидный id для объекта `ConfigYamlUser`
        - валидный токен для объекта `ConfigYamlUser`
        """
        with pytest.raises(ValueError):
            ConfigYamlUser(
                id=42,
                token="token",
                credentials=None,
                audio_client=None,
            )

    @pytest.mark.parametrize("creds", [None, "user_creds"])
    @pytest.mark.parametrize("audio_client", [None, "user_audio_client"])
    def test_change_both_creds_and_audio_to_none_fail(
        self,
        creds,
        audio_client,
        request: pytest.FixtureRequest,
    ):
        """
        ## Описание:
        Попытка изменить объект, присвоив `None` полям данных для входа
        и данных о приложении с доступом к аудиозаписям.

        ## Ожидание:
        Ошибка валидации, когда оба поля `credentials` и `audio_client` объекта
        `ConfigYamlUser` станут равны `None`.

        ## Входные данные:
        - `creds` - валидный объект `ConfigYamlUser.Credentials`
        - `audio_client` - валидный объект `ConfigYamlUser.AudioClient`
        """
        if not any([creds, audio_client]):
            return    # skip invalid case
        if creds:
            creds = request.getfixturevalue(creds)
        if audio_client:
            audio_client = request.getfixturevalue(audio_client)
        user = ConfigYamlUser(
            id=42,
            token="token",
            credentials=creds,
            audio_client=audio_client,
        )
        with pytest.raises(ValueError):
            user.credentials = None
            user.audio_client = None

    @pytest.mark.parametrize("creds", [None, "user_creds"])
    @pytest.mark.parametrize("audio_client", [None, "user_audio_client"])
    def test_create_valid_user(
        self,
        creds,
        audio_client,
        request: pytest.FixtureRequest,
    ):
        """
        ## Описание:
        Создание объекта с валидными данными.

        ## Ожидание:
        Объект создан и соответветствует заданным значениям.

        ## Входные данные:
        - `creds` - валидный объект `ConfigYamlUser.Credentials`
        - `audio_client` - валидный объект `ConfigYamlUser.AudioClient`
        """
        if not any([creds, audio_client]):
            return    # skip invalid case
        if creds:
            creds = request.getfixturevalue(creds)
        if audio_client:
            audio_client = request.getfixturevalue(audio_client)
        ConfigYamlUser(
            id=42,
            token="token",
            credentials=creds,
            audio_client=audio_client,
        )


class TestConfigYaml:
    """
    Тестирование класса `ConfigYamlUser`.

    Класс содержит настройки бота, группы в которых бот будет отвечать
    на сообщения и пользователей для работы с ВК API.
    """

    @pytest.fixture()
    def yaml_user(
        self,
        user_creds,
        user_audio_client,
    ) -> Generator[ConfigYamlUser]:
        """Валидный пользователь для `ConfigYaml`."""
        return ConfigYamlUser(
            id=42,
            token="42",
            credentials=user_creds,
            audio_client=user_audio_client,
        )

    @pytest.fixture()
    def yaml_groups(self):
        """Валидные группы для `ConfigYaml`."""
        return [
            ConfigYamlGroup(
                type=ConfigYamlGroup.Type.ARCHIVE,
                id=42,
                tokens=["42"],
            ),
            ConfigYamlGroup(
                type=ConfigYamlGroup.Type.MAIN,
                id=42,
                tokens=["42"],
            ),
        ]

    @pytest.fixture()
    def yaml_config(self, tmp_file: TmpFile, yaml_user, yaml_groups):
        """Валидный конфиг `ConfigYaml`."""
        return ConfigYaml(
            users=[yaml_user],
            groups=yaml_groups,
            config_file=tmp_file.file,
        )

    def test_zero_groups_fail(self, yaml_user):
        """
        ## Описание:
        Попытка создать объект без групп.

        ## Ожидание:
        Ошибка.

        ## Входные данные:
        - `yaml_user` - валидный пользователь.
        - пустой список объектов `ConfigYamlGroup`.
        """
        with pytest.raises(ValueError):
            ConfigYaml(users=[yaml_user], groups=[])

    @pytest.mark.parametrize(
        "group_type",
        [ConfigYamlGroup.Type.ARCHIVE, ConfigYamlGroup.Type.MAIN],
    )
    def test_only_one_group_fail(self, yaml_user, group_type):
        """
        ## Описание:
        Попытка создать конфиг только с одной группой вместо двух.

        ## Ожидание:
        Ошибка.

        ## Входные данные:
        - `yaml_user` - валидный пользователь.
        - `group_type` - валидный тип группы `ConfigYamlGroup`.
        """
        group = ConfigYamlGroup(
            type=group_type,
            id=42,
            tokens=["42"],
        )
        with pytest.raises(ValueError):
            ConfigYaml(users=[yaml_user], groups=[group])

    def test_zero_users_fail(self, yaml_groups):
        """
        ## Описание:
        Попытка инициализировать конфиг без пользователей.

        ## Ожидание:
        Ошибка.

        ## Входные данные:
        - `yaml_groups` - непустой список объектов `ConfigYamlGroup`,
        валидных для инициализации `ConfigYaml`.
        """
        with pytest.raises(ValueError):
            ConfigYaml(users=[], groups=yaml_groups)

    @pytest.mark.parametrize(
        "group_type",
        [ConfigYamlGroup.Type.ARCHIVE, ConfigYamlGroup.Type.MAIN],
    )
    def test_only_one_type_of_group_fail(self, yaml_user, group_type):
        """
        ## Описание:
        Попытка инициализировать конфиг с использованием групп
        только одного типа.

        ## Ожидание:
        Ошибка валидации входных данных.

        ## Входные данные:
        - `yaml_user` - валидный объект `ConfigYamlUser`.
        - `groups` - список объектов `ConfigYamlGroup` размером не меньше 2,
        где у каждого объекта значение в поле `type` одно и то же.
        """
        groups = [
            ConfigYamlGroup(
                type=group_type,
                id=i,
                tokens=["42"],
            )
            for i in range(1, 10)
        ]
        with pytest.raises(ValueError):
            ConfigYaml(users=[yaml_user], groups=groups)

    @pytest.mark.parametrize(
        "tmp_file",
        [TmpFileRequest(create=False)],
        indirect=True,
    )
    def test_not_existing_config_file_fail(
        self,
        yaml_user,
        yaml_groups,
        tmp_file: TmpFile,
    ):
        """
        ## Описание:
        Попытка инициализировать конфиг,
        передав несуществующий путь к файлу.

        ## Ожидание:
        Ошибка валидации входных данных.

        ## Входные данные:
        - `yaml_user` - валидный объект `ConfigYamlUser`.
        - `yaml_groups` - непустой список объектов `ConfigYamlGroup`,
        валидных для инициализации `ConfigYaml`.
        - `tmp_file` - несуществующий файл.
        """
        with pytest.raises(ValueError):
            ConfigYaml(
                users=[yaml_user],
                groups=yaml_groups,
                config_file=tmp_file,
            )

    @pytest.mark.parametrize("tokens", [["42", "24"], ["42", "42"]])
    @pytest.mark.parametrize("creds_login", [["42", "24"], ["42", "42"]])
    @pytest.mark.parametrize("creds_password", [["42", "24"], ["42", "42"]])
    @pytest.mark.parametrize("creds_two_fa", [["42", "24"], ["42", "42"]])
    @pytest.mark.parametrize("acs_secret", [["42", "24"], ["42", "42"]])
    @pytest.mark.parametrize("acs_token", [["42", "24"], ["42", "42"]])
    def test_users_same_id_diff_same_fields_fail(
        self,
        yaml_groups,
        tokens,
        creds_login,
        creds_password,
        creds_two_fa,
        acs_secret,
        acs_token,
    ):
        """
        ## Описание:
        Попытка инициализировать конфиг, передав список пользователей
        среди которых есть пользователи с одним `id`,
        но при этом есть не пустые поля, которые при этом отличаются.

        Например, не может существовать такой пользователь, у которого 2
        разных пароля от аккаунта, или 2 разных логина.

        И хотя у одного пользователя может быть несколько токенов приложения
        для работы с аудиозаписями, для бота нужен только 1, поэтому
        если у пользователя данные для приложения отличаются, то это тоже
        считается ошибкой.

        ## Ожидание:
        Ошибка во время валидации данных.

        ## Входные данные:
        - `yaml_groups` - непустой список объектов `ConfigYamlGroup`,
        валидных для инициализации `ConfigYaml`.
        - `tokens` - список строк.
        - `creds_login` - список строк.
        - `creds_password` - список строк.
        - `creds_two_fa` - список строк.
        - `acs_secret` - список строк.
        - `acs_token` - список строк.

        При этом хотя бы в одном из представленных списков, пара значений должна
        отличаться друг от друга.
        """
        params = list(locals().values())[2:]
        if len(params) == sum(map(len, map(set, params))):
            return    # all fields the same: nothing to test
        users = []
        for i in range(2):
            users += [
                ConfigYamlUser(
                    id=42,
                    token=tokens[i],
                    credentials=create_user_creds(
                        creds_login[i],
                        creds_password[i],
                        creds_two_fa[i],
                    ),
                    audio_client=create_user_ac(acs_secret[i],
                                                acs_token[i]),
                ),
            ]
        with pytest.raises(ValueError):
            ConfigYaml(groups=yaml_groups, users=users)

    def test_same_group_twice(self, yaml_user, yaml_groups):
        """
        ## Описание:
        Инициализация конфига списком групп, содержащим дубли.

        ## Ожидание:
        Конфиг содержит только уникальные данные о группах.

        ## Входные данные:
        - `yaml_user` - валидный объект `ConfigYamlUser`.
        - `yaml_groups` - непустой список объектов `ConfigYamlGroup`,
        валидных для инициализации `ConfigYaml`.
        """
        logger.debug(yaml_user)
        cfg = ConfigYaml(users=[yaml_user], groups=[*yaml_groups, *yaml_groups])
        assert len(cfg.groups) == len(yaml_groups)
        assert cfg.groups == yaml_groups

    def test_same_user_twice(self, yaml_user, yaml_groups):
        """
        ## Описание:
        Инициализация конфига списком пользователей, содержащим дубли.

        ## Ожидание:
        Конфиг содержит только уникальные данные о пользователях.

        ## Входные данные:
        - `yaml_user` - валидный объект `ConfigYamlUser`.
        - `yaml_groups` - непустой список объектов `ConfigYamlGroup`,
        валидных для инициализации `ConfigYaml`.
        """
        cfg = ConfigYaml(users=[yaml_user, yaml_user], groups=yaml_groups)
        assert len(cfg.users) == 1
        assert cfg.users[0] == yaml_user

    def test_unite_users(self, yaml_user: ConfigYamlUser, yaml_groups):
        """
        ## Описание:
        Инициализация конфига списком пользователей, среди которых есть
        пользователи с одним `id`, и они дополняют поля друг друга,
        т.е. у одного такого пользователя есть данные для входа в аккаунт,
        но нет данных о приложении для работы с аудиозаписями,
        а у 2го наоборот.

        ## Ожидание:
        каждый элемент из списка пользователей в конфиге
        соответствует пользователю с уникальным `id` и объединёнными полями.

        ## Входные данные:
        - `yaml_user` - валидный объект `ConfigYamlUser`.
        - `yaml_groups` - непустой список объектов `ConfigYamlGroup`,
        валидных для инициализации `ConfigYaml`.
        """
        user_in_the_middle = yaml_user.model_copy(deep=True)
        user_in_the_middle.id += 1
        users = [
            ConfigYamlUser(
                id=yaml_user.id,
                token=yaml_user.token,
                credentials=yaml_user.credentials,
            ),
            user_in_the_middle,
            ConfigYamlUser(
                id=yaml_user.id,
                token=yaml_user.token,
                audio_client=yaml_user.audio_client,
            ),
        ]
        cfg = ConfigYaml(users=users, groups=yaml_groups)
        assert len(cfg.users) == 1 + 1    # Evade magic number rule
        assert yaml_user.credentials == cfg.users[0].credentials
        assert yaml_user.audio_client == cfg.users[0].audio_client
        assert user_in_the_middle == cfg.users[1]

    def test_save_to_not_existing_file_fail(
        self,
        tmp_file: TmpFile,
        yaml_config: ConfigYaml,
    ):
        """
        ## Описание:
        Попытка сохранить конфиг в несуществующий файл.

        ## Ожидание:
        Ошибка валидации входных данных.

        ## Входные данные:
        - `tmp_file` - несуществующий файл.
        - `yaml_config` - валидный конфиг.
        """
        tmp_file.file.unlink()
        with pytest.raises(ValidationError):
            yaml_config.save(tmp_file.file)

    def test_load_config_file_not_set_fail(self, yaml_config: ConfigYaml):
        """
        ## Описание:
        Попытка загрузить конфиг из файла, который не задан.

        ## Ожидание:
        Ошибка валидации при попытке загрузить незаданный файл.

        ## Входные данные:
        - `yaml_config` - валидный конфиг без установленного файла для загрузки
        """
        yaml_config.config_file = None
        with pytest.raises(ValueError):
            yaml_config.load()

    def test_save_filepath_not_set(self, yaml_config: ConfigYaml):
        """
        ## Описание:
        Попытка сохранить конфиг в файл, который не задан.

        ## Ожидание:
        Ошибка валидации входных данных при вызове метода save().

        ## Входные данные:
        - `yaml_config` - валидный конфиг с конфигурацией бота,
        но не без пути к файлу.
        """
        yaml_config.config_file = None
        with pytest.raises(ValueError):
            yaml_config.save()
        with pytest.raises(ValueError):
            yaml_config.save(None)

    def test_save_load(self, yaml_config: ConfigYaml):
        """
        ## Описание:
        Сохранение конфига в файл, а затем загрузка конфига из этого же
        файла.

        ## Ожидание:
        Данные до сохранения и после загрузки равны.

        ## Входные данные:
        - `yaml_config` - валидный объект с конфигурацией бота
        """
        cfg_old = yaml_config.model_dump_json()
        yaml_config.save()
        yaml_config.load()
        assert yaml_config.model_dump_json() == cfg_old

        yaml_config.users[0].credentials.two_fa = None
        cfg_old = yaml_config.model_dump_json()
        yaml_config.save()
        yaml_config.load()
        assert yaml_config.model_dump_json() == cfg_old
