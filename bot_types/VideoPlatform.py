from enum import IntEnum, auto
import re

class VideoPlatform(IntEnum):
    YOUTUBE = auto()
    VK = auto()
    RAVE_DJ = auto()
    OTHER = auto()

VK_VIDEO_PATTERN = r"video(?P<vk_owner_id>[-]?\d+)_(?P<vk_video_id>\d+)"
VK_VIDEO_PATTERN_COMPILED = re.compile(VK_VIDEO_PATTERN)

YOUTUBE_VIDEO_PATTERN = r"(?:\/|%3D|v=|vi=)(?P<yt_video_id>[0-9A-z-_]{11})(?:[%#?&\s])"
YOUTUBE_VIDEO_PATTERN_COMPILED = re.compile(YOUTUBE_VIDEO_PATTERN)

VIDEO_PATTERNS = (
    VK_VIDEO_PATTERN, 
    YOUTUBE_VIDEO_PATTERN,
)

VIDEO_PATTERNS_COMPILED = (
    VK_VIDEO_PATTERN_COMPILED,
    YOUTUBE_VIDEO_PATTERN_COMPILED,
)

VIDEO_PATTERNS_COMPILED_WITH_PLATFORMS = (
    (VK_VIDEO_PATTERN_COMPILED, VideoPlatform.VK),
    (YOUTUBE_VIDEO_PATTERN_COMPILED, VideoPlatform.YOUTUBE),
)

VIDEO_PATTERNS_COMPILED_FULL = re.compile(r"|".join(VIDEO_PATTERNS))
