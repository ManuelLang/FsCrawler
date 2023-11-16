#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import time
from queue import Queue

from loguru import logger

from config import config
from crawler.events.crawlCompletedEventArgs import CrawlCompletedEventArgs
from crawler.events.crawlErrorEventArgs import CrawlErrorEventArgs
from crawler.events.crawlProgressEventArgs import CrawlProgessEventArgs
from crawler.events.crawlStartingEventArgs import CrawlStartingEventArgs
from crawler.events.crawlStoppedEventArgs import CrawlStoppedEventArgs
from crawler.events.crawlerEventArgs import CrawlerEventArgs
from crawler.events.directoryCrawledEventArgs import DirectoryCrawledEventArgs
from crawler.events.directoryFoundEventArgs import DirectoryFoundEventArgs
from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from crawler.events.fileFoundEventArgs import FileFoundEventArgs
from crawler.events.pathFoundEventArgs import PathFoundEventArgs
from crawler.events.pathSkippedEventArgs import PathSkippedEventArgs
from interfaces.iCrawlerObserver import ICrawlerObserver


class QueueObserver(ICrawlerObserver):

    def __init__(self, crawling_queue: Queue) -> None:
        super().__init__()
        if crawling_queue is None:
            raise ValueError("Please provide a Queue")
        self._crawling_queue: Queue = crawling_queue

    def _put_queue_event(self, crawl_event: CrawlerEventArgs):
        try:
            if self._crawling_queue.full():
                while self._crawling_queue.qsize() >= config.QUEUE_MIN_SIZE:
                    logger.info("Queue full, waiting for the files to be processed...")
                    time.sleep(config.QUEUE_WAIT_TIME / 3)
            self._crawling_queue.put(crawl_event)
        except Exception as ex:
            logger.error(f"Error while pushing item '{crawl_event}' to queue for processing: {ex}")
            crawl_event.should_stop = True

    def crawl_starting(self, crawl_event: CrawlStartingEventArgs):
        super().crawl_starting(crawl_event)
        self._put_queue_event(crawl_event)

    def path_found(self, crawl_event: PathFoundEventArgs):
        super().path_found(crawl_event)
        self._put_queue_event(crawl_event)

    def path_skipped(self, crawl_event: PathSkippedEventArgs):
        super().path_skipped(crawl_event)
        self._put_queue_event(crawl_event)

    def processing_file(self, crawl_event: FileFoundEventArgs):
        super().processing_file(crawl_event)
        self._put_queue_event(crawl_event)

    def processed_file(self, crawl_event: FileCrawledEventArgs):
        super().processed_file(crawl_event)
        self._put_queue_event(crawl_event)

    def processing_directory(self, crawl_event: DirectoryFoundEventArgs):
        super().processing_directory(crawl_event)
        self._put_queue_event(crawl_event)

    def processed_directory(self, crawl_event: DirectoryCrawledEventArgs):
        super().processed_directory(crawl_event)
        self._put_queue_event(crawl_event)

    def crawl_progress(self, crawl_event: CrawlProgessEventArgs):
        super().crawl_progress(crawl_event)
        self._put_queue_event(crawl_event)

    def crawl_error(self, crawl_event: CrawlErrorEventArgs):
        super().crawl_error(crawl_event)
        self._put_queue_event(crawl_event)

    def crawl_stopped(self, crawl_event: CrawlStoppedEventArgs):
        super().crawl_stopped(crawl_event)
        self._put_queue_event(crawl_event)

    def crawl_completed(self, crawl_event: CrawlCompletedEventArgs):
        super().crawl_completed(crawl_event)
        self._put_queue_event(crawl_event)
