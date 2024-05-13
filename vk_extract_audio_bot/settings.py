import itertools
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Optional, Self, overload

import pydantic
import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    DirectoryPath,
    Field,
    FilePath,
    NonNegativeInt,
    PositiveInt,
    SecretStr,
    field_serializer,
    model_validator,
    validate_call,
)
from pydantic_settings import BaseSettings


class _Contants(BaseModel):
    model_config = ConfigDict(frozen=True)

    VK_AUDIO_MIN_DURATION: PositiveInt = Field(
        default=5,
        description="Минимальная допустимая длина аудиозаписи в ВК в секундах",
    )
    """
    Минимальная допустимая длина аудиозаписи в ВК в секундах.
    """
    VK_MAX_ATTACHMENTS: PositiveInt = Field(
        default=10,
        description="Максимальное допустимое кол-во вложений в одном сообщении",
    )
    """
    Максимальное допустимое кол-во вложений в одном сообщении.
    """
    VK_MAX_AUDIOFILE_SIZE: PositiveInt = Field(
        default=200 * 10**6,  # 200 МБ
        description="Максимальный допустимый размер аудиозаписи ВК в байтах",
    )
    """
    Максимальный допустимый размер аудиозаписи ВК в байтах.
    """
    VK_VIDEO_MAX_DURATION: PositiveInt = Field(
        default=10 * 3600,  # 10 часов
        description="Максимальная допустимая продолжительность видео в ВК в секундах",
    )
    """
    Максимальная допустимая продолжительность видео в ВК в секундах.
    """


