#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from enum import Enum


class Rating(Enum):
    ALL = '*'
    EXCELLENT = 5
    GREAT = 4
    AVERAGE = 3
    POOR = 2
    BAD = 1

    def __str__(self):
        return self.name


