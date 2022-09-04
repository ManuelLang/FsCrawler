from abc import ABC

from crawler.events.crawlErrorEventArgs import CrawlErrorEventArgs
from crawler.events.crawlProgressEventArgs import CrawlProgessEventArgs
from crawler.events.crawlStatusEventArgs import CrawlStatusEventArgs
from crawler.events.pathEventArgs import PathEventArgs


class ICrawlerObserver(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'can_process') and
                callable(subclass.can_process) and
                hasattr(subclass, 'authorize') and
                callable(subclass.authorize))

    def crawl_starting(self, scan_event: CrawlStatusEventArgs):
        pass

    def path_found(self, scan_event: PathEventArgs):
        pass

    def path_skipped(self, scan_event: PathEventArgs):
        pass

    def processing_file(self, scan_event: PathEventArgs):
        pass

    def processed_file(self, scan_event: PathEventArgs):
        pass

    def processing_directory(self, scan_event: PathEventArgs):
        pass

    def processed_directory(self, scan_event: PathEventArgs):
        pass

    def crawl_progress(self, scan_event: CrawlProgessEventArgs):
        pass

    def crawl_error(self, scan_event: CrawlErrorEventArgs):
        pass

    def crawl_stopped(self, scan_event: CrawlStatusEventArgs):
        pass

    def crawl_completed(self, scan_event: CrawlStatusEventArgs):
        pass
