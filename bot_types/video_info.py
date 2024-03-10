"""TODO."""

from dataclasses import dataclass

from bot_types.video_platform import VideoPlatform


@dataclass
class VideoInfo:
    """TODO."""

    title: str
    author: str
    # link: str
    platform: VideoPlatform
    duration: int
    is_public: bool = False
    # path: None | str
