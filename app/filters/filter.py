#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
from os import DirEntry, stat_result
from pathlib import Path

from loguru import logger
from multipledispatch import dispatch

from helpers.serializationHelper import JsonDumper
from interfaces.iFilter import IFilter
from interfaces.iCrawler import ICrawler


class Filter(IFilter):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'can_process') and
                callable(subclass.can_process) and
                hasattr(subclass, 'authorize') and
                callable(subclass.authorize))

    # @dispatch(Path)
    # def can_process(self, path: Path) -> bool:
    #     can_process = True if path else False
    #     if not can_process:
    #         logger.warning(f"Not a valid path: {path}")
    #     return can_process
    #
    # @dispatch(DirEntry, stat_result)
    def can_process(self, entry: DirEntry, stat: stat_result = None) -> bool:
        can_process = True if entry else False
        if not can_process:
            logger.warning(f"Not a valid entry: {entry.path}")
        return can_process

    @dispatch(Path)
    def authorize(self, path: Path) -> bool:
        return self.can_process(path)

    @dispatch(DirEntry, stat_result)
    def authorize(self, entry: DirEntry, stat: stat_result = None):
        return self.can_process(entry)

    def to_json(self) -> dict:
        return {}

    def __str__(self) -> str:
        return JsonDumper.dumps({
            self.__class__.__name__: self.to_json()
        })
