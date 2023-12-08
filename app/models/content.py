#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from enum import Enum
from typing import List


class ContentFamily(Enum):
    ALL = '*'
    AUDIO = 1
    PICTURE = 2
    VIDEO = 3
    DOCUMENT = 4
    APPLICATION = 5
    ARCHIVE = 6

    def __str__(self):
        return self.name


class Content:
    def __init__(self) -> None:
        super().__init__()
        self.file_ids: List[str] = []
