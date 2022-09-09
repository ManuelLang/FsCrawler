import json
from pathlib import Path

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
        props = self.__dict__.copy()
        props['path_type'] = self.path_type.name
        return props

    def __str__(self) -> str:
        return json.dumps(self.to_json())
