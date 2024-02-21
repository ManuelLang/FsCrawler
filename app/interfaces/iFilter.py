#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from abc import ABC, abstractmethod
from os import DirEntry, stat_result
from pathlib import Path

from multipledispatch import dispatch

from interfaces.iCrawler import ICrawler


class IFilter(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'can_process') and
                callable(subclass.can_process) and
                hasattr(subclass, 'authorize') and
                callable(subclass.authorize))

    @dispatch(Path)
    @abstractmethod
    def can_process(self, path: Path) -> bool:
        pass

    @dispatch(DirEntry, stat_result)
    @abstractmethod
    def authorize(self, entry: DirEntry, stat: stat_result = None) -> bool:
        pass

    @dispatch(Path)
    @abstractmethod
    def can_process(self, path: Path) -> bool:
        pass

    @dispatch(DirEntry, stat_result)
    @abstractmethod
    def authorize(self, entry: DirEntry, stat: stat_result = None):
        pass
