#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from enum import Enum


class PathStage(Enum):
    CRAWLED = 'CRAWLED'
    ATTRIBUTES_EXTRACTED = 'ATTRIBUTES_EXTRACTED'
    HASH_COMPUTED = 'HASH_COMPUTED'
    TEXT_EXTRACTED = 'TEXT_EXTRACTED'
    THUMBNAIL_GENERATED = 'THUMBNAIL_GENERATED'
    INDEXED = 'INDEXED'
    PATH_DELETED = 'PATH_DELETED'

    def __str__(self):
        return self.name
