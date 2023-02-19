from abc import ABC
from pathlib import Path

from models.content import ContentFamily
from models.path_stage import PathStage
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
        self.content_family: str = ''
        self.mime_type: str = ''
        self.path_stage: PathStage = PathStage.CRAWLED  # if an instance of path is created, it means it was crawled

    @property
    def path_type(self) -> PathType:
        raise NotImplementedError()

    @staticmethod
    def get_content_familiy_from_mime_type(mime_type: str):
        if not mime_type:
            return None
        if mime_type.startswith('audio') or 'music' in mime_type:
            return ContentFamily.MUSIC
        if mime_type.startswith('video'):
            return ContentFamily.VIDEO
        if mime_type.startswith('image'):
            return ContentFamily.PICTURE
        if mime_type.startswith('message') \
                or mime_type.startswith('text') \
                or (mime_type.startswith('application/')
                    and ('word' in mime_type
                         or 'excel' in mime_type
                         or 'powerpoint' in mime_type
                         or 'office' in mime_type
                         or 'openxmlformats-officedocument' in mime_type
                         or 'spreadsheet' in mime_type
                         or 'visio' in mime_type
                         or 'x-tika-msworks' in mime_type
                         or 'x-tika-ooxml' in mime_type
                         or 'pdf' in mime_type
                         or 'onenote' in mime_type
                    )
        ):
            return ContentFamily.DOCUMENT
        if mime_type.startswith('application/') and (
                'x-tar' in mime_type
                or 'zip' in mime_type
                or 'rar' in mime_type
                or 'tar' in mime_type
                or '7z' in mime_type
                or 'archive' in mime_type
                or 'compressed' in mime_type
        ):
            return ContentFamily.ARCHIVE
        return ContentFamily.APPLICATION

    def to_json(self):
        props = self.__dict__.copy()
        props['path_stage'] = self.path_stage.name
        return props
