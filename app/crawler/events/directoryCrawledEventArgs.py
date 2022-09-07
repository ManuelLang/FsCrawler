from pathlib import Path

from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler
from crawler.events.pathEventArgs import PathEventArgs


class DirectoryCrawledEventArgs(PathEventArgs):

    def __init__(self, crawler: ICrawler, path: Path, size_in_mb: int, files_in_dir: int) -> None:
        super().__init__(crawler=crawler, path=path, is_dir=True, is_file=False, size_in_mb=size_in_mb)
        self.files_in_dir: int = files_in_dir

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
