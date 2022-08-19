import time
from pathlib import Path
from typing import List

from loguru import logger

from app.crawler.events.crawlStartingEvent import CrawlStartingEvent
from app.interfaces.iCrawler import ICrawler
from app.interfaces.iCrawlerObserver import ICrawlerObserver
from app.interfaces.iFilter import IFilter
from helpers.filesite_helper import *


class FileSystemCrawler(ICrawler):

    def __init__(self, roots: List[str], filters: List[IFilter] = [], observers: List[ICrawlerObserver] = []) -> None:
        super().__init__()
        self.roots = roots
        self.filters: List[IFilter] = filters
        self.observers: List[ICrawlerObserver] = observers
        self.processed_paths: List[str] = []
        self._require_stop = False
        self.paths_to_scan: List[Path] = []
        self.crawled_files_size = 0

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
        path = path.expanduser().resolve(strict=True)
        str_path = str(path)

        # check if path is not added, or is not a sub-path
        if not path.is_dir():
            raise ValueError(f"The path '{str_path}' is not a directory")

        for pts in self.paths_to_scan:
            if str_path.startswith(str(pts)):
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
        start_time = time.time()
        if not self.roots:
            logger.warning("No root location found to be crawled!")
            return

        total_roots = len(self.roots)
        logger.info(f"Found {total_roots} root paths to be crawled. Starting...")
        self.notify_crawl_starting(crawl_event=CrawlStartingEvent(crawler=self))

        # check the root paths
        for root in self.roots:
            if not self._add_path(Path(root)):
                logger.warning(f"Not adding path '{root}'")

        for path in self.paths_to_scan:
            self.crawl_path(path)

        end_time = time.time()
        logger.info(f"Crawled {len(self.processed_paths)} files (total of {self.crawled_files_size:0.2f} Gb) in "
                    f"{end_time - start_time:0.4f} sec")

    def crawl_path(self, path):
        for entry in sorted(path.iterdir()):
            entry = entry.expanduser().resolve()
            if not entry.exists():
                continue

            entry_str = str(entry)
            if self._require_stop:
                return

            self.processed_paths.append(entry_str)
            self.crawled_files_size += convert_size_to_gb(entry.lstat().st_size)

            if any(not f.authorize(crawler=self, path=entry) for f in self.filters):
                continue

            if entry.is_file():
                logger.info(entry_str)
            else:
                self.crawl_path(entry)
