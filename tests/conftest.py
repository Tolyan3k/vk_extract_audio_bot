from collections.abc import Generator
from pathlib import Path

import pytest

from .fixture_types import (
    TmpFile,
    TmpFileRequest,
)


@pytest.fixture()
def tmp_file(
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> Generator[TmpFile]:
    """Фикстура для создания временного файла."""
    tmp_file_req: TmpFileRequest = TmpFileRequest()
    if hasattr(request, "param"):
        tmp_file_req = request.param
    file = tmp_path / str(tmp_file_req)
    if tmp_file_req.create:
        file.touch()
    yield TmpFile(request=tmp_file_req, file=file)
    if tmp_file_req.delete_after_use:
        file.unlink(missing_ok=True)
