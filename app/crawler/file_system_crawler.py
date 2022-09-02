from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from loguru import logger

from app.interfaces.iCrawler import ICrawler
from app.interfaces.iCrawlerObserver import ICrawlerObserver
from app.interfaces.iFilter import IFilter
from crawler.events.crawlErrorEventArgs import CrawlErrorEventArgs
from crawler.events.crawlProgressEventArgs import CrawlProgessEventArgs
from crawler.events.crawlStatusEventArgs import CrawlStatusEventArgs
from crawler.events.pathEventArgs import PathEventArgs
from helpers.filesite_helper import *


class FileSystemCrawler(ICrawler):

    def __init__(self, roots: List[str], filters: List[IFilter] = [], observers: List[ICrawlerObserver] = []) -> None:
        super().__init__()
        self.roots = roots
        self._filters: List[IFilter] = filters
        self._observers: List[ICrawlerObserver] = observers
        self._require_stop = False
        self._paths_to_crawl: List[Path] = []

        # stats
        self._paths_found: List[Path] = []
        self._paths_skipped: List[Path] = []
        self._files_processed: List[Path] = []
        self._directories_processed: List[Path] = []
        self._errored_paths: Dict[str, str] = defaultdict(str)
        self._crawled_paths: List[str] = []
        self._crawled_files_size: int = 0
        self._start_time: datetime = None
        self._end_time: datetime = None

    def add_filter(self, path_filter: IFilter):
        if not path_filter:
            raise ValueError("Missing argument 'path_filter'")
        if path_filter not in self.filters:
            self.filters.append(path_filter)
        return self

    @property
    def filters(self) -> List[IFilter]:
        return self._filters

    def add_observer(self, observer: ICrawlerObserver):
        if not observer:
            raise ValueError("Missing argument 'observer'")
        if observer not in self._observers:
            self._observers.append(observer)
        return self

    @property
    def observers(self) -> List[ICrawlerObserver]:
        return self._observers

    @property
    def require_stop(self) -> bool:
        return self._require_stop

    # region stats

    @property
    def paths_found(self) -> List[Path]:
        return self._paths_found

    @property
    def paths_skipped(self) -> List[Path]:
        return self._paths_skipped

    @property
    def files_processed(self) -> List[Path]:
        return self._files_processed

    @property
    def directories_processed(self) -> List[Path]:
        return self._directories_processed

    @property
    def crawled_paths(self) -> List[str]:
        return self._crawled_paths

    @property
    def crawled_files_size(self) -> int:
        return self._crawled_files_size

    @property
    def errored_paths(self) -> Dict[str, str]:
        return self._errored_paths

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def end_time(self) -> datetime:
        return self._end_time

    # endregion

    @property
    def crawl_in_progress(self) -> bool:
        return self._start_time is not None and self._end_time is None

    def _add_path(self, path: Path) -> bool:
        path = path.expanduser().resolve(strict=True)
        str_path = str(path)

        # check if path is not added, or is not a sub-path
        if not path.is_dir():
            raise ValueError(f"The path '{str_path}' is not a directory")

        for pts in self._paths_to_crawl:
            if str_path.startswith(str(pts)):
                return False
        for pp in self._crawled_paths:
            if str_path.startswith(pp):
                return False
        self._paths_to_crawl.append(path)
        return True

    def stop(self):
        self._require_stop = True
        logger.info(f"Stop requested. Waiting for pending tasks to complete...")

    # region notifications

    def notify_crawl_starting(self, crawl_event: CrawlStatusEventArgs):
        for observer in self.observers:
            try:
                observer.crawl_starting(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_starting event {crawl_event}: {ex}")

    def notify_path_found(self, crawl_event: PathEventArgs):
        self.paths_found.append(crawl_event.path)
        for observer in self.observers:
            try:
                observer.path_found(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for path_found event {crawl_event}: {ex}")

    def notify_path_skipped(self, crawl_event: PathEventArgs):
        self.paths_skipped.append(crawl_event.path)
        for observer in self.observers:
            try:
                observer.path_skipped(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for path_skipped event {crawl_event}: {ex}")

    def notify_processing_file(self, crawl_event: PathEventArgs):
        self.files_processed.append(crawl_event.path)
        for observer in self.observers:
            try:
                observer.processing_file(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for processing_file event {crawl_event}: {ex}")

    def notify_processing_directory(self, crawl_event: PathEventArgs):
        self.directories_processed.append(crawl_event.path)
        for observer in self.observers:
            try:
                observer.processing_directory(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(
                    f"Unable to notify observer '{observer}' for processing_directory event {crawl_event}: {ex}")

    def notify_path_processed(self, crawl_event: PathEventArgs):
        for observer in self.observers:
            try:
                observer.path_processed(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for path_processed event {crawl_event}: {ex}")

    def notify_crawl_progress(self, crawl_event: CrawlProgessEventArgs):
        for observer in self.observers:
            try:
                observer.crawl_progress(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_progress event {crawl_event}: {ex}")

    def notify_crawl_error(self, crawl_event: CrawlErrorEventArgs):
        for observer in self.observers:
            try:
                observer.crawl_progress(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_error event {crawl_event}: {ex}")

    def notify_crawl_stopped(self, crawl_event: CrawlStatusEventArgs):
        for observer in self.observers:
            try:
                observer.crawl_stopped(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_stopped event {crawl_event}: {ex}")

    def notify_crawl_completed(self, crawl_event: CrawlStatusEventArgs):
        for observer in self.observers:
            try:
                observer.crawl_completed(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_completed event {crawl_event}: {ex}")

    # endregion

    def start(self):
        logger.info("Scanning is starting...")
        self._start_time = datetime.now()
        if not self.roots:
            logger.warning("No root location found to be crawled!")
            return

        total_roots = len(self.roots)
        logger.info(f"Found {total_roots} root paths to be crawled. Starting...")
        self.notify_crawl_starting(crawl_event=CrawlStatusEventArgs(crawler=self))

        try:
            # check the root paths
            for root in self.roots:
                if not self._add_path(Path(root)):
                    logger.warning(f"Not adding path '{root}'")

            for path in self._paths_to_crawl:
                self.crawl_path(path)
        except Exception as ex:
            logger.error(ex)
            self.notify_crawl_error(crawl_event=CrawlErrorEventArgs(crawler=self, error=ex))

        self._end_time = datetime.now()
        logger.info(f"Crawled {len(self._crawled_paths)} files (total of {self._crawled_files_size:0.2f} Gb) in "
                    f"{self._end_time - self._start_time:0.4f} sec")

        if self.require_stop:
            self.notify_crawl_stopped(crawl_event=CrawlStatusEventArgs(crawler=self))
        else:
            self.notify_crawl_completed(crawl_event=CrawlStatusEventArgs(crawler=self))

    def crawl_path(self, path):
        self.notify_path_found(crawl_event=PathEventArgs(crawler=self, path=path))
        for entry in sorted(path.iterdir()):
            try:
                entry = entry.expanduser().resolve()
                if not entry.exists():
                    continue

                entry_str = str(entry)
                if self._require_stop:
                    return

                self._crawled_paths.append(entry_str)
                self._crawled_files_size += convert_size_to_gb(entry.lstat().st_size)
                if len(self._crawled_paths) % 100 == 0:
                    self.notify_crawl_progress(crawl_event=CrawlProgessEventArgs(crawler=self))

                if any(not f.authorize(crawler=self, path=entry) for f in self.filters):
                    self.notify_path_skipped(crawl_event=PathEventArgs(crawler=self, path=entry))
                    continue

                if entry.is_file():
                    logger.debug(f"Crawling file: {entry_str}")
                    self.notify_processing_file(crawl_event=PathEventArgs(crawler=self, path=entry))
                else:
                    self.notify_processing_directory(crawl_event=PathEventArgs(crawler=self, path=entry))
                    self.crawl_path(entry)

                self.notify_path_processed(crawl_event=PathEventArgs(crawler=self, path=entry))
            except Exception as ex:
                logger.error(ex)
                self._errored_paths[str(entry)] = str(ex)
                self.notify_crawl_error(crawl_event=CrawlErrorEventArgs(crawler=self, error=ex, path=entry))
