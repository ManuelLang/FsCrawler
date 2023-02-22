#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from abc import ABC, abstractmethod
from pathlib import Path

from app.interfaces.iCrawler import ICrawler


class IFilter(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'can_process') and
                callable(subclass.can_process) and
                hasattr(subclass, 'authorize') and
                callable(subclass.authorize))

    @abstractmethod
    def can_process(self, crawler: ICrawler, path: Path) -> bool:
        pass

    @abstractmethod
    def authorize(self, crawler: ICrawler, path: Path) -> bool:
        pass
