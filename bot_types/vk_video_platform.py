"""TODO
"""

from enum import Enum

from bot_types.video_platform import VideoPlatform


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
    match video_platform:
        case VideoPlatform.VK:
            return VideoPlatform.VK
        case VideoPlatform.YOUTUBE:
            return VkVideoPlatform.YOUTUBE
        case _:
            return None
