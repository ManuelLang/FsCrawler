from pathlib import Path

from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler
from crawler.events.pathEventArgs import PathEventArgs


class DirectoryProcessedEventArgs(PathEventArgs):

    def __init__(self, crawler: ICrawler, path: Path, directory_size: int) -> None:
        super().__init__(crawler=crawler, path=path, is_dir=True, is_file=False, size_in_gb=directory_size)

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
