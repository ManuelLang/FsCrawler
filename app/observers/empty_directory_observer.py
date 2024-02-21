#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from typing import Dict, List

from loguru import logger

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
from helpers.filesize_helper import format_file_size
from interfaces.iCrawlerObserver import ICrawlerObserver
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType


class EmptyDirectoryObserver(ICrawlerObserver):

    def __init__(self):
        super().__init__()
        self.empty_dirs = []

    def crawl_starting(self, crawl_event: CrawlStartingEventArgs):
        pass

    def path_found(self, crawl_event: PathFoundEventArgs):
        pass

    def path_skipped(self, crawl_event: PathSkippedEventArgs):
        pass

    def processing_file(self, crawl_event: FileFoundEventArgs):
        pass

    def processed_file(self, crawl_event: FileCrawledEventArgs):
        pass

    def processing_directory(self, crawl_event: DirectoryFoundEventArgs):
        pass

    def processed_directory(self, crawl_event: DirectoryCrawledEventArgs):
        empty_dir = crawl_event.files_in_dir < 1 and crawl_event.size < 1
        if not empty_dir and crawl_event.file_names and len(crawl_event.file_names) == 1:
            # https://stackoverflow.com/questions/15835213/list-of-various-system-files-safe-to-ignore-when-implementing-a-virtual-file-sys
            empty_dir = crawl_event.file_names[0] in ['.DS_Store', '._.DS_Store', 'Thumbs.db', 'thumbs.db', 'Desktop.ini', 'desktop.ini', '@easyno', 'ehthumbs.db']
        full_path = str(crawl_event.path)
        if empty_dir and full_path not in self.empty_dirs:
            self.empty_dirs.append(full_path)

    def crawl_progress(self, crawl_event: CrawlProgessEventArgs):
        pass

    def crawl_error(self, crawl_event: CrawlErrorEventArgs):
        pass

    def crawl_stopped(self, crawl_event: CrawlStoppedEventArgs):
        pass

    def crawl_completed(self, crawl_event: CrawlCompletedEventArgs):
        if self.empty_dirs:
            msg = "Found empty directories (top 50):\n"
            i: int = 0
            for dir_name in self.empty_dirs:
                i += 1
                if i > 50:
                    break
                msg += f"{i:02} {dir_name}\n"
            logger.warning(msg)


