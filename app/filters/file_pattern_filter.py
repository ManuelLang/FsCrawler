#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
from os import DirEntry, stat_result
from pathlib import Path

from loguru import logger
from multipledispatch import dispatch

from filters.path_pattern_filter import PatternFilter
from helpers.serializationHelper import JsonDumper
from interfaces.iCrawler import ICrawler


class FilePatternFilter(PatternFilter):

    def __init__(self, authorized_path_pattern: str = '', excluded_path_pattern: str = '') -> None:
        super().__init__(authorized_path_pattern=authorized_path_pattern, excluded_path_pattern=excluded_path_pattern)

    @dispatch(Path)
    def authorize(self, path: Path) -> bool:
        if not self.can_process(path):
            return False
        authorize: bool = False
        if path.is_dir():
            authorize = True    # self in crawler.skip_filters  # Allow to process any directory and subdirs
        else:
            authorize = super(FilePatternFilter, self).authorize(path=path)  # Filter only files
        return authorize

    @dispatch(DirEntry, stat_result)
    def authorize(self, entry: DirEntry, stat: stat_result = None):
        if not self.can_process(entry):
            return False
        if entry.path.is_dir():
            authorize = True    # self in crawler.skip_filters  # Allow to process any directory and subdirs
        else:
            authorize = super(FilePatternFilter, self).authorize(path=entry.path)  # Filter only files
        return authorize

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict.update({
            self.__class__.__name__: {
                "authorized_path_pattern": self.authorized_path_pattern,
                "excluded_path_pattern": self.excluded_path_pattern
            }
        })
        return json_dict