class _Config(BaseSettings):
    class BotWorkDirs(BaseModel):
        class MainWorkDir(BaseSettings):
            DIR: DirectoryPath = Field(
                default=".",
                alias="MAIN_WORK_DIR",
                description="Рабочая директория бота",
            )
            """
            Рабочая директория бота.
            """

        DIRS: Annotated[
            dict[str,str],
            Field(
                default={
                    # Директория для локальной базы данных
                    "data": str(MainWorkDir().DIR) + "/data",
                    # директория для скачивания и хранения видео-файлов
                    # на время обработки сообщения
                    "videos": str(MainWorkDir().DIR) + "/temp/videos",
                    # директория для скачивания и хранения аудио-файлов
                    # на время обработки сообщения
                    "audios": str(MainWorkDir().DIR) + "/temp/audios",
                },
                description="Директории, которые будет использовать бот для работы",
            ),
        ]
        DATA: str = str(MainWorkDir().DIR) + "/data"
        """Директория для локальной базы данных."""

        VIDEOS: str = str(MainWorkDir().DIR) + "/temp/videos"
        """
        Директория для скачивания и хранения видео-файлов
        на время обработки сообщения.
        """

        AUDIOS: str = str(MainWorkDir().DIR) + "/temp/audios"
        """
        Директория для скачивания и хранения аудио-файлов
        на время обработки сообщения.
        """

    VK_USER_ID: str = Field(
        alias="VK_USER_ID",
        description="ID пользователя ВК",
    )
    VK_USER_LOGIN: str = Field(
        alias="VK_USER_LOGIN",
        description="Логин пользователя ВК",
    )
    VK_USER_PASSWORD: str = Field(
        alias="VK_USER_PASSWORD",
        description="Пароль пользователя ВК",
    )
    VK_USER_TOKEN: str = Field(
        alias="VK_USER_TOKEN",
        description="Токен доступа пользователя ВК для работы с API",
    )
    VK_USER_2FA: str = Field(
        alias="VK_USER_2FA",
        description="Код, который генерируется при подключении 2FA",
    )
    vk_audio_client_token: str | None = Field(
        default=None,
        alias="VK_AUDIO_CLIENT_TOKEN",
        description=(
            "Токен для клиента ВК с поддержкой аудио для юзера"
        ),
    )
    VK_ARCHIVE_GROUP_ID: PositiveInt = Field(
        alias="VK_ARCHIVE_GROUP_ID",
        description=(
            "ID архивной группы, которая используется для хранения"
            " аудиозаписей и других служебных вещей"
        ),
    )
    VK_ARCHIVE_GROUP_TOKEN: str = Field(
        alias="VK_ARCHIVE_GROUP_TOKEN",
        description=(
            "Токен архивной группы, которая используется для хранения"
            " аудиозаписей и других служебных вещей"
        ),
    )
    VK_MAIN_GROUP_ID: PositiveInt = Field(
        alias="VK_MAIN_GROUP_ID",
        description=(
            "ID группы, которая предназначена для работы с пользователями"
        ),
    )
    VK_MAIN_GROUP_TOKEN: str = Field(
        alias="VK_MAIN_GROUP_TOKEN",
        description=(
            "Токен группы, которая предназначена для работы с пользователями"
        ),
    )
    VK_MAIN_GROUP_URL: str = Field(
        default="https://vk.com/convert_to_audio",
        alias="VK_MAIN_GROUP_URL",
        description=(
            "Подпись, которая будет использоваться при загрузке аудиозаписей"
            " в ВК"
        ),
    )
    VK_AUDIO_CLIENT_SECRET: str = Field(
        default="hHbZxrka2uZ6jB1inYsH", # VK OFFICIAL ANDROID CLIENT
        alias="VK_AUDIO_CLIENT_SECRET",
        description=(
            "Секретный код, который выдаётся при регистрации приложения ВК"
        ),
    )
    MAIN_WORK_DIR: DirectoryPath = Field(
        default=BotWorkDirs.MainWorkDir().DIR,
        description="Рабочая директория бота",
    )
    BOT_WORK_DIRS: Annotated[
        dict[str, str],
        Field(
            default=BotWorkDirs().DIRS,
            description="Директории, которые будет использовать бот для работы",
        ),
    ]
    DB_URL: str = Field(
        default=f"sqlite:///{BotWorkDirs().DIRS["data"]}/database.db",
        alias="DB_URL",
        description="URL для доступа к базе данных",
    )

    VIDEO_MIN_DURATION: NonNegativeInt = Field(
        default=0,
        alias="VIDEO_MIN_DURATION",
        description=(
            "Минимальная допустимая длина видео в секундах,"
            " которое должен обработать бот"
        ),
    )
    """
    P.S.  Никогда не ставил больше `0`,
    так что хз, как бот с работает этим параметром
    """

    VIDEO_MAX_DURATION: PositiveInt = Field(
        default=1800,
        le=_Contants().VK_VIDEO_MAX_DURATION,
        alias="VIDEO_MAX_DURATION",
        description=(
            "Максимальная допустимая длина видео в секундах,"
            " которое должен обработать бот"
        ),
    )
    """
    P.S.  В теории ограничено лишь `VK_VIDEO_MAX_DURATION`,
    но т.к. бот пока не умеет занижать битрейт аудио,
    то также ограничено `VK_MAX_AUDIOFILE_SIZE`.
    Остальное ограничивается возможностями сервера
    """

    MSG_PROCCESSING_DELAY: NonNegativeInt = Field(
        default=5,
        alias="MSG_PROCCESSING_DELAY",
        description="Задержка в секундах перед началом обработки сообщения",
    )
    """
    Задержка в секундах перед началом обработки сообщения.

    PS.   Нужна, чтобы при отправлении сообщения с ссылкой на видео
    успело прогрузиться и вложение с этим видео.
    Выбирать меньше `5` не рекомендуется.
    """

    WORKER_COUNT: PositiveInt = Field(
        default=1,
        alias="WORKER_COUNT",
        description=(
            "Максимальное кол-во воркеров, которые будут заниматься"
            " скачиванием видео и их конвертацией"
        ),
    )
    """
    Максимальное кол-во воркеров, которые будут заниматься
    скачиванием видео и их конвертацией.

    PS.   Ограничено лишь возможностями сервера (память, интернет, CPU).
    """

