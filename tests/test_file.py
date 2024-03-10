"""TODO."""

import shutil
from pathlib import Path

import pytest
from pydantic import DirectoryPath, NewPath

from services.extra import File

TEST_DIR = DirectoryPath("./tests/.temp")
shutil.rmtree(TEST_DIR, ignore_errors=True)
TEST_DIR.mkdir(exist_ok=True)    # pylint: disable=no-member


def create_and_delete_file(filepath: str) -> None:
    """TODO.

    Args:
    ----
        filepath (str): _description_

    """
    np = NewPath(filepath)
    np.touch()    # pylint: disable=no-member
    Path.unlink(np)


class TestFile:
    """TODO."""

    def test_nop(self) -> None:
        """TODO."""

    def test_filename_with_spaces(self) -> None:
        """TODO."""
        f = File(dirpath="", filename="some file.txt")
        create_and_delete_file(f.get_str())

    def test_valid_file(self) -> None:
        """TODO."""
        f = File(dirpath="", filename="good_file_name.txt")
        create_and_delete_file(f.get_str())

    def test_empty_filename(self) -> None:
        """TODO."""
        with pytest.raises(Exception):
            File(dirpath=".", filename="")

    def test_not_exisiting_dirpath(self) -> None:
        """TODO."""
        with pytest.raises(Exception):
            File(dirpath="not-existsing-dirpath", filename="filename")

    def test_filepath_points_to_dir(self) -> None:
        """TODO."""
        with pytest.raises(Exception):
            File(dirpath="tests", filename=".temp")

    def test_filename_deprecated_chars(self) -> None:
        """TODO."""
        with pytest.raises(Exception):
            File(dirpath="", filename="!@#$%^&*()?_.txt")

    def test_filename_has_dir(self) -> None:
        """TODO."""
        with pytest.raises(Exception):
            File(dirpath="", filename="tests/file.txt")

    def test_change_valid_filename_to_another(self) -> None:
        """TODO."""
        f = File(dirpath="", filename="valid filename")
        # with pytest.raises(Exception):
        f.filename = "another valid filename"

    def test_change_valid_dirpath_to_another(self) -> None:
        """TODO."""
        f = File(dirpath="", filename="filename")
        f.dirpath = "./tests"

    def test_change_valid_dirpath_to_invalid(self) -> None:
        """TODO."""
        f = File(dirpath="", filename="filename")
        with pytest.raises(Exception):
            f.dirpath = "!@#$%^&*()?_.txt"

    def test_change_valid_filename_to_invalid(self) -> None:
        """TODO."""
        f = File(dirpath="", filename="valid filename")
        with pytest.raises(Exception):
            f.filename = "!@#$%^&*()?_.txt"

    def test_str_eq_get_str(self) -> None:
        """TODO."""
        f = File(dirpath="", filename="filename")
        assert f"{f}" == f.get_str()

    def test_filepath_on_not_existing_file(self) -> None:
        """TODO."""
        f = File(dirpath="", filename="filename")
        f.as_filepath()

    def test_filepath_on_existing_file(self) -> None:
        """TODO."""
        f = File(dirpath="", filename="filename")
        np = NewPath(f"{f}")
        np.touch()    # pylint: disable=no-member
        f.as_filepath()
        Path.unlink(f"{np}")
