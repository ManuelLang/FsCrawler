#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path

from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler
from crawler.events.crawlerEventArgs import CrawlerEventArgs


class CrawlErrorEventArgs(CrawlerEventArgs):

    def __init__(self, crawler: ICrawler, error: BaseException, path: Path = None) -> None:
        super().__init__(crawler=crawler)
        self.error = error
        self.path = path

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
