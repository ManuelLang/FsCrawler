from pathlib import Path

from loguru import logger

from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iFilter import IFilter
from interfaces.iCrawler import ICrawler


class Filter(IFilter):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'can_process') and
                callable(subclass.can_process) and
                hasattr(subclass, 'authorize') and
                callable(subclass.authorize))

    def can_process(self, crawler: ICrawler, path: Path) -> bool:
        can_process = True if path and path.exists() else False
        if not can_process:
            logger.info(f"Not a valid path: {path}")
        return can_process

    def authorize(self, crawler: ICrawler, path: Path) -> bool:
        return self.can_process(crawler, path)

    def to_json(self) -> dict:
        return {}

    def __str__(self) -> str:
        return JsonDumper.dumps({
            self.__class__.__name__: self.to_json()
        })
