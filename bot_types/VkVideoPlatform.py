"""TODO
"""

from enum import Enum

from bot_types.VideoPlatform import VideoPlatform


class VkVideoPlatform(Enum):
    """TODO

    Args:
    ----
        Enum (_type_): _description_

    """

    VK = None
    YOUTUBE = "YouTube"


def video_platform_to_vk_video_platform(
    video_platform: VideoPlatform,
) -> VkVideoPlatform | None:
    """TODO

    Args:
    ----
        video_platform (VideoPlatform): _description_

    Returns:
    -------
        Optional[VkVideoPlatform]: _description_

    """
    if video_platform == VideoPlatform.VK:
        return VkVideoPlatform.VK
    elif video_platform == VideoPlatform.YOUTUBE:
        return VkVideoPlatform.YOUTUBE
    else:
        return None
