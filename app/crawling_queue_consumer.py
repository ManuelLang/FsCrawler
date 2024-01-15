#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from queue import Queue
from threading import Lock
from typing import List, Dict

from loguru import logger

from config import config
from app.helpers.filesize_helper import format_file_size
from crawler.events.crawlCompletedEventArgs import CrawlCompletedEventArgs
from crawler.events.crawlStoppedEventArgs import CrawlStoppedEventArgs
from crawler.events.crawlerEventArgs import CrawlerEventArgs
from crawler.events.directoryCrawledEventArgs import DirectoryCrawledEventArgs
from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from crawler.events.pathEventArgs import PathEventArgs
from database.data_manager import PathDataManager
from interfaces.iCrawlingQueueConsumer import ICrawlingQueueConsumer
from interfaces.iPathProcessor import IPathProcessor
from models.directory import DirectoryModel
from models.file import FileModel
from models.path import PathModel
from models.path_type import PathType


class CrawlingQueueConsumer(ICrawlingQueueConsumer):

    def __init__(self, crawling_queue: Queue, path_processors: List[IPathProcessor] = [],
                 data_manager: PathDataManager = None, update_existing_paths: bool = False) -> None:
        """

        :param crawling_queue:
        :param path_processors:
        :param data_manager:
        :param update_existing_paths: if
        """
        super().__init__()
        if crawling_queue is None:
            raise ValueError("Please provide a Queue")
        self._crawling_queue = crawling_queue
        self._in_progress: bool = False
        self._should_stop: bool = False
        self._processed_files: List[FileModel] = []
        self._processed_directories: List[DirectoryModel] = []
        self._path_processors: List[IPathProcessor] = path_processors
        self._errored_paths: Dict[str, str] = {}
        self.data_manager = data_manager
        self._force_refresh = update_existing_paths
        self.nb_processed_paths_count = 0
        self.nb_updated_paths_count = 0
        self.processed_files_size = 0
        self.nb_running_threads: int = 0
        self.nb_completed_threads: int = 0
        self.nb_popped_items: int = 0
        self.nb_crawled_paths: int = 0

    @property
    def processed_files(self) -> List[FileModel]:
        return self._processed_files

    @property
    def processed_directories(self) -> List[DirectoryModel]:
        return self._processed_directories

    @property
    def should_stop(self) -> bool:
        return self._should_stop

    @should_stop.setter
    def should_stop(self, value: bool):
        self._should_stop = value

    def pop_item(self) -> CrawlerEventArgs:
        item: CrawlerEventArgs = None
        max_retries = config.QUEUE_WAIT_TIME
        try:
            while self._crawling_queue.empty():
                if self.should_stop:
                    break
                max_retries -= 1
                if max_retries <= 0:
                    self._should_stop = True
                    logger.warning("No more items coming into queue. Still processing popped items... "
                                   f"({self.nb_running_threads} running tasks)")
                    if item and item.crawler:
                        logger.success(f"Crawled {item.crawler.nb_files_processed} files and {item.crawler.nb_directories_processed} directories")
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
        if item and item.crawler:
            self.nb_crawled_paths = item.crawler.nb_processed_paths
        return item

    def _process_path(self, crawl_event: PathEventArgs, path_model: PathModel) -> PathModel:
        try:
            logger.debug(f"Processing {path_model.path_type.name} '{crawl_event.path}'... ({self.nb_running_threads} running tasks)")

            path_need_update: bool = True
            if not self._force_refresh and self.data_manager:
                path: PathModel = self.data_manager.get_path(path=path_model.full_path)
                if path and path == path_model:
                    path_need_update = False  # Path exists and size still the same: nothing has changed
                    logger.debug(f"Path already saved into DB: '{path_model.full_path}'. Skipping")
            if path_need_update:
                for processor in self._path_processors:
                    if processor.processor_type.name == path_model.path_type.name or processor.processor_type.name == PathType.ALL.name:
                        try:
                            logger.debug(f"\tRunning {processor.__class__.__name__}...")
                            processor.process_path(crawl_event=crawl_event, path_model=path_model)
                            logger.debug(f"\tDone processing  '{path_model.full_path}' with {processor.__class__.__name__}!")
                        except Exception as ex:
                            self._errored_paths[str(crawl_event.path)] = str(ex)
                            logger.error(f"Unable to process {path_model.path_type} '{path_model.full_path}' "
                                         f"({processor.__class__.__name__}): {ex}")
                self.nb_processed_paths_count += 1
                self.processed_files_size += crawl_event.size
                if self.data_manager:
                    if path_model.mime_type == 'inode/x-empty' and path_model.size == 0:
                        logger.debug(f"Skipping empty path '{path_model.full_path}' because it is empty")
                    else:
                        self.data_manager.save_path(path_model=path_model)
                        self.nb_updated_paths_count += 1
                        if config.LOGGING_LEVEL <= config.LOG_LEVEL_INFO:
                            logger.info(f"Done saving path '{path_model.full_path}' into DB ({format_file_size(path_model.size)})")
                        else:
                            print(":", end="")  # Show progress indicator
                else:
                    logger.debug(f"Path not saved in DB (data_manager is None): {path_model.relative_path}")

            if self.nb_completed_threads % 200 == 0 and self.nb_completed_threads > 0:
                if config.LOGGING_LEVEL >= config.LOG_LEVEL_WARNING:
                    print(".", end="")  # Show progress indicator
                else:
                    logger.success(f"Processed {self.nb_completed_threads}/{self.nb_crawled_paths} (updated {self.nb_updated_paths_count} paths) - {path_model.relative_path}")
        except Exception as exc:
            logger.error(f"Error while processing path '{crawl_event.path}': {exc}", exc)
        return path_model

    def start(self):
        self._in_progress = True
        futures = []
        with ThreadPoolExecutor(max_workers=1000) as executor:
            while True:
                if self._should_stop:
                    logger.error(f"Stopping current session... Remaining tasks: {self.nb_running_threads}")
                    break
                crawl_event = self.pop_item()
                if crawl_event is None \
                        or crawl_event.should_stop \
                        or isinstance(crawl_event, CrawlCompletedEventArgs) \
                        or isinstance(crawl_event, CrawlStoppedEventArgs):
                    self._should_stop = True
                    break

                if crawl_event.__class__.__name__ != FileCrawledEventArgs.__name__ and crawl_event.__class__.__name__ != DirectoryCrawledEventArgs.__name__:
                    logger.debug(f"Not a crawled path event: {crawl_event.__class__.__name__}")
                    continue
                path_model = crawl_event.path_model

                self.nb_running_threads, self.nb_completed_threads = running_thread_count(futures)
                logger.debug(f"Waiting for {self.nb_running_threads} tasks to complete...")
                if self.nb_running_threads > 10000:
                    while self.nb_running_threads > 1000:
                        time.sleep(5)
                        self.nb_running_threads, self.nb_completed_threads = running_thread_count(futures)
                        logger.success(f"Waiting for {self.nb_running_threads} tasks to complete...")
                futures.append(executor.submit(self._process_path, crawl_event, path_model))
                self.nb_popped_items = len(futures)

            self.nb_running_threads, self.nb_completed_threads = running_thread_count(futures)
            logger.success(f"Done pulling all tasks: waiting for {self.nb_running_threads} tasks to complete...")
            while self.nb_running_threads > 0:
                time.sleep(5)
                self.nb_running_threads, self.nb_completed_threads = running_thread_count(futures)
                logger.success(f"Waiting for current tasks to complete... Running: {self.nb_running_threads} - Completed: {self.nb_completed_threads}/{self.nb_popped_items}")

        self._in_progress = False
        # for future in as_completed(futures):
        #     path_model = future.result()
        logger.success(f"Processing files completed! Processed {len(self.processed_files)} files")


def running_thread_count(futures: List[Future]):
    running: int = 0
    completed: int = 0
    for future in futures:
        if future.running():
            running += 1
        elif future.done():
            completed += 1
    return running, completed
