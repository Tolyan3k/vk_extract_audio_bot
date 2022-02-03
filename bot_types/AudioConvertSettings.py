from dataclasses import dataclass

@dataclass
class AudioConvertSettings:
    max_bitrate: int
    max_duration: int
    max_size: int