from abc import ABC, abstractmethod

from crawler.events.crawlCompletedEventArgs import CrawlCompletedEventArgs
from crawler.events.crawlErrorEventArgs import CrawlErrorEventArgs
from crawler.events.crawlProgressEventArgs import CrawlProgessEventArgs
from crawler.events.crawlStartingEventArgs import CrawlStartingEventArgs
from crawler.events.crawlStoppedEventArgs import CrawlStoppedEventArgs
from crawler.events.directoryCrawledEventArgs import DirectoryCrawledEventArgs
from crawler.events.directoryFoundEventArgs import DirectoryFoundEventArgs
from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from crawler.events.fileFoundEventArgs import FileFoundEventArgs
from crawler.events.pathFoundEventArgs import PathFoundEventArgs
from crawler.events.pathSkippedEventArgs import PathSkippedEventArgs


class ICrawlerObserver(ABC):

    @abstractmethod
    def crawl_starting(self, crawl_event: CrawlStartingEventArgs):
        pass

    @abstractmethod
    def path_found(self, crawl_event: PathFoundEventArgs):
        pass

    @abstractmethod
    def path_skipped(self, crawl_event: PathSkippedEventArgs):
        pass

    @abstractmethod
    def processing_file(self, crawl_event: FileFoundEventArgs):
        pass

    @abstractmethod
    def processed_file(self, crawl_event: FileCrawledEventArgs):
        pass

    @abstractmethod
    def processing_directory(self, crawl_event: DirectoryFoundEventArgs):
        pass

    @abstractmethod
    def processed_directory(self, crawl_event: DirectoryCrawledEventArgs):
        pass

    @abstractmethod
    def crawl_progress(self, crawl_event: CrawlProgessEventArgs):
        pass

    @abstractmethod
    def crawl_error(self, crawl_event: CrawlErrorEventArgs):
        pass

    @abstractmethod
    def crawl_stopped(self, crawl_event: CrawlStoppedEventArgs):
        pass

    @abstractmethod
    def crawl_completed(self, crawl_event: CrawlCompletedEventArgs):
        pass
