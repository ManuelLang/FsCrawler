import time
from queue import Queue

from loguru import logger

from config import config
from crawler.events.crawlErrorEventArgs import CrawlErrorEventArgs
from crawler.events.crawlProgressEventArgs import CrawlProgessEventArgs
from crawler.events.crawlStatusEventArgs import CrawlStatusEventArgs
from crawler.events.directoryProcessedEventArgs import DirectoryProcessedEventArgs
from crawler.events.pathEventArgs import PathEventArgs
from interfaces.iCrawlerObserver import ICrawlerObserver


class QueueObserver(ICrawlerObserver):

    def __init__(self, crawling_queue: Queue) -> None:
        super().__init__()
        if crawling_queue is None:
            raise ValueError("Please provide a Queue")
        self._crawling_queue: Queue = crawling_queue

    def _put_queue_event(self, crawl_event: PathEventArgs):
        try:
            while self._crawling_queue.full():
                logger.info("Queue full, waiting for the files to be processed")
                time.sleep(config.QUEUE_WAIT_TIME)
            self._crawling_queue.put(crawl_event)
        except Exception as ex:
            logger.error(f"Error while pushing item '{crawl_event}' to queue for processing: {ex}")
            crawl_event.should_stop = True

    def crawl_starting(self, crawl_event: CrawlStatusEventArgs):
        super().crawl_starting(crawl_event)

    def path_found(self, crawl_event: PathEventArgs):
        super().path_found(crawl_event)

    def path_skipped(self, crawl_event: PathEventArgs):
        super().path_skipped(crawl_event)

    def processing_file(self, crawl_event: PathEventArgs):
        super().processing_file(crawl_event)

    def processed_file(self, crawl_event: PathEventArgs):
        super().processed_file(crawl_event)
        self._put_queue_event(crawl_event)

    def processing_directory(self, crawl_event: PathEventArgs):
        super().processing_directory(crawl_event)

    def processed_directory(self, crawl_event: DirectoryProcessedEventArgs):
        super().processed_directory(crawl_event)
        self._put_queue_event(crawl_event)

    def crawl_progress(self, crawl_event: CrawlProgessEventArgs):
        super().crawl_progress(crawl_event)

    def crawl_error(self, crawl_event: CrawlErrorEventArgs):
        super().crawl_error(crawl_event)

    def crawl_stopped(self, crawl_event: CrawlStatusEventArgs):
        super().crawl_stopped(crawl_event)

    def crawl_completed(self, crawl_event: CrawlStatusEventArgs):
        super().crawl_completed(crawl_event)
