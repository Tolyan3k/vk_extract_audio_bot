from dataclasses import dataclass
from enum import Enum, IntEnum, auto

from pydantic import (
    NonNegativeInt,
)


@dataclass
class AudioInfo:
    artist: str = ""
    title: str = ""
    lyrics: str = ""
    duration: NonNegativeInt = 0
    is_public: bool = False


@dataclass
class AudioConvertSettings:
    min_duration: int


@dataclass
class VideoDownloadSettings:
    min_duration: int
    max_duration: int
    max_size: int | None
    file_name: str


class VideoPlatform(IntEnum):
    YOUTUBE = auto()
    VK = auto()
    OTHER = auto()


@dataclass
class VideoInfo:
    title: str
    author: str
    platform: VideoPlatform
    duration: int
    is_public: bool = False


class VkVideoPlatform(Enum):
    VK = None
    YOUTUBE = "YouTube"
