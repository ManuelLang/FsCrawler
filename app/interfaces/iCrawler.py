from abc import ABC
from datetime import time
from pathlib import Path
from typing import List


class ICrawler(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'filters') and
                callable(subclass.filters) and
                hasattr(subclass, 'observers') and
                callable(subclass.observers) and
                hasattr(subclass, 'require_stop') and
                callable(subclass.require_stop) and
                hasattr(subclass, 'paths_found') and
                callable(subclass.paths_found) and
                hasattr(subclass, 'paths_skipped') and
                callable(subclass.paths_skipped) and
                hasattr(subclass, 'files_processed') and
                callable(subclass.files_processed) and
                hasattr(subclass, 'directories_processed') and
                callable(subclass.directories_processed) and
                hasattr(subclass, 'crawled_paths') and
                callable(subclass.crawled_paths) and
                hasattr(subclass, 'crawled_files_size') and
                callable(subclass.crawled_files_size) and
                hasattr(subclass, 'start_time') and
                callable(subclass.start_time) and
                hasattr(subclass, 'end_time') and
                callable(subclass.end_time) and
                hasattr(subclass, 'crawl_in_progress') and
                callable(subclass.crawl_in_progress))

    @property
    def observers(self) -> List[object]:
        raise NotImplementedError()

    @property
    def filters(self) -> List[object]:
        raise NotImplementedError()

    @property
    def require_stop(self) -> bool:
        raise NotImplementedError()

    @property
    def paths_found(self) -> List[Path]:
        raise NotImplementedError()

    @property
    def paths_skipped(self) -> List[Path]:
        raise NotImplementedError()

    @property
    def files_processed(self) -> List[Path]:
        raise NotImplementedError()

    @property
    def directories_processed(self) -> List[Path]:
        raise NotImplementedError()

    @property
    def crawled_paths(self) -> List[str]:
        raise NotImplementedError()

    @property
    def crawled_files_size(self) -> int:
        raise NotImplementedError()

    @property
    def start_time(self) -> time:
        raise NotImplementedError()

    @property
    def end_time(self) -> time:
        raise NotImplementedError()

    @property
    def crawl_in_progress(self) -> bool:
        raise NotImplementedError()
