from pathlib import Path

from helpers.serializationHelper import JsonDumper
from models.path import PathModel
from models.path_type import PathType


class DirectoryModel(PathModel):
    def __init__(self, path: Path, size_in_mb: int = 0) -> None:
        super().__init__(path, size_in_mb)

        if not path.is_dir():
            raise ValueError(f"The given path is not a file: '{path}'")

    @property
    def path_type(self) -> PathType:
        return PathType.DIRECTORY

    def to_json(self):
        props = super().to_json()
        props['path_type'] = self.path_type.name
        return props

    def __str__(self) -> str:
        return JsonDumper.dumps(self)