class ConfigYamlSettings(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        validate_assignment=True,
    )

    class WorkDirs(BaseModel):
        model_config = ConfigDict(
            validate_default=True,
            validate_assignment=True,
        )

        main: Path = Field(
            # pylint: disable=E1101
            default=".",
            description="Рабочая директория бота",
        )
        """
        Основная рабочая директория бота.
        По умолчанию все остальные директории создаются в этой.
        """

        data: Path = Field(
            default="./data",
            description="Директория для локальной базы данных",
        )
        """Директория для локальной базы данных."""

        videos: Path = Field(
            default="./temp/videos",
        )
        """
        Директория для скачивания и хранения видео-файлов
        на время обработки сообщения.
        """

        audios: Path = Field(
            default="./temp/audios",
        )
        """
        Директория для скачивания и хранения аудио-файлов
        на время обработки сообщения.
        """

        @model_validator(mode="after")
        def fix_paths(self) -> Self:
            if self.main != Path():
                if self.data == Path("./data"):
                    self.data = f"{self.main}/data"
                if self.videos == Path("./temp/videos"):
                    self.videos = Path(f"{self.main}/temp/videos")
                if self.audios == Path("./temp/audios"):
                    self.audios = Path(f"{self.main}/temp/audios")
            return self

        @model_validator(mode="after")
        def check_path_not_files(self) -> Self:
            for dir_name, path in dict(self).items():
                path: Path
                if path.exists() and path.is_file():
                    msg = f"'{dir_name}' must point to directory: '{path}'"
                    raise ValueError(msg)
            return self

    work_dirs: WorkDirs = Field(
        default=WorkDirs(),
        description="Директории, которые будет использовать бот для работы",
    )
    """Директории, которые будет использовать бот для работы."""

    msg_processing_delay: NonNegativeInt = Field(
        default=5,
        alias="msg_processing_delay",
        description="Задержка в секундах перед началом обработки сообщения",
    )
    """
    PS.   Нужна, чтобы при отправлении сообщения с ссылкой на видео
    успело прогрузиться и вложение с этим видео.
    Выбирать меньше `5` не рекомендуется
    """

    worker_count: PositiveInt = Field(
        default=1,
        alias="worker_count",
        description=(
            "Максимальное кол-во воркеров, которые будут заниматься"
            " скачиванием видео и их конвертацией"
        ),
    )
    """
    Максимальное кол-во воркеров, которые будут заниматься
    скачиванием видео и их конвертацией

    PS.   Ограничено лишь возможностями сервера (память, интернет, CPU)
    """

    db_url: SecretStr = Field(
        default=f"sqlite:///{WorkDirs().data}/database.db",
        alias="db_url",
        description="URL для доступа к базе данных",
        min_length=1,
    )
    """URL для доступа к базе данных."""

    video_min_duration: NonNegativeInt = Field(
        default=0,
        alias="video_min_duration",
        description=(
            "Минимальная допустимая длина видео в секундах,"
            " которое должен обработать бот"
        ),
    )
    """
    Минимальная допустимая длина видео в секундах,
    которое должен обработать бот.

    P.S.  Никогда не ставил больше `0`,
    так что хз, как бот с работает этим параметром
    """

    video_max_duration: PositiveInt = Field(
        default=1800,
        le=_Contants().VK_VIDEO_MAX_DURATION,
        alias="video_max_duration",
        description=(
            "Максимальная допустимая длина видео в секундах,"
            " которое должен обработать бот"
        ),
    )
    """
    Максимальная допустимая длина видео в секундах,
    которое должен обработать бот.

    P.S.  В теории ограничено лишь `VK_VIDEO_MAX_DURATION`,
    но т.к. бот пока не умеет занижать битрейт аудио,
    то также ограничено `VK_MAX_AUDIOFILE_SIZE`.
    Остальное ограничивается возможностями сервера
    """

    @pydantic.model_validator(mode="after")
    def check_video_min_dur_le_video_max_dur(self) -> Self:
        if self.video_min_duration > self.video_max_duration:
            msg = "'video_min_duration' must be less or equal 'video_max_duration'"
            raise ValueError(msg)
        return self

    @field_serializer("db_url", when_used="json")
    def db_url_secret_value(db_url: SecretStr) -> str:
        # ruff: noqa: N805
        # pylint: disable=E0213
        return db_url.get_secret_value()

