#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from loguru import logger

from config import config
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
from helpers.filesize_helper import *
from helpers.serializationHelper import JsonDumper
from interfaces.iCrawler import ICrawler
from interfaces.iCrawlerObserver import ICrawlerObserver
from interfaces.iFilter import IFilter

from helpers.filesize_helper import format_file_size

from models.content import ContentCategory, ContentClassificationPegi

MIN_BLOCK_SIZE = 1024 * 4
MAX_LAST_N_ITEMS_TO_KEEP = 2000


class FileSystemCrawler(ICrawler):

    def __init__(self, roots: Dict[str, dict], skip_filters: List[IFilter] = [], notify_filters: List[IFilter] = [],
                 observers: List[ICrawlerObserver] = []) -> None:
        """
        Create a new instance of crawler to browse  file system on a machine
        :param roots: the base directories to scan. A dict is expected as <Base_Directory, Path_Part_To_Ignore>.
        The `Path_Part_To_Ignore` is useful when workingon network drive, mapped volumes or any case when you want to get rid of path prefix
        :param skip_filters: a set of rules to teach the crawler to ignore some paths based on criterion. This crawler will walk through the directories and subdirs as long a no filters prevents it.
         When a filter prevents it, all sub-dirs are ignored. Notifications are sent each time a file/directory is authorized by all skip_filters (applies AND amongst filters).
        :param observers: defines what  component to notify when files/directories are found
        :param notify_filters: This crawler will walk through all the directories and subdirs (as allowed by skip_filters).
        If notify_filters is set, notifications are sent only when the current path matches any of the filters.
        """
        super().__init__()
        self.roots: Dict[str, dict] = roots
        self._skip_filters: List[IFilter] = skip_filters
        self._notify_filters: List[IFilter] = notify_filters
        self._observers: List[ICrawlerObserver] = observers
        self._require_stop = False
        self._paths_to_crawl: Dict[Path, dict] = {}

        # stats
        self._paths_found: List[Path] = []
        self._nb_paths_found: int = 0
        self._paths_skipped: List[Path] = []
        self._nb_paths_skipped: int = 0
        self._files_processed: List[Path] = []
        self._nb_files_processed: int = 0
        self._directories_processed: List[Path] = []
        self._nb_directories_processed: int = 0
        self._errored_paths: Dict[str, str] = defaultdict(str)
        self._nb_errored_paths: int = 0
        self._crawled_paths: List[str] = []
        self._crawled_roots: List[str] = []
        self._crawled_files_size: int = 0
        self._processed_files_size: int = 0
        self._nb_ignored_files: int = 0
        self._nb_ignored_dirs: int = 0
        self._nb_processed_paths: int = 0
        self._start_time: datetime = None
        self._end_time: datetime = None
        self.duration = 0

    def add_skip_filter(self, path_filter: IFilter):
        if not path_filter:
            raise ValueError("Missing argument 'path_filter'")
        if path_filter not in self.skip_filters:
            self.skip_filters.append(path_filter)
        return self

    def add_skip_filters(self, skip_filters: List[IFilter]):
        for f in skip_filters:
            self.add_skip_filter(f)
        return self

    @property
    def skip_filters(self) -> List[IFilter]:
        return self._skip_filters

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
    def nb_paths_found(self) -> int:
        return self._nb_paths_found

    @property
    def nb_processed_paths(self) -> int:
        return self._nb_processed_paths

    @property
    def paths_found(self) -> List[Path]:
        self._paths_found = self._paths_found[-MAX_LAST_N_ITEMS_TO_KEEP:]
        return self._paths_found

    @property
    def nb_paths_skipped(self) -> int:
        return self._nb_paths_skipped

    @property
    def paths_skipped(self) -> List[Path]:
        self._paths_skipped = self._paths_skipped[-MAX_LAST_N_ITEMS_TO_KEEP:]
        return self._paths_skipped

    @property
    def nb_files_processed(self) -> int:
        return self._nb_files_processed

    @property
    def files_processed(self) -> List[Path]:
        self._files_processed = self._files_processed[-MAX_LAST_N_ITEMS_TO_KEEP:]
        return self._files_processed

    @property
    def nb_directories_processed(self) -> int:
        return self._nb_directories_processed

    @property
    def directories_processed(self) -> List[Path]:
        self._directories_processed = self._directories_processed[-MAX_LAST_N_ITEMS_TO_KEEP:]
        return self._directories_processed

    @property
    def nb_crawled_paths(self) -> int:
        return self._nb_paths_found

    @property
    def crawled_paths(self) -> List[str]:
        reversed(self._crawled_paths)
        self._crawled_paths = self._crawled_paths[-MAX_LAST_N_ITEMS_TO_KEEP:]
        return self._crawled_paths

    @property
    def crawled_files_size(self) -> int:
        return self._crawled_files_size

    @property
    def processed_files_size(self) -> int:
        return self._processed_files_size

    @property
    def nb_errored_paths(self) -> int:
        return self._nb_errored_paths

    @property
    def errored_paths(self) -> Dict[str, str]:
        self._errored_paths = self._errored_paths[-MAX_LAST_N_ITEMS_TO_KEEP:]
        return self._errored_paths

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def end_time(self) -> datetime:
        return self._end_time

    @property
    def nb_files_skipped(self) -> int:
        return self._nb_ignored_files

    @property
    def nb_directories_skipped(self) -> int:
        return self._nb_ignored_dirs

    # endregion

    @property
    def crawl_in_progress(self) -> bool:
        return self._start_time is not None and self._end_time is None

    def _add_path(self, path: Path, root_dir: str, root_category: ContentCategory,
                  root_min_age: ContentClassificationPegi, root_target_table: str) -> bool:
        path = path.expanduser().resolve(strict=True)
        str_path = str(path)

        # check if path is not added, or is not a sub-path
        if not path.is_dir():
            raise ValueError(f"The path '{str_path}' is not a directory")

        for paths, root_path_dir in self._paths_to_crawl.items():
            if str_path.startswith(str(paths)):
                return False

        for pp in self._crawled_roots:
            if pp.startswith(str_path):
                return False

        self._paths_to_crawl[path] = {
            'root': root_dir,
            'category': root_category,
            'min_age': root_min_age,
            'target_table': root_target_table,
        }
        if root_dir not in self._crawled_roots:
            self._crawled_roots.append(root_dir)
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
        self._nb_paths_found += 1
        for observer in self.observers:
            try:
                observer.path_found(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for path_found event {crawl_event}: {ex}")

    def notify_path_skipped(self, crawl_event: PathSkippedEventArgs):
        self.paths_skipped.append(crawl_event.path)
        self._nb_paths_skipped += 1
        if crawl_event.is_file:
            self._nb_ignored_files += 1
        elif crawl_event.is_dir:
            self._nb_ignored_dirs += 1
        for observer in self.observers:
            try:
                observer.path_skipped(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for path_skipped event {crawl_event}: {ex}")

    def notify_processing_file(self, crawl_event: FileFoundEventArgs):
        self._crawled_files_size += crawl_event.size
        for observer in self.observers:
            try:
                observer.processing_file(crawl_event)
                if crawl_event.should_stop:
                    self.stop()
            except Exception as ex:
                logger.error(f"Unable to notify observer '{observer}' for processing_file event {crawl_event}: {ex}")

    def notify_processed_file(self, crawl_event: FileCrawledEventArgs):
        self._processed_files_size += crawl_event.size
        self._nb_files_processed += 1
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
        self._nb_directories_processed += 1
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
        logger.success("Crawling is starting...")
        self._start_time = datetime.now()
        if not self.roots:
            logger.warning("No root location found to be crawled!")
            return

        total_roots = len(self.roots)
        logger.info(f"Found {total_roots} root paths to be crawled:")
        logger.info(self.roots)
        logger.info("Filters applied:")
        for f in self.skip_filters:
            logger.info(f)
        logger.info("Start browsing files...")
        self.notify_crawl_starting(crawl_event=CrawlStartingEventArgs(crawler=self))

        # try:
        # check the root paths
        for path, root_obj in self.roots.items():
            root_dir: str = root_obj.get('root')
            root_category: ContentCategory = root_obj.get('category', None)
            root_min_age: ContentClassificationPegi = root_obj.get('min_age', ContentClassificationPegi.EIGHTEEN_OR_MORE)
            root_target_table: str = root_obj.get('target_table', 'path')
            if not self._add_path(Path(path), root_dir, root_category, root_min_age, root_target_table):
                logger.warning(f"Not adding path '{path}'")

        for path, attrs_dict in self._paths_to_crawl.items():
            path_size, files_in_directory = self.crawl_path(path=path, root_dir=attrs_dict['root'],
                                                            category=attrs_dict['category'],
                                                            min_age=attrs_dict['min_age'],
                                                            target_table=attrs_dict['target_table'])
            logger.success(f"Crawled path '{path}' [{format_file_size(path_size)} / {files_in_directory} files]")
        # except Exception as ex:
        #     logger.error(ex)
        #     self.notify_crawl_error(crawl_event=CrawlErrorEventArgs(crawler=self, error=ex))

        self._end_time = datetime.now()
        self.duration = self._end_time - self._start_time
        logger.success(f"Found {self._nb_paths_found} paths (total of {format_file_size(self._crawled_files_size)})"
                    f"in {self.duration} sec\n"
                    f"\t- {self._nb_directories_processed} directories\n"
                    f"\t- {self._nb_files_processed} files processed (total of {format_file_size(self._processed_files_size)})\n"
                    f"\t- {self._nb_ignored_files} ignored files, {self._nb_ignored_dirs} "
                    f"director{'y' if self._nb_ignored_dirs <= 1 else 'ies'} skipped")

        if self.require_stop:
            self.notify_crawl_stopped(crawl_event=CrawlStoppedEventArgs(crawler=self))
        else:
            self.notify_crawl_completed(crawl_event=CrawlCompletedEventArgs(crawler=self))

    def crawl_path(self, path: Path, root_dir: str, category: ContentCategory, min_age: ContentClassificationPegi,
                   target_table: str) -> (int, int):
        path_size = 0
        files_in_directory = 0
        if self._require_stop:
            return path_size, files_in_directory
        #try:
        entry = path.expanduser().resolve()
        entry_str = str(entry)
        self._crawled_paths.append(entry_str)
        if len(self._crawled_paths) > MAX_LAST_N_ITEMS_TO_KEEP:
            self._crawled_paths = self.crawled_paths

        if not entry.exists():
            logger.debug(f"File: '{entry_str}' does not exists. Ignoring.")
            return path_size, files_in_directory

        self.notify_path_found(crawl_event=PathFoundEventArgs(crawler=self, path=path, root_dir_path=root_dir,
                                                              is_dir=None, is_file=None, size=-1))
        self._nb_processed_paths += 1
        if entry.is_file():
            logger.debug(f"Crawling file: '{entry_str}'")
            files_in_directory = 1
            file_size = entry.lstat().st_size
            # size_on_disk = ((int)(file_size / MIN_BLOCK_SIZE)) * MIN_BLOCK_SIZE + MIN_BLOCK_SIZE
            # path_size = convert_size_to_mb(size_on_disk)
            path_size = file_size
            self.notify_processing_file(crawl_event=FileFoundEventArgs(crawler=self, path=entry,
                                                                       size=path_size,
                                                                       root_dir_path=root_dir))
        else:
            if entry.is_dir():
                logger.debug(f"Crawling directory: '{entry_str}'")
                self.notify_processing_directory(crawl_event=DirectoryFoundEventArgs(crawler=self, path=entry,
                                                                                     size=path_size,
                                                                                     root_dir_path=root_dir))
        if self._nb_paths_found % 1000 == 0 and self._nb_paths_found > 0:
            self.notify_crawl_progress(crawl_event=CrawlProgessEventArgs(crawler=self))
            if config.LOGGING_LEVEL >= config.LOG_LEVEL_WARNING:
                print(".", end="")  # Show progress indicator
            else:
                logger.success(f"Found {self._nb_paths_found} paths so far...")

        should_skip = False
        for f in self.skip_filters:
            if not f.authorize(path=entry):
                should_skip = True
                logger.debug(f"should_skip set to True by {f} for path {entry}")
                break
        if should_skip:
            self.notify_path_skipped(crawl_event=PathSkippedEventArgs(crawler=self, path=entry,
                                                                      is_dir=entry.is_dir(),
                                                                      is_file=entry.is_file(),
                                                                      size=path_size,
                                                                      root_dir_path=root_dir))
            logger.debug(f"Path '{entry_str}' skipped...")
            return path_size, files_in_directory

        # FIND mode: notify when path matches any of the notify_filters
        should_notify = not self._notify_filters
        for f in self._notify_filters:
            if f.authorize(path=entry):
                should_notify = True
                logger.debug(f"should_notify set to True by {f} for path {entry}")
                break

        if entry.is_file():
            logger.debug(f"Found file: '{entry_str}'")
            if should_notify:
                self.notify_processed_file(crawl_event=FileCrawledEventArgs(crawler=self, path=entry,
                                                                            root_dir_path=root_dir,
                                                                            size=path_size,
                                                                            root_category=category,
                                                                            root_min_age=min_age,
                                                                            root_target_table=target_table))
        elif entry.is_dir():
            logger.debug(f"Found directory: '{entry_str}'")
            dir_direct_children_files: List[str] = []
            for dir_item in entry.iterdir():
                if not dir_item.is_dir():
                    dir_direct_children_files.append(dir_item.name)

                sub_item_size, files_in_sub_directory = self.crawl_path(dir_item, root_dir, category, min_age, target_table)
                path_size += sub_item_size
                files_in_directory += files_in_sub_directory

            logger.info(f"Crawled directory '{entry_str}', size: {format_file_size(path_size)}")
            if should_notify:
                self.notify_processed_directory(crawl_event=
                                                DirectoryCrawledEventArgs(crawler=self, path=entry,
                                                                          size=path_size,
                                                                          files_in_dir=files_in_directory,
                                                                          root_dir_path=root_dir,
                                                                          file_names=dir_direct_children_files,
                                                                          root_category=category,
                                                                          root_min_age=min_age,
                                                                          root_target_table=target_table))
        # except Exception as ex:
        #     logger.error(ex)
        #     self._errored_paths[str(path)] = str(ex)
        #     self.notify_crawl_error(crawl_event=CrawlErrorEventArgs(crawler=self, error=ex, path=path))
        return path_size, files_in_directory

    def to_json(self) -> dict:
        return {
            "roots": self.roots,
            "filters": self.skip_filters,
            "observers": self.observers,
            "paths_found": self.nb_paths_found,
            "paths_skipped": self.nb_paths_skipped,
            "files_processed": self.nb_files_processed,
            "directories_processed": self.nb_directories_processed,
            "crawled_paths": self.nb_crawled_paths,
            "crawled_files_size": format_file_size(self.crawled_files_size),
            "processed_files_size": format_file_size(self.processed_files_size),
            "errored_paths": self.nb_errored_paths,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "nb_files_skipped": self.nb_files_skipped,
            "nb_directories_skipped": self.nb_directories_skipped,
            "crawl_in_progress": self.crawl_in_progress,
            "require_stop": self._require_stop
        }

    def __str__(self) -> str:
        return JsonDumper.dumps(self.to_json())
