#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
from os import DirEntry, stat_result
from pathlib import Path
from typing import List

from loguru import logger
from multipledispatch import dispatch

from filters.filter import Filter
from helpers.serializationHelper import JsonDumper
from interfaces.iCrawler import ICrawler


class NameFilter(Filter):

    def __init__(self, excluded_names: set[str]) -> None:
        super().__init__()
        self.excluded_names = excluded_names

    # @dispatch(Path)
    # def authorize(self, path: Path) -> bool:
    #     if not self.can_process(path):
    #         return False
    #     entry_name: str = path.parts[-1]
    #     return entry_name in self.excluded_names
    #
    # @dispatch(DirEntry, stat_result)
    def authorize(self, entry: DirEntry, stat: stat_result = None):
        if not self.can_process(entry, stat):
            return False
        return entry.name not in self.excluded_names

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict.update({
            self.__class__.__name__: {
                "excluded_names": self.excluded_names
            }
        })
        return json_dict

    def __eq__(self, o: object) -> bool:
        if o is None or o.__class__.__name__ != NameFilter.__name__ or not isinstance(o, NameFilter):
            return False
        return self.excluded_names == o.excluded_names

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.to_json())))

    def __str__(self) -> str:
        return JsonDumper.dumps(self.to_json())
