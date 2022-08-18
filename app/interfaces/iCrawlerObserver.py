from abc import ABC

from app.crawler.events.crawlStartingEvent import CrawlStartingEvent


class ICrawlerObserver(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'can_process') and
                callable(subclass.can_process) and
                hasattr(subclass, 'authorize') and
                callable(subclass.authorize))

    def crawl_starting(self, scan_event: CrawlStartingEvent):
        pass

    def path_found(self, scan_event: CrawlStartingEvent):
        pass

    def path_skipped(self, scan_event: CrawlStartingEvent):
        pass

    def processing_file(self, scan_event: CrawlStartingEvent):
        pass

    def processing_directory(self, scan_event: CrawlStartingEvent):
        pass

    def path_processed(self, scan_event: CrawlStartingEvent):
        pass

    def crawl_progress(self, scan_event: CrawlStartingEvent):
        pass

    def crawl_error(self, scan_event: CrawlStartingEvent):
        pass

    def crawl_stopped(self, scan_event: CrawlStartingEvent):
        pass

    def crawl_completed(self, scan_event: CrawlStartingEvent):
        pass
