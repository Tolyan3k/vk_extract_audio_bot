from pydantic import BaseModel, Field, DirectoryPath, FilePath, NewPath, ValidationInfo
from pydantic import field_validator, model_validator

import pathvalidate

from loguru import logger

class_config = dict(
    validate_assignment=True,
)

class File(BaseModel, **class_config):
    dirpath: DirectoryPath
    filename: str
    
    def get_str(self) -> str:
        filepath = rf'{self.dirpath}/{self.filename}'
        logger.debug(filepath)
        return filepath
    
    def as_filepath(cls) -> FilePath:
        return FilePath(f'{cls}')
    
    def __str__(self) -> str:
        return self.get_str()
        
    @field_validator('filename')
    @classmethod
    def check_filename(cls, filename: str, info: ValidationInfo) -> str:
        logger.debug(f'Got args: {locals()}')
        filename = filename.strip()
        pathvalidate.validate_filename(filename)
        return filename
    
    @model_validator(mode='after')
    def check_filepath(self) -> 'File':
        filepath = NewPath(self.get_str())
        logger.debug(f'Checking is filepath exists and file: {filepath}')
        if filepath.exists() and not filepath.is_file():
            raise ValueError('Existing filepath points not to file')
        logger.debug(f'Checking filepath valid')
        pathvalidate.validate_filepath(filepath)
        return self
    
    
