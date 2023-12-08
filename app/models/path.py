#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict
from loguru import logger
import re

from models.content import ContentFamily
from models.path_stage import PathStage
from models.path_type import PathType

from app.models.rating import Rating


class PathModel(ABC):
    FILE_EXTENSION_PATTERN = re.compile("[a-z0-9_]{2,12}", re.IGNORECASE)

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'path_type') and
                callable(subclass.path_type))

    def __init__(self, root: str, path: str | Path, size: int = 0, files_in_dir: int = 0) -> None:
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

        self.extension: str = None
        self.size: int = size
        self.create_time = None
        self.modify_time = None

        if self.path:
            self.extension = self.get_extension(self.path)

        self._path_type: PathType = None
        if self.path and path.exists():

            if self.path.is_file():
                self._path_type = PathType.FILE
            elif self.path.is_dir():
                self._path_type = PathType.DIRECTORY

            self.name: str = path.stem
            try:
                self.owner: str = path.owner()
                self.group: str = path.group()
            except Exception as ex:
                logger.debug(f"Unable to get file ownership for {path}. Error: {ex}")
                self.owner: str = None
                self.group: str = None
            self.root: str = path.root
            self.drive: str = path.drive
            self.status = 'CURRENT'
        else:
            self.name: str = None
            self.owner: str = None
            self.group: str = None
            self.root: str = None
            self.drive: str = None
            self.status = 'DELETED'

        self.file_name: str = None
        if self._path_type == PathType.FILE:
            self.file_name = f"{self.name}{self.extension}"
        self.hash: str = None
        self.is_windows_path: bool = False
        self.hidden: bool = False
        self.archive: bool = False
        self.compressed: bool = False
        self.encrypted: bool = False
        self.offline: bool = False
        self.readonly: bool = False
        self.system: bool = False
        self.temporary: bool = False
        self.content_family: ContentFamily = None
        self.content_rating: Rating = None
        self.mime_type: str = None
        self.path_stage: PathStage = PathStage.CRAWLED  # if an instance of path is created, it means it was crawled
        self.keywords: str = None
        self._tags: Dict[str, str] = {}  # For finder tags: <Label_Name, Color_name>
        self.files_in_dir: int = files_in_dir

    def get_extension(self, path: Path) -> str | None:
        if not path or not path.is_file():
            return None
        extension = None
        parts = self._full_path.split('/')
        parts.reverse()
        file_name = parts[0] if parts else None
        if file_name and '.' in file_name:
            file_parts = file_name.split('.')
            file_parts.reverse()
            last_part = str(file_parts[0])
            if last_part:
                word_array = re.split('[^a-zA-Z0-9_]', last_part)
                last_part = str(word_array[0]).lower() if word_array else None
            extension = last_part.lower() \
                if last_part and PathModel.FILE_EXTENSION_PATTERN.match(last_part) \
                else None     # Handles files having no extension
        if not extension:
            extension = path.suffix
        if extension:
            extension = extension.strip()
            if not extension.startswith('.'):
                extension = f".{extension}"
            if len(extension) > 25:
                extension = extension[0:24]
        return extension

    @property
    def path_type(self) -> PathType:
        if self._path_type:
            return self._path_type
        raise NotImplementedError()

    @property
    def tags(self) -> Dict[str, str]:  # For finder tags: <Label_Name, Color_name>
        return self._tags

    @property
    def full_path(self) -> str:
        # _full_path = os.path.join(self.path_root, self.relative_path)
        # return _full_path
        return self._full_path

    def __eq__(self, other):
        """Overrides the default implementation"""
        if self.path_type != other.path_type:
            return False
        if self.full_path != other.full_path:
            return False
        if self.hash and self.hash == other.hash:
            return True
        if self.path_type == PathType.DIRECTORY:
            if self.size == other.size:
                return True
        if self.path_type == PathType.FILE:
            if self.size > 0 and self.size == other.size:
                return True
            if (self.file_name and self.file_name == other.file_name
                    and self.size > 0 and self.size == other.size
                    and self.modify_time and self.modify_time == other.modify_time):
                return True
        return False

    @staticmethod
    def get_content_family_from_mime_type(mime_type: str) -> ContentFamily:
        if not mime_type:
            return None
        if mime_type.startswith('audio') or 'music' in mime_type:
            return ContentFamily.AUDIO
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
        path_type = PathType.FILE if values.get('path_type', '').lower() == 'file' else PathType.DIRECTORY
        path_model: PathModel = PathModel(root=root, path=path, size=values.get('size', 0))
        if not path_model.path_type:
            path_model._path_type = path_type
        return path_model

    def to_json(self):
        props = self.__dict__.copy()
        props['path_stage'] = self.path_stage.name
        return props
