"""TODO
"""

import os
import shutil

import pathvalidate
from pydantic import DirectoryPath, NewPath

from services.downloader import DownloadedFile, Downloader
from services.extra import File


TEST_DIR = "./tests/.temp"
test_dir = DirectoryPath(TEST_DIR)
shutil.rmtree(test_dir, ignore_errors=True)
test_dir.mkdir()    # pylint: disable=no-member

PUBLIC_URLS = [
    # 'https://youtu.be/5jfPeClZF8M',
    # 'https://www.youtube.com/watch?v=mwKJfNYwvm800', # multiple dub tracks
    # 'https://www.youtube.com/watch?v=Do5_wU9X1pc&t=15s',
    "https://www.youtube.com/watch?v=cdBK0-9gsFA",
    "https://www.youtube.com/watch?v=mwKJfNYwvm8",
    # "https://www.youtube.com/watch?v=biYFsy1s2t0",
]


def is_exists_and_file(filepath: File):
    """TODO

    Args:
        filepath (File): _description_

    Returns:
        _type_: _description_
    """
    np = NewPath(f"{filepath}")
    return np.exists() and np.is_file()    # pylint: disable=no-member


class TestYT:
    """TODO"""

    def test_nop(self):
        """TODO"""

    class TestVideoInfo:
        """TODO"""

        def test_get_info_works(self):
            """TODO"""
            for url in PUBLIC_URLS:
                Downloader.get_video_info(url)

    class TestLinks:
        """TODO"""

        class TestDownloadOnlyVideo:
            """TODO"""

            def test_downloads(self):
                """TODO"""
                for url in PUBLIC_URLS:
                    to = File(
                        dirpath=TEST_DIR,
                        filename=pathvalidate.sanitize_filename(url),
                    )
                    dlf = Downloader.download_video(url, to)
                    assert is_exists_and_file(dlf.filepath)
                    os.remove(dlf.filepath.get_str())

            def test_is_real_video(self):
                """TODO"""

        class TestDownloadOnlyAudio:
            """TODO"""

            def test_downloads(self):
                """TODO"""
                for url in PUBLIC_URLS:
                    to = File(
                        dirpath=TEST_DIR,
                        filename=pathvalidate.sanitize_filename(url),
                    )
                    dlf = Downloader.download_audio(url, to)
                    assert is_exists_and_file(dlf.filepath)
                    os.remove(dlf.filepath.get_str())

            def test_is_real_audio(self):
                """TODO"""

        class TestDownloadAny:
            """TODO"""

            def test_first_audio(self):
                """Must be only audio"""
                for url in PUBLIC_URLS:
                    to = File(
                        dirpath=TEST_DIR,
                        filename=pathvalidate.sanitize_filename(url),
                    )
                    dlf = Downloader.download_any(
                        url,
                        to,
                        DownloadedFile.Type.AUDIO,
                    )
                    assert is_exists_and_file(dlf.filepath)
                    os.remove(dlf.filepath.get_str())

            def test_first_video(self):
                """Must be only video"""
                for url in PUBLIC_URLS:
                    to = File(
                        dirpath=TEST_DIR,
                        filename=pathvalidate.sanitize_filename(url),
                    )
                    dlf = Downloader.download_any(
                        url,
                        to,
                        DownloadedFile.Type.VIDEO,
                    )
                    assert is_exists_and_file(dlf.filepath)
                    os.remove(dlf.filepath.get_str())
