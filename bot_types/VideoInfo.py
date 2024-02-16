from dataclasses import dataclass

from bot_types.VideoPlatform import VideoPlatform

@dataclass
class VideoInfo:
    title: str
    author: str
    #link: str
    platform: VideoPlatform
    duration: int
    is_public: bool = False
    #path: None | str
    