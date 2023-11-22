#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from collections import defaultdict, OrderedDict
from typing import List, Dict

from loguru import logger
from more_itertools import take

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
from interfaces.iCrawlerObserver import ICrawlerObserver

from app.models.path import PathModel


class MetricsObserver(ICrawlerObserver):

    def __init__(self) -> None:
        super().__init__()
        self._found_extensions: List[str] = []
        self._paths_depth: Dict[int, List[str]] = defaultdict(list)
        self._paths_length: Dict[int, str] = defaultdict()
        self._crawled_extensions: List[str] = []
        self._directories_sizes: Dict[int, str] = {}
        self._empty_directories: List[str] = []
        self._skipped_files_size: int = 0

    @property
    def extensions_found(self) -> List[str]:
        return [e for e in sorted(list(set(self._found_extensions))) if e]

    @property
    def extensions_crawled(self) -> List[str]:
        return [e for e in sorted(list(set(self._crawled_extensions))) if e]

    @property
    def deepest_paths(self, top_n: int = 10) -> Dict[int, List[str]]:
        top_depth = OrderedDict(sorted(self._paths_depth.items(), reverse=True))
        result = dict(take(top_n, top_depth.items()))
        return result

    @property
    def biggest_directories(self, top_n: int = 10) -> Dict[int, List[str]]:
        top_size = OrderedDict(sorted(self._directories_sizes.items(), reverse=True))
        result = dict(take(top_n, top_size.items()))
        return result

    @property
    def empty_directories(self, top_n: int = 10) -> List[str]:
        top_size = sorted(self._empty_directories)
        result = take(top_n, top_size)
        return result

    @property
    def longest_paths(self, top_n: int = 10) -> Dict[int, List[str]]:
        top_length = OrderedDict(sorted(self._paths_length.items(), reverse=True))
        result = dict(take(top_n, top_length.items()))
        return result

    @property
    def skipped_files_total_size(self) -> int:
        return self._skipped_files_size

    def print_statistics(self):
        logger.success(f"Files extensions found ({len(self.extensions_found)}): {', '.join(self.extensions_found)}")
        ext_diff = list(set(self.extensions_found) - set(self.extensions_crawled))
        inverse_diff = list(set(self.extensions_crawled) - set(self.extensions_found))
        if inverse_diff:
            logger.error(f"Some extensions were not recorded as found but are crawled. Please check this out: {inverse_diff}")
        logger.success(f"Files extensions ignored ({len(ext_diff)}): {', '.join(sorted(ext_diff))}")
        logger.success(f"Files extensions crawled ({len(self.extensions_crawled)}): {', '.join(self.extensions_crawled)}")
        logger.success(f"Total size of skipped files: {self.skipped_files_total_size:.2f} Mb")
        logger.success("Deepest paths:")
        for depth, path_list in self.deepest_paths.items():
            logger.success(f"depth: {depth} ({len(path_list)} items)\n\texemple: {path_list[0]}")
            # for path in path_list:
            #     logger.success(f"\n\t{path}")
        logger.success("Biggest directories (Top 10, in Mb):")
        for size, path in self.biggest_directories.items():
            logger.success(f"\t{size:.2f} Mb\t\t{path}")
        if self.empty_directories:
            logger.success(f"{len(self._empty_directories)} empty directories. Top 10:")
            for dir_name in self.empty_directories:
                logger.success(dir_name)
        paths_too_long = {length: path for length, path in self.longest_paths.items() if length >= 255}
        if paths_too_long:
            logger.success("Path too long:")
            for length, path in paths_too_long.items():
                logger.warning(f"\t{length} chars\t\t{path}")
        logger.success("Done printing stats")

    def path_found(self, crawl_event: PathFoundEventArgs):
        if crawl_event.is_file:
            file_extension = crawl_event.path.suffix
            if not crawl_event.path.suffix:
                file_extension = crawl_event.path.stem
            if file_extension not in self._found_extensions:
                self._found_extensions.append(str(file_extension).lower())
        str_path = str(crawl_event.path)
        depth = len(list(crawl_event.path.parts)) - 1  # remove first '/'
        paths_list = self._paths_depth.get(depth, [])
        if str_path not in paths_list:
            paths_list.append(str_path)
        self._paths_depth[depth] = paths_list
        if str_path not in self._paths_length:
            self._paths_length[len(str_path)] = str_path

    def path_skipped(self, crawl_event: PathSkippedEventArgs):
        if crawl_event.is_file:
            self._skipped_files_size += crawl_event.size_in_mb

    def processed_file(self, crawl_event: FileCrawledEventArgs):
        if crawl_event.__class__.__name__ != FileCrawledEventArgs.__name__ and crawl_event.__class__.__name__ != DirectoryCrawledEventArgs.__name__:
            return
        path_model: PathModel = crawl_event.path_model
        if path_model and path_model.extension and path_model.extension not in self._crawled_extensions:
            self._crawled_extensions.append(path_model.extension)

    def processed_directory(self, crawl_event: DirectoryCrawledEventArgs):
        self._directories_sizes[crawl_event.size_in_mb] = str(crawl_event.path)
        if crawl_event.files_in_dir < 1 and crawl_event.size_in_mb < 1:
            self._empty_directories.append(str(crawl_event.path))

    def crawl_stopped(self, crawl_event: CrawlStoppedEventArgs):
        logger.warning("crawl_stopped")
        self.print_statistics()

    def crawl_completed(self, crawl_event: CrawlCompletedEventArgs):
        logger.success("crawl_completed")
        self.print_statistics()

    def crawl_starting(self, crawl_event: CrawlStartingEventArgs):
        pass

    def processing_file(self, crawl_event: FileFoundEventArgs):
        pass

    def processing_directory(self, crawl_event: DirectoryFoundEventArgs):
        pass

    def crawl_progress(self, crawl_event: CrawlProgessEventArgs):
        pass

    def crawl_error(self, crawl_event: CrawlErrorEventArgs):
        pass
