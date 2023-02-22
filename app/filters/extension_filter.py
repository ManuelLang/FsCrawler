#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path
from typing import List

from loguru import logger

from app.filters.filter import Filter
from app.interfaces.iCrawler import ICrawler


class ExtensionFilter(Filter):

    def __init__(self, authorized_extensions: List[str] = [], excluded_extensions: List[str] = []) -> None:
        super().__init__()
        self.authorized_extensions = authorized_extensions
        self.excluded_extensions = excluded_extensions

    def authorize(self, crawler: ICrawler, path: Path) -> bool:
        """
        :return:
        """
        if not self.can_process(crawler, path):
            return False

        if self.excluded_extensions:
            if path.suffix in self.excluded_extensions:
                logger.debug(f"Skipping path {path}: excluded by extensions {self.excluded_extensions}")
                return False

        if self.authorized_extensions:
            if path.suffix in self.authorized_extensions:
                logger.debug(f"Skipping path {path}: not allowed by extensions {self.authorized_extensions}")
                return False

        return True

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict.update({
            "filter": self.__class__.__name__,
            "authorized_extensions": self.authorized_extensions,
            "excluded_extensions": self.excluded_extensions
        })
        return json_dict

    def __eq__(self, o: object) -> bool:
        if o is None or o.__class__.__name__ != ExtensionFilter.__name__ or not isinstance(o, ExtensionFilter):
            return False
        return self.authorized_extensions == o.authorized_extensions \
               and self.excluded_extensions == o.excluded_extensions

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.to_json())))
