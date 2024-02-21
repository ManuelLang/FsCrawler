#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path
from loguru import logger

from helpers.serializationHelper import JsonDumper
from interfaces.iCrawler import ICrawler
from crawler.events.crawlerEventArgs import CrawlerEventArgs
from models.content import ContentCategory, ContentClassificationPegi
from models.file import FileModel
from models.directory import DirectoryModel


class PathEventArgs(CrawlerEventArgs):

    def __init__(self, crawler: ICrawler, path: Path, root_dir_path: str, is_dir: bool, is_file: bool,
                 size: int, root_category: ContentCategory = None,
                 root_min_age: ContentClassificationPegi = None, root_target_table: str = None) -> None:
        super().__init__(crawler=crawler)
        self.path: Path = path
        self.is_dir = is_dir or self.path and self.path.is_dir()
        self.is_file = is_file or self.path and self.path.is_file()
        self.size = size
        self.root_dir_path = root_dir_path
        if self.is_file:
            self.path_model = FileModel(root=self.root_dir_path, path=self.path, size=self.size)
        elif self.is_dir:
            self.path_model = DirectoryModel(root=self.root_dir_path, path=self.path, size=self.size, files_in_dir=0)
        else:
            logger.error(f"Unable to determine whether the path '{self.path}' is a file or a directory")

        self.path_model.content_category = root_category
        self.path_model.content_min_age = root_min_age
        self.root_target_table = root_target_table

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
