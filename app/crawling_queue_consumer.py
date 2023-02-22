#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import time
from queue import Queue
from typing import List, Dict

from loguru import logger

from crawler.events.crawlCompletedEventArgs import CrawlCompletedEventArgs
from crawler.events.crawlStoppedEventArgs import CrawlStoppedEventArgs
from crawler.events.crawlerEventArgs import CrawlerEventArgs
from crawler.events.directoryCrawledEventArgs import DirectoryCrawledEventArgs
from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from crawler.events.pathEventArgs import PathEventArgs
from interfaces.iCrawlingQueueConsumer import ICrawlingQueueConsumer
from interfaces.iPathProcessor import IPathProcessor
from models.directory import DirectoryModel
from models.file import FileModel
from models.path import PathModel
from models.path_type import PathType


class CrawlingQueueConsumer(ICrawlingQueueConsumer):

    def __init__(self, crawling_queue: Queue, path_processors: List[IPathProcessor] = []) -> None:
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

    def _process_path(self, crawl_event: PathEventArgs, path_model: PathModel):
        logger.info(f"Processing {path_model.path_type.name} '{crawl_event.path}'...")
        for processor in self._path_processors:
            if processor.processor_type == path_model.path_type or processor.processor_type == PathType.ALL:
                try:
                    processor.process_path(crawl_event=crawl_event, path_model=path_model)
                except Exception as ex:
                    self._errored_paths[str(crawl_event.path)] = str(ex)
                    logger.error(f"Unable to process {path_model.path_type} '{path_model}' "
                                 f"({processor.__class__.__name__}): {ex}")

    def start(self):
        self._in_progress = True
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
                file: FileModel = FileModel(path=crawl_event.path, size_in_mb=crawl_event.size_in_mb)
                self._process_path(crawl_event=crawl_event, path_model=file)
                self.processed_files.append(file)
            elif isinstance(crawl_event, DirectoryCrawledEventArgs):
                dir: DirectoryModel = DirectoryModel(path=crawl_event.path, size_in_mb=crawl_event.size_in_mb)
                self._process_path(crawl_event=crawl_event, path_model=dir)
                self._processed_directories.append(dir)
        self._in_progress = False
        logger.info(f"Processed {len(self.processed_files)} files")
