#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path
from typing import List

from helpers.serializationHelper import JsonDumper
from interfaces.iCrawler import ICrawler
from crawler.events.pathEventArgs import PathEventArgs
from models.content import ContentCategory, ContentClassificationPegi


class DirectoryCrawledEventArgs(PathEventArgs):

    def __init__(self, crawler: ICrawler, path: Path, size: int, files_in_dir: int, root_dir_path: str,
                 file_names: List[str], root_category: ContentCategory = None,
                 root_min_age: ContentClassificationPegi = None, root_target_table: str = None) -> None:
        super().__init__(crawler=crawler, path=path, root_dir_path=root_dir_path, is_dir=True, is_file=False, size=size,
                         root_category=root_category, root_min_age=root_min_age,
                         root_target_table=root_target_table)
        self.file_names: List[str] = file_names
        self.files_in_dir: int = files_in_dir
        self.path_model.files_in_dir = self.files_in_dir

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
