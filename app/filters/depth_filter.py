#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
from os import DirEntry, stat_result
from pathlib import Path

from loguru import logger
from multipledispatch import dispatch

from filters.filter import Filter
from interfaces.iCrawler import ICrawler


class DepthFilter(Filter):

    def __init__(self, max_depth: int = -1, root_dir_path='/') -> None:
        super().__init__()
        self.max_depth = max_depth
        self.root_dir_path = root_dir_path

    @dispatch(Path)
    def authorize(self, path: Path) -> bool:
        """
        :return:
        """
        if not self.can_process(path):
            return False

        depth = len(path.relative_to(self.root_dir_path).parts)

        if 0 < self.max_depth < depth:
            logger.debug(f"Skipping path {path}: above max allowed depth {self.max_depth} (current: {depth})")
            return False
        return True

    @dispatch(DirEntry, stat_result)
    def authorize(self, entry: DirEntry, stat: stat_result = None):
        """
        :return:
        """
        if not self.can_process(entry):
            return False

        relative_path = entry.path.replace(self.root_dir_path, '')
        parts = [x for x in relative_path.split('/') if x]

        depth = len(parts)
        if 0 < self.max_depth < depth:
            logger.debug(f"Skipping path {entry.path}: above max allowed depth {self.max_depth} (current: {depth})")
            return False
        return True

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict.update({
            self.__class__.__name__: {
                "max_depth": self.max_depth,
                "root_dir_path": self.root_dir_path
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
