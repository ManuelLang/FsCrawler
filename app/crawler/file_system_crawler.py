from datetime import time
from typing import List
from loguru import logger

from app.crawler.events.crawlStartingEvent import CrawlStartingEvent
from app.interfaces.iCrawler import ICrawler
from app.interfaces.iCrawlerObserver import ICrawlerObserver
from app.interfaces.iFilter import IFilter
from pathlib import Path


class FileSystemCrawler(ICrawler):

    def __init__(self, roots: List[str], filters: List[IFilter] = [], observers: List[ICrawlerObserver] = []) -> None:
        super().__init__()
        self.roots = roots
        self.filters: List[IFilter] = filters
        self.observers: List[ICrawlerObserver] = observers
        self.processed_paths: List[str] = []
        self._require_stop = False
        self.paths_to_scan: List[Path] = []

    def add_filter(self, path_filter: IFilter):
        if not path_filter:
            raise ValueError("Missing argument 'path_filter'")
        if path_filter not in self.filters:
            self.filters.append(path_filter)
        return self

    def get_filters(self) -> List[IFilter]:
        return self.filters

    def add_observer(self, observer: ICrawlerObserver):
        if not observer:
            raise ValueError("Missing argument 'observer'")
        if observer not in self.observers:
            self.observers.append(observer)
        return self

    def get_observers(self) -> List[ICrawlerObserver]:
        return self.observers

    def _add_path(self, path: Path) -> bool:
        # check if path is not added, or is not a sub-path
        str_path = str(path.resolve())
        for pts in self.paths_to_scan:
            if str_path.startswith(str(pts.resolve())):
                return False
        for pp in self.processed_paths:
            if str_path.startswith(pp):
                return False
        self.paths_to_scan.append(path)
        return True

    def stop(self):
        self._require_stop = True
        logger.info(f"Stop requested. Waiting for pending tasks to complete...")

    def notify_crawl_starting(self, crawl_event: CrawlStartingEvent):
        for observer in self.observers:
            try:
                observer.crawl_starting(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_starting event {crawl_event}: {ex}")

    def start(self):
        logger.info("Scanning is starting...")
        if not self.roots:
            logger.warning("No root location found to be crawled!")
            return

        total_roots = len(self.roots)
        logger.info(f"Found {total_roots} root paths to be crawled. Starting...")
        self.notify_crawl_starting(crawl_event=CrawlStartingEvent(crawler=self))

        # check the root paths
        for root in self.roots:
            d = Path(root)
            if not d.exists():
                raise ValueError(f"The path '{root}' does not exists")
            if not d.is_dir():
                raise ValueError(f"The path '{root}' is not a directory")
            if not self._add_path(d):
                logger.warning(f"Not adding path '{d.resolve()}'")

        for path in self.paths_to_scan:
            self.crawl_path(path)

    def crawl_path(self, path):
        for entry in path.iterdir():
            if entry.is_file():
                logger.info(entry.resolve())
            else:
                self.crawl_path(entry)


if __name__ == '__main__':
    crawler = FileSystemCrawler(roots=['/Users/langm27/Downloads/2021-07-11_Mac_book_Downloads_A_trier/Bail Yoan DUONG'])
    crawler.start()
