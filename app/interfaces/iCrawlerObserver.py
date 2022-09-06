from abc import ABC, abstractmethod

from crawler.events.crawlErrorEventArgs import CrawlErrorEventArgs
from crawler.events.crawlProgressEventArgs import CrawlProgessEventArgs
from crawler.events.crawlStatusEventArgs import CrawlStatusEventArgs
from crawler.events.directoryProcessedEventArgs import DirectoryProcessedEventArgs
from crawler.events.pathEventArgs import PathEventArgs


class ICrawlerObserver(ABC):

    @abstractmethod
    def crawl_starting(self, crawl_event: CrawlStatusEventArgs):
        pass

    @abstractmethod
    def path_found(self, crawl_event: PathEventArgs):
        pass

    @abstractmethod
    def path_skipped(self, crawl_event: PathEventArgs):
        pass

    @abstractmethod
    def processing_file(self, crawl_event: PathEventArgs):
        pass

    @abstractmethod
    def processed_file(self, crawl_event: PathEventArgs):
        pass

    @abstractmethod
    def processing_directory(self, crawl_event: PathEventArgs):
        pass

    @abstractmethod
    def processed_directory(self, crawl_event: DirectoryProcessedEventArgs):
        pass

    @abstractmethod
    def crawl_progress(self, crawl_event: CrawlProgessEventArgs):
        pass

    @abstractmethod
    def crawl_error(self, crawl_event: CrawlErrorEventArgs):
        pass

    @abstractmethod
    def crawl_stopped(self, crawl_event: CrawlStatusEventArgs):
        pass

    @abstractmethod
    def crawl_completed(self, crawl_event: CrawlStatusEventArgs):
        pass
