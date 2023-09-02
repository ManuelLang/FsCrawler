#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from pathlib import Path

from app.filters.path_pattern_filter import PatternFilter
from app.interfaces.iCrawler import ICrawler


class FilePatternFilter(PatternFilter):

    def __init__(self, authorized_path_pattern: str = '', excluded_path_pattern: str = '') -> None:
        super().__init__(authorized_path_pattern=authorized_path_pattern, excluded_path_pattern=excluded_path_pattern)

    def authorize(self, crawler: ICrawler, path: Path) -> bool:
        if not self.can_process(crawler, path):
            return False
        if path.is_dir():
            authorize = self in crawler.skip_filters  # Allow to process any directory and subdirs
            return authorize
        return super(FilePatternFilter, self).authorize(crawler=crawler, path=path)  # Filter only files
