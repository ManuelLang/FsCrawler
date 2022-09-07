from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from loguru import logger

from app.interfaces.iCrawler import ICrawler
from app.interfaces.iCrawlerObserver import ICrawlerObserver
from app.interfaces.iFilter import IFilter
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
from helpers.filesite_helper import *

MIN_BLOCK_SIZE = 1024 * 4


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
        self._processed_files_size: int = 0
        self._ignored_files: int = 0
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
    def processed_files_size(self) -> int:
        return self._processed_files_size

    @property
    def errored_paths(self) -> Dict[str, str]:
        return self._errored_paths

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def end_time(self) -> datetime:
        return self._end_time

    @property
    def nb_files_skipped(self) -> int:
        return self._ignored_files

    @property
    def nb_directories_skipped(self) -> int:
        _nb_dir_skipped = len(self._paths_skipped) - self._ignored_files
        return _nb_dir_skipped

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

    def notify_crawl_starting(self, crawl_event: CrawlStartingEventArgs):
        for observer in self.observers:
            try:
                observer.crawl_starting(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_starting event {crawl_event}: {ex}")

    def notify_path_found(self, crawl_event: PathFoundEventArgs):
        self.paths_found.append(crawl_event.path)
        for observer in self.observers:
            try:
                observer.path_found(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for path_found event {crawl_event}: {ex}")

    def notify_path_skipped(self, crawl_event: PathSkippedEventArgs):
        self.paths_skipped.append(crawl_event.path)
        if crawl_event.is_file:
            self._ignored_files += 1
        for observer in self.observers:
            try:
                observer.path_skipped(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for path_skipped event {crawl_event}: {ex}")

    def notify_processing_file(self, crawl_event: FileFoundEventArgs):
        self._crawled_files_size += crawl_event.size_in_mb
        for observer in self.observers:
            try:
                observer.processing_file(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for processing_file event {crawl_event}: {ex}")

    def notify_processed_file(self, crawl_event: FileCrawledEventArgs):
        self._processed_files_size += crawl_event.size_in_mb
        self.files_processed.append(crawl_event.path)
        for observer in self.observers:
            try:
                observer.processed_file(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(
                    f"Unable to notify observer '{observer}' for notify_processed_file event {crawl_event}: {ex}")

    def notify_processing_directory(self, crawl_event: DirectoryFoundEventArgs):
        for observer in self.observers:
            try:
                observer.processing_directory(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for processing_directory event {crawl_event}: "
                             f"{ex}")

    def notify_processed_directory(self, crawl_event: DirectoryCrawledEventArgs):
        self.directories_processed.append(crawl_event.path)
        for observer in self.observers:
            try:
                observer.processed_directory(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for notify_processed_directory event "
                             f"{crawl_event}: {ex}")

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
                observer.crawl_error(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_error event {crawl_event}: {ex}")

    def notify_crawl_stopped(self, crawl_event: CrawlStoppedEventArgs):
        for observer in self.observers:
            try:
                observer.crawl_stopped(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_stopped event {crawl_event}: {ex}")

    def notify_crawl_completed(self, crawl_event: CrawlCompletedEventArgs):
        for observer in self.observers:
            try:
                observer.crawl_completed(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for crawl_completed event {crawl_event}: {ex}")

    # endregion

    def start(self):
        logger.info("Crawling is starting...")
        self._start_time = datetime.now()
        if not self.roots:
            logger.warning("No root location found to be crawled!")
            return

        total_roots = len(self.roots)
        logger.info(f"Found {total_roots} root paths to be crawled. Starting...")
        self.notify_crawl_starting(crawl_event=CrawlStartingEventArgs(crawler=self))

        try:
            # check the root paths
            for root in self.roots:
                if not self._add_path(Path(root)):
                    logger.warning(f"Not adding path '{root}'")

            for path in self._paths_to_crawl:
                path_size_in_mb, files_in_directory = self.crawl_path(path)
                logger.info(f"Crawled path '{path}' [{path_size_in_mb:0.2f} Mb / {files_in_directory} files]")
        except Exception as ex:
            logger.error(ex)
            self.notify_crawl_error(crawl_event=CrawlErrorEventArgs(crawler=self, error=ex))

        self._end_time = datetime.now()
        duration = self._end_time - self._start_time
        nb_dir_skipped = len(self._paths_skipped) - self._ignored_files
        logger.info(f"Found {len(self._crawled_paths)} paths (total of {self._crawled_files_size:0.2f} Mb) "
                    f"in {duration} sec\n"
                    f"\t- {len(self._directories_processed)} directories\n"
                    f"\t- {len(self._files_processed)} files processed (total of {self._processed_files_size:0.2f} Mb)\n"
                    f"\t- {self._ignored_files} ignored files, {nb_dir_skipped} "
                    f"director{'y' if nb_dir_skipped <= 1 else 'ies'} skipped")

        if self.require_stop:
            self.notify_crawl_stopped(crawl_event=CrawlStoppedEventArgs(crawler=self))
        else:
            self.notify_crawl_completed(crawl_event=CrawlCompletedEventArgs(crawler=self))

    def crawl_path(self, path) -> (int, int):
        path_size_in_mb = 0
        files_in_directory = 0
        if self._require_stop:
            return path_size_in_mb, files_in_directory
        try:
            entry = path.expanduser().resolve()
            entry_str = str(entry)
            self._crawled_paths.append(entry_str)

            if not entry.exists():
                logger.debug(f"File: '{entry_str}' does not exists. Ignoring.")
                return path_size_in_mb, files_in_directory

            self.notify_path_found(crawl_event=PathFoundEventArgs(crawler=self, path=path, is_file=None, is_dir=None,
                                                                  size_in_mb=-1))

            if entry.is_file():
                logger.debug(f"Crawling file: '{entry_str}'")
                files_in_directory = 1
                file_size = entry.lstat().st_size
                size_on_disk = ((int)(file_size / MIN_BLOCK_SIZE)) * MIN_BLOCK_SIZE + MIN_BLOCK_SIZE
                path_size_in_mb = convert_size_to_mb(size_on_disk)
                self.notify_processing_file(crawl_event=FileFoundEventArgs(crawler=self, path=entry,
                                                                           is_dir=entry.is_dir(),
                                                                           is_file=entry.is_file(),
                                                                           size_in_mb=path_size_in_mb))
            else:
                if entry.is_dir():
                    logger.debug(f"Crawling directory: '{entry_str}'")
                    self.notify_processing_directory(crawl_event=DirectoryFoundEventArgs(crawler=self, path=entry,
                                                                                         is_dir=entry.is_dir(),
                                                                                         is_file=entry.is_file(),
                                                                                         size_in_mb=path_size_in_mb))
            if len(self._crawled_paths) % 1000 == 0:
                self.notify_crawl_progress(crawl_event=CrawlProgessEventArgs(crawler=self))

            if any(not f.authorize(crawler=self, path=entry) for f in self.filters):
                self.notify_path_skipped(crawl_event=PathSkippedEventArgs(crawler=self, path=entry,
                                                                          is_dir=entry.is_dir(),
                                                                          is_file=entry.is_file(),
                                                                          size_in_mb=path_size_in_mb))
                logger.debug(f"Path '{entry_str}' skipped...")
                return path_size_in_mb, files_in_directory

            if entry.is_file():
                logger.debug(f"Found file: '{entry_str}'")
                self.notify_processed_file(crawl_event=FileCrawledEventArgs(crawler=self, path=entry,
                                                                            is_dir=entry.is_dir(),
                                                                            is_file=entry.is_file(),
                                                                            size_in_mb=path_size_in_mb))
            elif entry.is_dir():
                logger.debug(f"Found directory: '{entry_str}'")
                for dir_item in entry.iterdir():
                    sub_item_size_in_mb, files_in_sub_directory = self.crawl_path(dir_item)
                    path_size_in_mb += sub_item_size_in_mb
                    files_in_directory += files_in_sub_directory

                logger.info(f"Crawled directory '{entry_str}', size: {path_size_in_mb:0.2f} Mb")
                self.notify_processed_directory(crawl_event=
                                                DirectoryCrawledEventArgs(crawler=self, path=entry,
                                                                          size_in_mb=path_size_in_mb,
                                                                          files_in_dir=files_in_directory))
        except Exception as ex:
            logger.error(ex)
            self._errored_paths[str(path)] = str(ex)
            self.notify_crawl_error(crawl_event=CrawlErrorEventArgs(crawler=self, error=ex, path=path))
        return path_size_in_mb, files_in_directory
