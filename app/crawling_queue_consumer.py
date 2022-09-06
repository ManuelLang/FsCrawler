import time
from queue import Queue

from loguru import logger

from crawler.events.crawlerEventArgs import CrawlerEventArgs
from crawler.events.pathEventArgs import PathEventArgs
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
        try:
            while self._crawling_queue.empty():
                logger.debug("Queue full, waiting for the files to be processed")
                time.sleep(1)  # Wait for some data to come in

            item = self._crawling_queue.get()
        except Exception as ex:
            logger.error(f"Error while popping item '{item}' from queue for processing: {ex}")
            # stops the process
            if item:
                item.should_stop = True
        return item

    def _process_path(self, crawl_event: PathEventArgs):
        if crawl_event.is_file:
            logger.info(f"Saving file '{crawl_event.path}' into DB...")
            self.processed_files += 1
            # TODO: implement a file processor interface

    def start(self):
        while not (self._crawling_queue.empty() and self._should_stop):
            crawl_event = self.pop_item()
            if isinstance(crawl_event, PathEventArgs):
                self._process_path(crawl_event=crawl_event)
        logger.info(f"Processed {self.processed_files} files")
