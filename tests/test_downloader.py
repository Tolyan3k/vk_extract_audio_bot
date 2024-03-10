"""TODO."""

import shutil
from pathlib import Path

import pathvalidate
from pydantic import DirectoryPath, NewPath

from services.downloader import DownloadedFile, Downloader
from services.extra import File

TEST_DIR = "./tests/.temp"
test_dir = DirectoryPath(TEST_DIR)
shutil.rmtree(test_dir, ignore_errors=True)
test_dir.mkdir()    # pylint: disable=no-member

PUBLIC_URLS = [
    "https://www.youtube.com/watch?v=cdBK0-9gsFA",
    "https://www.youtube.com/watch?v=mwKJfNYwvm8",
]


def is_exists_and_file(filepath: File) -> bool:
    """TODO.

    Args:
    ----
        filepath (File): _description_

    Returns:
    -------
        _type_: _description_

    """
    np = NewPath(f"{filepath}")
    return np.exists() and np.is_file()    # pylint: disable=no-member


class TestYT:
    """TODO."""

    def test_nop(self) -> None:
        """TODO."""

    class TestVideoInfo:
        """TODO."""

        def test_get_info_works(self) -> None:
            """TODO."""
            for url in PUBLIC_URLS:
                Downloader.get_video_info(url)

    class TestLinks:
        """TODO."""

        class TestDownloadOnlyVideo:
            """TODO."""

            def test_downloads(self) -> None:
                """TODO."""
                for url in PUBLIC_URLS:
                    to = File(
                        dirpath=TEST_DIR,
                        filename=pathvalidate.sanitize_filename(url),
                    )
                    dlf = Downloader.download_video(url, to)
                    assert is_exists_and_file(dlf.filepath)
                    Path.unlink(dlf.filepath.get_str())

            def test_is_real_video(self) -> None:
                """TODO."""

        class TestDownloadOnlyAudio:
            """TODO."""

            def test_downloads(self) -> None:
                """TODO."""
                for url in PUBLIC_URLS:
                    to = File(
                        dirpath=TEST_DIR,
                        filename=pathvalidate.sanitize_filename(url),
                    )
                    dlf = Downloader.download_audio(url, to)
                    assert is_exists_and_file(dlf.filepath)
                    Path.unlink(dlf.filepath.get_str())

            def test_is_real_audio(self) -> None:
                """TODO."""

        class TestDownloadAny:
            """TODO."""

            def test_first_audio(self) -> None:
                """Must be only audio."""
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
                    Path.unlink(dlf.filepath.get_str())

            def test_first_video(self) -> None:
                """Must be only video."""
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
                    Path.unlink(dlf.filepath.get_str())
