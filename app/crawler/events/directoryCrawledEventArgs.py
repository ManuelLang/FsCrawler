#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path

from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler
from crawler.events.pathEventArgs import PathEventArgs


class DirectoryCrawledEventArgs(PathEventArgs):

    def __init__(self, crawler: ICrawler, path: Path, size_in_mb: int, files_in_dir: int, root_dir_path: str) -> None:
        super().__init__(crawler=crawler, path=path, is_dir=True, is_file=False, size_in_mb=size_in_mb,
                         root_dir_path=root_dir_path)
        self.files_in_dir: int = files_in_dir
        self.path_model.files_in_dir = self.files_in_dir

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
