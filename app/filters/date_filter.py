#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import datetime
from os import DirEntry, stat_result
from pathlib import Path

import pytz
from loguru import logger

from filters.filter import Filter
from interfaces.iCrawler import ICrawler
from multipledispatch import dispatch


class DateFilter(Filter):

    def __init__(self, attribute_filter: str = '',
                 min_date: datetime.datetime = None,
                 max_date: datetime.datetime = None) -> None:
        """
        :param attribute_filter: One of the attributes to filter on:
        st_atime: float  # time of most recent access,
        st_mtime: float  # time of most recent content modification,
        st_ctime: float  # platform dependent (time of most recent metadata change on Unix, or the time of creation on Windows)
        st_atime_ns: int  # time of most recent access, in nanoseconds
        st_mtime_ns: int  # time of most recent content modification in nanoseconds
        st_ctime_ns: int  # platform dependent (time of most recent metadata change on Unix, or the time of creation on Windows) in nanoseconds
        :param min_date: the earliest date allowed
        :param max_date: the latest date allowed
        """
        super().__init__()
        self.attribute_filter: str = attribute_filter
        self.min_date: datetime.datetime = min_date.replace(tzinfo=pytz.UTC) if min_date else None
        self.max_date: datetime.datetime = max_date.replace(tzinfo=pytz.UTC) if max_date else None

    @dispatch(Path)
    def authorize(self, path: Path) -> bool:
        """
        :return:
        """
        if not self.can_process(path):
            return False

        date_value = None
        lstat = path.lstat()
        if hasattr(lstat, self.attribute_filter):
            date_value = getattr(lstat, self.attribute_filter)

        if not date_value:
            return True

        path_date = datetime.datetime.fromtimestamp(date_value / 1e9).replace(tzinfo=pytz.UTC)
        if self.min_date and path_date < self.min_date:
            logger.debug(f"Skipping path {path}: before allowed min date {self.min_date.isoformat()} "
                         f"(current: {path_date.isoformat()})")
            return False

        if self.max_date and path_date > self.max_date:
            logger.debug(f"Skipping path {path}: after allowed max date {self.max_date.isoformat()} "
                         f"(current: {path_date.isoformat()})")
            return False
        return True

    @dispatch(DirEntry, stat_result)
    def authorize(self, entry: DirEntry, stat: stat_result = None):
        if not entry:
            return False
        if not stat:
            return True

        date_value = None
        if hasattr(stat, self.attribute_filter):
            date_value = getattr(stat, self.attribute_filter)
        if not date_value:
            return True
        path_date = datetime.datetime.fromtimestamp(date_value / 1e9).replace(tzinfo=pytz.UTC)
        if self.min_date and path_date < self.min_date:
            logger.debug(f"Skipping path {entry.path}: before allowed min date {self.min_date.isoformat()} "
                         f"(current: {path_date.isoformat()})")
            return False

        if self.max_date and path_date > self.max_date:
            logger.debug(f"Skipping path {entry.path}: after allowed max date {self.max_date.isoformat()} "
                         f"(current: {path_date.isoformat()})")
            return False
        return True

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict.update({
            self.__class__.__name__: {
                "attribute_filter": self.attribute_filter,
                "min_date": self.min_date,
                "max_date": self.max_date
            }
        })
        return json_dict

    def __eq__(self, o: object) -> bool:
        if o is None or o.__class__.__name__ != DepthFilter.__name__ or not isinstance(o, DepthFilter):
            return False
        return self.max_depth == o.max_depth \
               and self.root_dir_path == o.root_dir_path

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.to_json())))
