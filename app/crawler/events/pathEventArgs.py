from pathlib import Path

from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler
from crawler.events.crawlerEventArgs import CrawlerEventArgs


class PathEventArgs(CrawlerEventArgs):

    def __init__(self, crawler: ICrawler, path: Path) -> None:
        super().__init__(crawler=crawler)
        self.path: Path = path

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
