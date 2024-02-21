#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path
from typing import List

from loguru import logger

from filters.filter import Filter
from helpers.serializationHelper import JsonDumper
from interfaces.iCrawler import ICrawler
from interfaces.iFilter import IFilter


class OrFilter(Filter):

    def __init__(self, filters: List[IFilter]) -> None:
        super().__init__()
        if not filters:
            raise ValueError(f"The filters list is mandatory")
        self.filters: List[IFilter] = filters

    def authorize(self, path: Path) -> bool:
        """
        :return:
        """
        if any([f.authorize(path=path) for f in self.filters]):
            return True
        logger.debug(f"Skipping path {path}: excluded by all filters:\n{self.filters}")
        return False

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict.update({
            "filter": self.__class__.__name__,
            "filters": [JsonDumper.dumps(f) for f in self.filters]
        })
        return json_dict

    def __eq__(self, o: object) -> bool:
        if o is None or o.__class__.__name__ != OrFilter.__name__ or not isinstance(o, OrFilter):
            return False
        return self.filters == o.filters

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.to_json())))
