from pathlib import Path

from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler
from crawler.events.crawlerEventArgs import CrawlerEventArgs


class PathEventArgs(CrawlerEventArgs):

    def __init__(self, crawler: ICrawler, path: Path, is_dir: bool, is_file: bool, size_in_mb: int) -> None:
        super().__init__(crawler=crawler)
        self.path: Path = path
        self.is_dir = is_dir
        self.is_file = is_file
        self.size_in_mb = size_in_mb

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
