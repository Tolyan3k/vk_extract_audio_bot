"""TODO
"""

from dataclasses import dataclass


@dataclass
class AudioInfo:
    """TODO"""

    artist: str = ""
    title: str = ""
    lyrics: str = ""
    duration: int = 0
    is_public: bool = False
