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

    @staticmethod
    def from_name(name: str):
        if not name:
            raise ValueError("The name is mandatory to parse the ContentCategory")
        name = name.strip().upper()
        try:
            return ContentCategory[name]
        except Exception as ex:
            raise ValueError(f"Can not parse name '{name}' to ContentCategory. Allowed values are: {[e.value for e in ContentCategory]}")


class ContentClassificationPegi(Enum):
    ALL = '*'
    THREE_OR_MORE= 3
    SEVEN_OR_MORE = 7
    TWELVE_OR_MORE = 12
    SIXTEEN_OR_MORE = 16
    EIGHTEEN_OR_MORE = 18

    @staticmethod
    def classification_from_age(age: int):
        if age < 7:
            return ContentClassificationPegi.THREE_OR_MORE
        elif age < 12:
            return ContentClassificationPegi.SEVEN_OR_MORE
        elif age < 16:
            return ContentClassificationPegi.TWELVE_OR_MORE
        elif age < 18:
            return ContentClassificationPegi.SIXTEEN_OR_MORE
        else:
            return ContentClassificationPegi.EIGHTEEN_OR_MORE

    @staticmethod
    def from_name(name: str):
        if not name:
            raise ValueError("The name is mandatory to parse the ContentClassificationPegi")
        name = name.strip().upper()
        try:
            return ContentClassificationPegi[name]
        except Exception as ex:
            raise ValueError(f"Can not parse name '{name}' to ContentClassificationPegi. Allowed values are: {[e.value for e in ContentClassificationPegi]}")

    def __str__(self):
        return self.name


class Content:
    def __init__(self) -> None:
        super().__init__()
        self.file_ids: List[str] = []