class ConfigYamlGroup(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        validate_assignment=True,
    )

    type: "Type" = Field(
        description=(
            "Тип группы: для работы с пользователями (main) или"
            " для хранения аудиозаписей и управления (archive)"
        ),
    )
    """
    Тип группы: для работы с пользователями (`main`) или
    для хранения аудиозаписей и управления (`archive`).
    """

    id: PositiveInt = Field(
        description="ID группы",
    )
    """
    ID группы.
    """

    tokens: set[SecretStr] = Field(
        description="Список токенов для работы с группой",
        min_length=1,
    )
    """
    Список токенов для работы с группой.
    """

    @field_serializer("tokens", when_used="json")
    def password_secret_value(tokens: set[SecretStr]) -> set[str]:
        # ruff: noqa: N805
        # pylint: disable=E0213
        return {t.get_secret_value() for t in tokens}

    class Type(StrEnum):
        MAIN = "main"
        """
        Основная (`main`) группа.

        Предназначена для работы с пользователям.
        """
        ARCHIVE = "archive"
        """
        Архивная (`archive`) группа.

        Предназначена для хранения аудиозаписей и административных нужд.
        """

class ConfigYamlUser(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        validate_assignment=True,
    )

    id: PositiveInt = Field(
        description="ID пользователя ВК",
    )
    """ID пользователя ВК."""

    token: SecretStr = Field(
        description="Токен доступа пользователя ВК для работы с API",
        min_length=1,
    )
    """Токен доступа пользователя ВК для работы с API."""

    credentials: Optional["Credentials"] = Field(
        default=None,
        description="",
    )
    """TODO."""

    audio_client: Optional["AudioClient"] = Field(
        default=None,
        description="",
    )
    """TODO."""

    @model_validator(mode="after")
    def check_at_least_credentials_or_audio_client(self) -> Self:
        if self.credentials or self.audio_client:
            return self
        raise ValueError

    class Credentials(BaseModel):
        model_config = ConfigDict(
            validate_default=True,
            validate_assignment=True,
        )

        login: str = Field(
            coerce_numbers_to_str=True,
            description="Логин пользователя ВК",
            min_length=1,
        )
        """Логин пользователя ВК."""

        password: SecretStr = Field(
            description="Пароль пользователя ВК",
            min_length=1,
        )
        """Пароль пользователя ВК."""

        two_fa: SecretStr | None = Field(
            default=None,
            alias="2fa",
            description="Код, который генерируется при подключении 2FA",
            min_length=1,
        )
        """Код, который генерируется при подключении 2FA."""

        @field_serializer("password", when_used="json")
        def password_secret_value(password: SecretStr) -> str:
            # ruff: noqa: N805
            # pylint: disable=E0213
            return password.get_secret_value()

        @field_serializer("two_fa", when_used="json")
        def two_fa_secret_value(two_fa: SecretStr | None) -> str | None:
            # ruff: noqa: N805
            # pylint: disable=E0213
            if two_fa is not None:
                return two_fa.get_secret_value()
            return None

    @field_serializer("token", when_used="json")
    def two_fa_secret_value(token: SecretStr) -> str:
        # ruff: noqa: N805
        # pylint: disable=E0213
        return token.get_secret_value()

    class AudioClient(BaseModel):
        model_config = ConfigDict(
            validate_default=True,
            validate_assignment=True,
        )
        secret: SecretStr = Field(
            default="hHbZxrka2uZ6jB1inYsH", # VK OFFICIAL ANDROID CLIENT
            description=(
                "Секретный код, который выдаётся при регистрации приложения ВК"
            ),
            min_length=1,
        )
        """Секретный код, который выдаётся при регистрации приложения ВК."""

        token: SecretStr = Field(
            description="Токен клиента ВК с поддержкой аудио для юзера",
            min_length=1,
        )
        """Токен клиента ВК с поддержкой аудио для юзера."""

        @field_serializer("secret", when_used="json")
        def secret_secret_value(secret: SecretStr) -> str:
            # ruff: noqa: N805
            # pylint: disable=E0213
            return secret.get_secret_value()

        @field_serializer("token", when_used="json")
        def token_secret_value(token: SecretStr) -> str:
            # ruff: noqa: N805
            # pylint: disable=E0213
            return token.get_secret_value()

