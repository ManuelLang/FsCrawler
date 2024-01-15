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


class ContentCategory(Enum):
    ALL = '*'
    MUSIC = 1
    BOOK = 2
    MOVIE = 3
    ANIME = 4
    SERIES = 5
    PHOTO = 6
    PAPER = 7
    CODE = 8
    ADULT = 9
    GAME = 10
    APP = 11

    def __str__(self):
        return self.name


class ContentClassificationPegi(Enum):
    ALL = '*'
    THREE_OR_MORE= 1
    SEVEN_OR_MORE = 2
    TWELVE_OR_MORE = 3
    SIXTEEN_OR_MORE = 4
    EIGHTEEN_OR_MORE = 5

    def __str__(self):
        return self.name

class Content:
    def __init__(self) -> None:
        super().__init__()
        self.file_ids: List[str] = []
