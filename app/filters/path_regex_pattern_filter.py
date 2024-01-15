#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path

from loguru import logger
import re

from app.filters.filter import Filter
from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler


class RegexPatternFilter(Filter):
    """
    See https://docs.python.org/3/howto/regex.html for reference
    """

    def __init__(self, authorized_path_pattern: str = '', excluded_path_pattern: str = '', ignore_case: bool = True) -> None:
        """
        Filter paths based on the **regex patterns** that are defined.
        /!\ This is NOT a Path pattern
        :param authorized_path_pattern: the regex pattern that should be crawled, e.g. .*\.jpg$
        :param excluded_path_pattern: the regex pattern that should be skipped, e.g. \/MyDummyFolder\/
        """
        super().__init__()
        self.authorized_path_pattern = None
        if authorized_path_pattern:
            self.authorized_path_pattern = re.compile(authorized_path_pattern, re.IGNORECASE if ignore_case else 0)
        self.excluded_path_pattern = None
        if excluded_path_pattern:
            self.excluded_path_pattern = re.compile(excluded_path_pattern, re.IGNORECASE if ignore_case else 0)

    def authorize(self, crawler: ICrawler, path: Path) -> bool:
        """
        :return:
        """
        if not self.can_process(crawler, path):
            return False

        str_path = str(path)
        if self.excluded_path_pattern:
            if self.excluded_path_pattern.findall(str_path) or self.excluded_path_pattern.pattern.replace('\\', '') in str_path:
                logger.debug(f"Skipping path {path}: excluded by pattern {self.excluded_path_pattern}")
                return False

        if self.authorized_path_pattern:
            if not self.authorized_path_pattern.findall(str_path) or self.authorized_path_pattern.pattern.replace('\\', '') in str_path:
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
        if o is None or o.__class__.__name__ != RegexPatternFilter.__name__ or not isinstance(o, RegexPatternFilter):
            return False
        return self.authorized_path_pattern == o.authorized_path_pattern \
               and self.excluded_path_pattern == o.excluded_path_pattern

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.to_json())))

    def __str__(self) -> str:
        return JsonDumper.dumps(self.to_json())
