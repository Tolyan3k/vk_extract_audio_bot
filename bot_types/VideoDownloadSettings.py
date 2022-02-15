from dataclasses import dataclass

@dataclass
class VideoDownloadSettings:
    min_duration: int
    max_duration: int

    max_size: int

    file_name: str
