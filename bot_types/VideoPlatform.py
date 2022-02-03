from enum import IntEnum, auto
import re


class VideoPlatform(IntEnum):
    YOUTUBE = auto()
    VK = auto()
    RAVE_DJ = auto()
    OTHER = auto()


def get_video_platform(url_link: str) -> VideoPlatform:
    youtube_pattern = re.compile(r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$")
    vk_pattern = re.compile("")