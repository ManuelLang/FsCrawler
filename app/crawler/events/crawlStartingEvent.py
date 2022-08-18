from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iCrawler import ICrawler


class CrawlStartingEvent:

    def __init__(self, crawler: ICrawler) -> None:
        super().__init__()
        self.crawler: ICrawler = crawler
        self.should_stop: bool = False

    def __str__(self) -> str:
        return JsonDumper.dumps(self.__dict__)
