import sys
from pathlib import Path

from loguru import logger

from app.filters.filter import Filter
from app.interfaces.iCrawler import ICrawler


class SizeFilter(Filter):

    def __init__(self, min_size_in_bytes: int = 0, max_size_in_bytes: int = sys.maxsize) -> None:
        super().__init__()
        self.min_size_in_bytes = min_size_in_bytes
        self.max_size_in_bytes = max_size_in_bytes

    def authorize(self, crawler: ICrawler, path: Path) -> bool:
        """
        :return:
        """
        if not self.can_process(crawler, path):
            return False

        size = path.lstat().st_size
        authorized = self.min_size_in_bytes <= size <= self.max_size_in_bytes
        if not authorized:
            logger.debug(f"Skipping path {path}: size is {size} (min allowed: {self.min_size_in_bytes}, "
                         f"max allowed: {self.max_size_in_bytes})")
        return authorized

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict.update({
            "filter": self.__class__.__name__,
            "min_size_in_bytes": self.min_size_in_bytes,
            "max_size_in_bytes": self.max_size_in_bytes
        })
        return json_dict

    def __eq__(self, o: object) -> bool:
        if o is None or o.__class__.__name__ != SizeFilter.__name__ or not isinstance(o, SizeFilter):
            return False
        return self.min_size_in_bytes == o.min_size_in_bytes \
               and self.max_size_in_bytes == o.max_size_in_bytes

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.to_json())))
