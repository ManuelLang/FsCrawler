#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
from pathlib import Path

from crawler.events.pathEventArgs import PathEventArgs
from helpers.serializationHelper import JsonDumper
from interfaces.iCrawler import ICrawler
from models.content import ContentCategory, ContentClassificationPegi


class FileCrawledEventArgs(PathEventArgs):

    def __init__(self, crawler: ICrawler, path: Path, root_dir_path: str, size: int,
                 root_category: ContentCategory = None, root_min_age: ContentClassificationPegi = None,
                 root_target_table: str = None) -> None:
        super().__init__(crawler=crawler, path=path, is_dir=False, is_file=True, size=size,
                         root_dir_path=root_dir_path, root_category=root_category, root_min_age=root_min_age,
                         root_target_table=root_target_table)

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
