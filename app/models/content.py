from enum import Enum
from typing import List


class ContentFamily(Enum):
    ALL = '*'
    MUSIC = 'MUSIC'
    PICTURE = 'PICTURE'
    VIDEO = 'VIDEO'
    DOCUMENT = 'DOCUMENT'
    APPLICATION = 'APPLICATION'
    ARCHIVE = 'ARCHIVE'

    def __str__(self):
        return self.name


class Content:
    def __init__(self) -> None:
        super().__init__()
        self.file_ids: List[str] = []
