from filters.date_filter import DateFilter
from filters.depth_filter import DepthFilter
from filters.extension_filter import ExtensionFilter
from filters.file_pattern_filter import FilePatternFilter
from filters.filter import Filter
from filters.path_name_ignore_filter import NameFilter
from filters.path_pattern_filter import PatternFilter
from filters.path_regex_pattern_filter import RegexPatternFilter
from filters.size_filter import SizeFilter


class FilterFactory:

    @staticmethod
    def get_filter(filter_name, **args) -> Filter:
        if not filter_name:
            return None
        filter_name = filter_name.lower().strip()
        if DateFilter.__name__.lower() == filter_name:
            return DateFilter(**args)
        if DepthFilter.__name__.lower() == filter_name:
            return DepthFilter(**args)
        if ExtensionFilter.__name__.lower() == filter_name:
            return ExtensionFilter(**args)
        if FilePatternFilter.__name__.lower() == filter_name:
            return FilePatternFilter(**args)
        if NameFilter.__name__.lower() == filter_name:
            return NameFilter(**args)
        if PatternFilter.__name__.lower() == filter_name:
            return PatternFilter(**args)
        if RegexPatternFilter.__name__.lower() == filter_name:
            return RegexPatternFilter(**args)
        if SizeFilter.__name__.lower() == filter_name:
            return SizeFilter(**args)
        return None