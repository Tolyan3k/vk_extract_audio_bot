"""TODO."""

import shutil
from pathlib import Path

import pathvalidate
from pydantic import DirectoryPath

from vk_extract_audio_from_video_bot.services.extra import File
from vk_extract_audio_from_video_bot.services.extractor import AudioExtractor

TEST_DIR = DirectoryPath("./tests/.temp")
shutil.rmtree(TEST_DIR, ignore_errors=True)
TEST_DIR.mkdir(exist_ok=True)    # pylint: disable=no-member

VK_URLS = [
    "https://vk.com/video202745946_456239031?list=5741411ffee8b2bea4",
]

YT_URLS = [
    "https://www.youtube.com/watch?v=cdBK0-9gsFA",
    "https://www.youtube.com/watch?v=mwKJfNYwvm8",
]

RT_URLS = [
    "https://rutube.ru/video/e7929fa8fe0baeff21688ef498c142a4/",
]

ALL_URLS = [
    *VK_URLS,
    *YT_URLS,
    *RT_URLS,
]


class TestExtractor:
    """TODO."""

    def test_free_pass(self) -> None:
        """TODO."""

    class TestUrl:
        """TODO."""

        def test_extract_audio(self) -> None:
            """TODO."""
            for url in ALL_URLS:
                temp = File(
                    dirpath=TEST_DIR,
                    filename=f"video_{pathvalidate.sanitize_filename(url)}",
                )
                to = File(
                    dirpath=TEST_DIR,
                    filename=f"audio_{pathvalidate.sanitize_filename(url)}.mp3",
                )
                af = AudioExtractor.extract_from_url(url, temp, to)
                assert af.audiofile.as_filepath().exists()
                Path.unlink(Path(af.audiofile.get_str()))
