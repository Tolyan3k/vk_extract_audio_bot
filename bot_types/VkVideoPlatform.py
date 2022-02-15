from typing import Optional
from enum import Enum

from bot_types.VideoPlatform import VideoPlatform


class VkVideoPlatform(Enum):
    VK = None
    YOUTUBE = "YouTube"


def video_platform_to_vk_video_platform(video_platform: VideoPlatform) -> Optional[VkVideoPlatform]:
    if video_platform == VideoPlatform.VK:
        return VkVideoPlatform.VK
    elif video_platform == VideoPlatform.YOUTUBE:
        return VkVideoPlatform.YOUTUBE
    else:
        return None
