#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path
from loguru import logger

from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler
from app.crawler.events.crawlerEventArgs import CrawlerEventArgs
from app.models.file import FileModel
from app.models.directory import DirectoryModel


class PathEventArgs(CrawlerEventArgs):

    def __init__(self, crawler: ICrawler, path: Path, root_dir_path: str, is_dir: bool, is_file: bool,
                 size_in_mb: int) -> None:
        super().__init__(crawler=crawler)
        self.path: Path = path
        self.is_dir = self.path and self.path.is_dir() or is_dir
        self.is_file = self.path and self.path.is_file() or is_file
        self.size_in_mb = size_in_mb
        self.root_dir_path = root_dir_path
        if self.is_file:
            self.path_model = FileModel(root=self.root_dir_path, path=self.path, size_in_mb=self.size_in_mb)
        elif self.is_dir:
            self.path_model = DirectoryModel(root=self.root_dir_path, path=self.path, size_in_mb=self.size_in_mb, files_in_dir=0)
        else:
            logger.error(f"Unable to determine whether the path '{self.path}' is a file or a directory")

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
