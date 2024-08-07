#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path

from helpers.serializationHelper import JsonDumper
from models.path import PathModel
from models.path_type import PathType


class FileModel(PathModel):
    def __init__(self, root: str, path, size: int = 0) -> None:
        super().__init__(root, path, size)
        if isinstance(path, Path) and not path.is_file():
            raise ValueError(f"The given path is not a valid file: '{path}'")

    @property
    def path_type(self) -> PathType:
        return PathType.FILE

    def to_json(self):
        props = super().to_json()
        props['path_type'] = self.path_type.name
        return props

    def __str__(self) -> str:
        return JsonDumper.dumps(self)
