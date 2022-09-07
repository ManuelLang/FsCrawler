import time
from queue import Queue

from loguru import logger

from crawler.events.crawlCompletedEventArgs import CrawlCompletedEventArgs
from crawler.events.crawlStoppedEventArgs import CrawlStoppedEventArgs
from crawler.events.crawlerEventArgs import CrawlerEventArgs
from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iCrawlingQueueConsumer import ICrawlingQueueConsumer


class CrawlingQueueConsumer(ICrawlingQueueConsumer):

    def __init__(self, crawling_queue: Queue) -> None:
        super().__init__()
        if crawling_queue is None:
            raise ValueError("Please provide a Queue")
        self._crawling_queue = crawling_queue
        self._should_stop: bool = False
        self.processed_files: int = 0

    @property
    def should_stop(self) -> bool:
        return self._should_stop

    @should_stop.setter
    def should_stop(self, value: bool):
        self._should_stop = value

    def pop_item(self) -> CrawlerEventArgs:
        item: CrawlerEventArgs = None
        max_retries = 10
        try:
            while self._crawling_queue.empty():
                if self.should_stop:
                    break
                max_retries -= 1
                if max_retries <= 0:
                    self._should_stop = True
                    logger.warning("Processed stopped because no more items coming into queue")
                    break
                logger.info(f"Queue emtpy, waiting for the files to be processed. "
                            f"{max_retries} retry left...")
                time.sleep(1)  # Wait for some data to come in

            if not self._crawling_queue.empty():
                item = self._crawling_queue.get()
        except Exception as ex:
            logger.error(f"Error while popping item '{item}' from queue for processing: {ex}")
            # stops the process
            if item:
                item.should_stop = True
        return item

    def _process_file(self, crawl_event: FileCrawledEventArgs):
        if crawl_event.is_file is True:
            logger.info(f"Saving file '{crawl_event.path}' into DB...")
            self.processed_files += 1
            # TODO: implement a file processor interface

    def start(self):
        while True:
            if self._should_stop:
                break
            crawl_event = self.pop_item()
            if crawl_event is None \
                    or crawl_event.should_stop \
                    or isinstance(crawl_event, CrawlCompletedEventArgs) \
                    or isinstance(crawl_event, CrawlStoppedEventArgs):
                self._should_stop = True
                break
            if isinstance(crawl_event, FileCrawledEventArgs):
                self._process_file(crawl_event=crawl_event)

        logger.info(f"Processed {self.processed_files} files")
