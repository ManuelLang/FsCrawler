import os
from pathlib import Path
from typing import List

from database.data_manager import PathDataManager
from fast_crawler import FastCrawler
from interfaces.iFilter import IFilter
from models.content import ContentCategory, ContentClassificationPegi


class PersistentFilerCrawler(FastCrawler):
    """
    A file crawler that persists scanned files into database
    """

    def __init__(self, base_path: str, child_path: str, category: ContentCategory, min_age: ContentClassificationPegi,
                 data_manager: PathDataManager, fetch_file_stat: bool = True, max_lists_size: int = 10,
                 filters: List[IFilter] = [], invert_filters: bool = False):
        """
        :param base_path: The directory path of the root volume
        :param child_path: The directory path to be scanned on this volume
        :param data_manager: Providing the data manager will persist processed paths into DB
        :param fetch_file_stat: Whether the file stats needs to be loaded (i.e. size, last modified date, flags, etc...).
        Gives many additional information (and may be required by some filters); but will result in additional system call
        for every single file, resulting in 2x slower scan speed.
        See here for reference: https://www.geeksforgeeks.org/python-os-direntry-stat-method/
        :param max_lists_size: defines how many paths to keep in memory while scanning
        (i.e. empty directories, ignored files, etc...).
        The higher is the number, the slower will be the scanning process.
        :param filters: the filters to be applied in order to skip unwanted paths.
        All paths that are not authorized by any of the filter will be filtered out.
        :param invert_filters: Filters will ignore some files based on criterion. Setting this flag will invert the logic,
        i.e. will return only paths that should be filtered out. This is useful to list files & dirs to be deleted
        """
        super().__init__(base_path, child_path, category, min_age, data_manager, fetch_file_stat, max_lists_size,
                         filters, invert_filters)

        self.data_manager: PathDataManager = data_manager

    def scan_completed(self):
        super().scan_completed()

    def scan_error(self, ex: Exception):
        super().scan_error(ex)

    def scan_starting(self):
        super().scan_starting()

    def path_error(self, _path: Path, error: Exception, msg: str = None):
        super().path_error(_path, error, msg)

    def path_found(self, entry: os.DirEntry):
        super().path_found(entry)

    def empty_directory_found(self, entry: os.DirEntry):
        super().empty_directory_found(entry)

    def directory_found(self, directory: os.DirEntry):
        super().directory_found(directory)

    def file_found(self, file: os.DirEntry):
        super().file_found(file)

    def path_ignored(self, entry: os.DirEntry, filter: IFilter, is_file: bool, file_extension: str):
        super().path_ignored(entry, filter, is_file, file_extension)

    def directory_scanned(self, directory: os.DirEntry, is_empty: bool, dir_total_size: int, dir_total_files_nb: int):
        super().directory_scanned(directory, is_empty, dir_total_size, dir_total_files_nb)

    def file_scanned(self, file: os.DirEntry, entry_stat, file_extension: str):
        super().file_scanned(file, entry_stat, file_extension)


