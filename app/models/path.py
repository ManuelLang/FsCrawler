#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import os
from abc import ABC
from pathlib import Path
from typing import Dict

from models.content import ContentFamily
from models.path_stage import PathStage
from models.path_type import PathType


class PathModel(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'path_type') and
                callable(subclass.path_type))

    def __init__(self, root: str, path, size_in_mb: int = 0) -> None:
        super().__init__()
        if not path:
            raise ValueError("The path is mandatory")
        if not isinstance(path, Path):
            path = Path(path)
        self.path: Path = path
        self._full_path: str = str(path)

        self.id: int = 0
        self.path_root: str = root
        start_index = self._full_path.find(root)
        self.relative_path: str = self._full_path[start_index + len(root) - 1:] \
            if start_index >= 0 and len(root) > 0 \
            else self._full_path
        if self.relative_path and len(self.relative_path) > 0 and self.relative_path[0] == '/':
            self.relative_path = self.relative_path[1:]

        self.extension: str = ''
        parts = self._full_path.split('/')
        parts.reverse()
        file_name = parts[0] if parts else None
        if file_name and '.' in file_name:
            file_parts = file_name.split('.')
            file_parts.reverse()
            self.extension = file_parts[0]
        self.size_in_mb: int = size_in_mb

        if path.exists():
            self.name: str = path.stem
            self.owner: str = path.owner()
            self.group: str = path.group()
            self.root: str = path.root
            self.drive: str = path.drive
            self.status = 'CURRENT'
        else:
            self.name: str = ''
            self.owner: str = ''
            self.group: str = ''
            self.root: str = ''
            self.drive: str = ''
            self.status = 'DELETED'
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
        self._tags: Dict[str, str] = {}  # For finder tags: <Label_Name, Color_name>

    @property
    def path_type(self) -> PathType:
        if self.path:
            if self.path.is_file():
                return PathType.FILE
            elif self.path.is_dir():
                return PathType.DIRECTORY
        raise NotImplementedError()

    @property
    def tags(self) -> Dict[str, str]:  # For finder tags: <Label_Name, Color_name>
        return self._tags

    @property
    def full_path(self) -> str:
        # _full_path = os.path.join(self.path_root, self.relative_path)
        # return _full_path
        return self._full_path

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

    @staticmethod
    def from_dict(values: dict):
        path = values.get('path', '')
        root = values.get('root', '')
        if not path:
            return None
        path_model: PathModel = PathModel(root=root, path=path)
        return path_model

    def to_json(self):
        props = self.__dict__.copy()
        props['path_stage'] = self.path_stage.name
        return props
