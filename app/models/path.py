from abc import ABC
from pathlib import Path

from models.path_type import PathType


class PathModel(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'path_type') and
                callable(subclass.path_type)
                )

    def __init__(self, path: Path, size_in_mb: int = 0) -> None:
        super().__init__()
        if not path:
            raise ValueError("The path is mandatory")
        if not path.exists():
            raise ValueError(f"The given path does not exists: '{path}'")

        self.path: str = str(path)
        self.extension: str = path.suffix
        self.name: str = path.stem
        self.owner: str = path.owner()
        self.group: str = path.group()
        self.root: str = path.root
        self.drive: str = path.drive
        self.size_in_mb: int = size_in_mb
        self.hash_md5: str = ''
        self.hash_sha256: str = ''
        self.is_windows_path: bool = False
        self.hidden: bool = False
        self.archive: bool = False
        self.compressed: bool = False
        self.encrypted: bool = False
        self.offline: bool = False
        self.readonly: bool = False
        self.system: bool = False
        self.temporary: bool = False

    @property
    def path_type(self) -> PathType:
        raise NotImplementedError()

    def to_json(self):
        return self.__dict__.copy()
