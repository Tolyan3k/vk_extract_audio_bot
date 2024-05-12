from pydantic import (
    BaseModel,
    FilePath,
    NewPath,
)


class TmpFileRequest(BaseModel):
    """Запрос для фикстуры `tmp_file` на создание файла."""

    create: bool = True
    delete_after_use: bool = True
    name: str = "file"
    suffix: str = ""

    def __str__(self) -> str:
        return self.name + self.suffix


class TmpFile(BaseModel):
    """Ответ фикстуры `tmp_file` на создание файла."""

    request: TmpFileRequest
    file: FilePath | NewPath

    def __str__(self) -> str:
        return str(self.file)
