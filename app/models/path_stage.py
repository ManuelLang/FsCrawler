#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from enum import Enum


class PathStage(Enum):
    CRAWLED = 1
    ATTRIBUTES_EXTRACTED = 2
    HASH_COMPUTED = 3
    TEXT_EXTRACTED = 4
    THUMBNAIL_GENERATED = 5
    INDEXED = 6
    PATH_DELETED = 7

    def __str__(self):
        return self.name