class ConfigYaml(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        validate_assignment=True,
    )

    settings: ConfigYamlSettings = Field(
        default=ConfigYamlSettings(),
        description="",
    )
    """"""

    groups: list[ConfigYamlGroup] = Field(
        description="Группы ВК, с которыми работает бот",
        min_length=2,
    )
    """Группы ВК, с которыми работает бот."""

    users: list[ConfigYamlUser] = Field(
        description="Пользователи ВК для работы с аудиозаписями",
        min_length=1,
    )
    """
    Пользователи ВК для работы с аудиозаписями.

    Только загрузка аудиозаписей в ВК и добавление в архивную группу.
    """

    config_file: FilePath | None = Field(
        default=None,
        exclude=True,
        description="YAML-файл, в который будет сохраняться конфиг по умолчанию",
    )
    """YAML-файл, в который будет сохраняться конфиг по умолчанию."""

    def load(self) -> Self:
        if self.config_file is None:
            msg = "Config file is not set"
            raise ValueError(msg)
        new_cfg = load_yaml_config(self.config_file)
        self.groups = new_cfg.groups
        self.settings = new_cfg.settings
        self.users = new_cfg.users
        self.config_file = new_cfg.config_file
        return self

    @overload
    def save(self) -> None:
        ...

    @overload
    def save(self, file: FilePath) -> None:
        ...

    @validate_call
    def save(self, file: FilePath | None = None) -> None:
        out_f = (self.config_file, file)[file is not None]
        if out_f is None:
            msg = "Save filepath not set"
            raise ValueError(msg)
        with out_f.open("w", encoding="utf-8") as wf:
            yaml.safe_dump(self.model_dump(mode="json", by_alias=True), wf)


    @model_validator(mode="after")
    def check_groups_at_least_archive_and_main_type(self) -> Self:
        check_group_types = {
            ConfigYamlGroup.Type.ARCHIVE, ConfigYamlGroup.Type.MAIN,
        }
        self_group_types = {g.type for g in self.groups}
        if check_group_types == self_group_types:
            return self
        msg = "Need at least one 'main' and 'archive' group"
        raise ValueError(msg)

    @model_validator(mode="after")
    def try_unite_users_with_same_id(self) -> Self:
        users_grouped_by_id: list[list[ConfigYamlUser]] = [
            list(g)
            for _, g
            in itertools.groupby(
                sorted(self.users, key=lambda u: u.id),
                lambda u: u.id,
            )
        ]
        if len(users_grouped_by_id) == len(self.users):
            return self
        users_all_in_one_per_id = []
        for users in users_grouped_by_id:
            if len(users) == 1:
                users_all_in_one_per_id.extend(users)
                continue
            user_all_in_one = {}
            for u1, u2 in itertools.combinations(users, 2):
                # ruff: noqa: PLW2901
                u1 = u1.model_dump(mode="json", by_alias=True)
                u2 = u2.model_dump(mode="json", by_alias=True)
                for key in u1:
                    if all([u1[key], u2[key]]) and u1[key] != u2[key]:
                        msg = f"Users {u1} and {u2} have different values in '{key}'"
                        raise ValueError(msg)
                    user_all_in_one[key] = (u1[key], u2[key])[u2[key] is not None]
            users_all_in_one_per_id.append(ConfigYamlUser.model_validate(user_all_in_one))
        self.users = users_all_in_one_per_id
        return self

    @model_validator(mode="after")
    def unite_groups_with_same_id_and_type(self) -> Self:
        groups_groups: list[list[ConfigYamlGroup]] = [
            list(g)
            for _, g
            in itertools.groupby(
                sorted(self.groups, key=lambda g: (g.id, g.type)),
                lambda g: (g.id, g.type),
            )
        ]
        if len(self.groups) == len(groups_groups):
            return self
        groups_united = []
        for groups_g in groups_groups:
            group_united = groups_g.pop()
            for group in groups_g:
                group_united.tokens = group_united.tokens.union(group.tokens)
            groups_united.append(group_united)
        self.groups = groups_united
        return self

@validate_call
def load_yaml_config(file: FilePath) -> ConfigYaml:
    with file.open("r", encoding="utf-8") as f:
        config = ConfigYaml.model_validate(yaml.safe_load(f))
        config.config_file = file
        return config

class ConfigEnv(BaseSettings):
    yaml_config_file: FilePath = Field(
        alias="CONFIG",
        description="YAML-файл с конфигурацией бота",
    )
    """YAML-файл с конфигурацией бота."""

CONSTANTS = _Contants()
CONFIG = _Config()

__all__ = [
    "CONSTANTS",
    "CONFIG",
]
