#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
from os import DirEntry, stat_result
from pathlib import Path
from typing import List

from loguru import logger
from multipledispatch import dispatch

from filters.filter import Filter
from interfaces.iCrawler import ICrawler


class ExtensionFilter(Filter):

    def __init__(self, authorized_extensions: set[str] = {}, excluded_extensions: set[str] = {}) -> None:
        super().__init__()
        self.authorized_extensions = authorized_extensions
        self.excluded_extensions = excluded_extensions

    # @dispatch(Path)
    # def authorize(self, path: Path) -> bool:
    #     """
    #     :return:
    #     """
    #     if path.is_dir():
    #         return True     # Crawl files inside directories
    #
    #     if not self.can_process(path):
    #         return False
    #
    #     extension = path.suffix[1:] if path.suffix.startswith('.') else path.suffix
    #     if self.excluded_extensions:
    #         if path.suffix in self.excluded_extensions or path.suffix != extension and extension in self.excluded_extensions:
    #             logger.info(f"Skipping path {path}: excluded by extensions {self.excluded_extensions}")
    #             return False
    #
    #     if self.authorized_extensions:
    #         if path.suffix not in self.authorized_extensions and extension not in self.authorized_extensions:
    #             logger.info(f"Skipping path {path}: not allowed by extensions {self.authorized_extensions}")
    #             return False
    #     # logger.debug(f"ExtensionFilter: Authorizing path {path}")
    #     return True

    def authorize(self, entry: DirEntry, stat: stat_result = None):
        file_extension = str(entry.name.split('.')[-1]).lower() \
            if entry.is_file(follow_symlinks=False) and '.' in entry.name else None
        if file_extension and len(file_extension) > 12:
            file_extension = None  # There is likely a dot in the middle of the filename, but no extension
        if self.excluded_extensions:
            if file_extension in self.excluded_extensions:
                logger.debug(f"Skipping path {entry.path}: excluded by extensions {self.excluded_extensions}")
                return False

        if self.authorized_extensions:
            if file_extension not in self.authorized_extensions:
                logger.debug(f"Skipping path {entry.path}: not allowed by extensions {self.authorized_extensions}")
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
