#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from helpers.serializationHelper import JsonDumper
from interfaces.iCrawler import ICrawler
from crawler.events.crawlerEventArgs import CrawlerEventArgs


class CrawlStatusEventArgs(CrawlerEventArgs):

    def __init__(self, crawler: ICrawler) -> None:
        super().__init__(crawler=crawler)

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
