"""TODO."""

import pathvalidate
from loguru import logger
from pydantic import (
    BaseModel,
    DirectoryPath,
    FilePath,
    NewPath,
    ValidationInfo,
    field_validator,
    model_validator,
)

class_config = {
    "validate_assignment": True,
}


class File(BaseModel, **class_config):
    """TODO.

    Args:
    ----
        BaseModel (_type_): _description_

    Raises:
    ------
        ValueError: _description_

    Returns:
    -------
        _type_: _description_

    """

    dirpath: DirectoryPath
    filename: str

    def get_str(self) -> str:
        """TODO.

        Returns
        -------
            str: _description_

        """
        filepath = rf"{self.dirpath}/{self.filename}"
        logger.debug(filepath)
        return filepath

    def as_filepath(self) -> FilePath:
        """TODO.

        Returns
        -------
            FilePath: _description_

        """
        return FilePath(f"{self}")

    def __str__(self) -> str:
        return self.get_str()

    @field_validator("filename")
    @classmethod
    def check_filename(cls, filename: str, _: ValidationInfo) -> str:
        # ruff: noqa: ANN102
        """TODO.

        Args:
        ----
            filename (str): _description_
            info (ValidationInfo): _description_

        Returns:
        -------
            str: _description_

        """
        logger.debug(f"Got args: {locals()}")
        filename = filename.strip()
        pathvalidate.validate_filename(filename)
        return filename

    @model_validator(mode="after")
    def check_filepath(self) -> "File":
        """TODO.

        Raises
        ------
            ValueError: _description_

        Returns
        -------
            File: _description_

        """
        filepath = NewPath(self.get_str())
        logger.debug(f"Checking is filepath exists and file: {filepath}")
        if filepath.exists() and not filepath.is_file():    # pylint: disable=no-member
            msg = "Existing filepath points not to file"
            raise ValueError(msg)
        logger.debug("Checking filepath valid")
        pathvalidate.validate_filepath(filepath)
        return self
