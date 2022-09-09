from enum import Enum


class PathType(Enum):
    ALL = '*'
    FILE = 'FILE'
    DIRECTORY = 'DIRECTORY'

    def __str__(self):
        return self.name
