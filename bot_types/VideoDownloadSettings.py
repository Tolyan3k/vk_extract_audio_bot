from dataclasses import dataclass

@dataclass
class VideoDownloadSetting:
    min_duration: int
    max_duration: int

    max_size: int
