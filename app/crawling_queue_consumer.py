#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Lock
from typing import List, Dict

from loguru import logger

from config import config
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
        self.paths_processed_count = 0

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

    def _process_path(self, crawl_event: PathEventArgs, path_model: PathModel) -> PathModel:
        logger.info(f"Processing {path_model.path_type.name} '{crawl_event.path}'...")
        if not self._force_refresh and self.data_manager \
                and self.data_manager.path_exists(path=path_model.full_path):
            logger.debug(f"Path already saved into DB: '{path_model.full_path}'. Skipping")
            return path_model
        for processor in self._path_processors:
            if processor.processor_type.name == path_model.path_type.name or processor.processor_type.name == PathType.ALL.name:
                try:
                    logger.info(f"\tRunning {processor.__class__.__name__}...")
                    processor.process_path(crawl_event=crawl_event, path_model=path_model)
                except Exception as ex:
                    self._errored_paths[str(crawl_event.path)] = str(ex)
                    logger.error(f"Unable to process {path_model.path_type} '{path_model}' "
                                 f"({processor.__class__.__name__}): {ex}")
        self.paths_processed_count += 1
        if config.LOGGING_LEVEL > config.LOG_LEVEL_INFO and self.paths_processed_count % 10 == 0:
            print(".", end="")  # Show progress indicator
        if self.paths_processed_count % 3000 == 0:
            print(f"\nProcessed {self.paths_processed_count} paths")
        if self.data_manager:
            self.data_manager.save_path(path_model=path_model)
            logger.info(f"Done saving path '{path_model.relative_path}' into DB")
        else:
            logger.debug(f"Path not saved in DB (data_manager is None): {path_model.relative_path}")
        return path_model

    def start(self):
        self._in_progress = True
        lock = Lock()
        with ThreadPoolExecutor(max_workers=50) as executor:
            while True:
                if self._should_stop:
                    logger.error(f"Stopping current session...")
                    executor.shutdown(wait=True, cancel_futures=True)
                    break
                crawl_event = self.pop_item()
                if crawl_event is None \
                        or crawl_event.should_stop \
                        or isinstance(crawl_event, CrawlCompletedEventArgs) \
                        or isinstance(crawl_event, CrawlStoppedEventArgs):
                    self._should_stop = True
                    break

                if crawl_event.__class__.__name__ == FileCrawledEventArgs.__name__:
                    path_model: PathModel = FileModel(root=crawl_event.root_dir_path, path=crawl_event.path,
                                                      size_in_mb=crawl_event.size_in_mb)
                elif crawl_event.__class__.__name__ == DirectoryCrawledEventArgs.__name__:
                    path_model: PathModel = DirectoryModel(root=crawl_event.root_dir_path, path=crawl_event.path,
                                                           size_in_mb=crawl_event.size_in_mb,
                                                           files_in_dir=crawl_event.files_in_dir)
                else:
                    logger.debug(f"Not a crawled path event: {crawl_event.__class__.__name__}")
                    continue

                futures = [executor.submit(self._process_path, crawl_event, path_model)]

                for future in as_completed(futures):
                    try:
                        path_model = future.result()
                        lock.acquire(blocking=True)
                        if path_model.path_type == PathType.FILE:
                            self.processed_files.append(path_model)
                        else:
                            self._processed_directories.append(path_model)
                        lock.release()
                    except Exception as exc:
                        print(f"Error while processing path '{crawl_event.path}': {exc}")

        self._in_progress = False
        logger.info(f"Processed {len(self.processed_files)} files")
