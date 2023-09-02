#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path

from loguru import logger

from app.filters.filter import Filter
from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler


class PatternFilter(Filter):

    def __init__(self, authorized_path_pattern: str = '', excluded_path_pattern: str = '') -> None:
        super().__init__()
        self.authorized_path_pattern = authorized_path_pattern
        self.excluded_path_pattern = excluded_path_pattern

    def authorize(self, crawler: ICrawler, path: Path) -> bool:
        """
        :return:
        """
        if not self.can_process(crawler, path):
            return False

        if self.excluded_path_pattern:
            if path.match(self.excluded_path_pattern):
                logger.debug(f"Skipping path {path}: excluded by pattern {self.excluded_path_pattern}")
                return False

        if self.authorized_path_pattern:
            if not path.match(self.authorized_path_pattern):
                logger.debug(f"Skipping path {path}: not allowed by pattern {self.authorized_path_pattern}")
                return False

        return True

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict.update({
            "filter": self.__class__.__name__,
            "authorized_path_pattern": self.authorized_path_pattern,
            "excluded_path_pattern": self.excluded_path_pattern
        })
        return json_dict

    def __eq__(self, o: object) -> bool:
        if o is None or o.__class__.__name__ != PatternFilter.__name__ or not isinstance(o, PatternFilter):
            return False
        return self.authorized_path_pattern == o.authorized_path_pattern \
               and self.excluded_path_pattern == o.excluded_path_pattern

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.to_json())))

    def __str__(self) -> str:
        return JsonDumper.dumps(self.to_json())
