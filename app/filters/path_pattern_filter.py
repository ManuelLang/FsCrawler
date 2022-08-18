import re
from pathlib import Path

from app.filters.filter import Filter
from app.interfaces.iCrawler import ICrawler


class PatternFilter(Filter):

    def __init__(self, authorized_path_pattern: str = '', excluded_path_pattern: str = '',
                 regex_flags: int = re.IGNORECASE) -> None:
        super().__init__()
        self.authorized_path_pattern = authorized_path_pattern
        self.excluded_path_pattern = excluded_path_pattern
        self.regex_flags = regex_flags

    def authorize(self, crawler: ICrawler, path: Path) -> bool:
        """
        :return:
        """
        if not self.can_process(crawler, path):
            return True

        if self.excluded_path_pattern:
            if path.match(self.excluded_path_pattern):
                return False

        if self.authorized_path_pattern:
            if not path.match(self.authorized_path_pattern):
                return False

        return True

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict.update({
            "filter": self.__class__.__name__,
            "authorized_path_pattern": self.authorized_path_pattern,
            "excluded_path_pattern": self.excluded_path_pattern,
            "regex_flags": self.regex_flags
        })
        return json_dict

    def __eq__(self, o: object) -> bool:
        if o is None or o.__class__.__name__ != PatternFilter.__name__ or not isinstance(o, PatternFilter):
            return False
        return self.authorized_path_pattern == o.authorized_path_pattern \
               and self.excluded_path_pattern == o.excluded_path_pattern \
               and self.regex_flags == o.regex_flags

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.to_json())))
