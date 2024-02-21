import os, sys
import re
import time
from pathlib import Path
from typing import List
from loguru import logger

from database.data_manager import PathDataManager
from filters.extension_filter import ExtensionFilter
from filters.path_name_ignore_filter import NameFilter
from filters.path_pattern_filter import PatternFilter
from filters.path_regex_pattern_filter import RegexPatternFilter
from interfaces.iFilter import IFilter
from models.content import ContentCategory, ContentClassificationPegi
from models.path_stage import PathStage

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

from config import config


class FastCrawler:

    def __init__(self, base_path: str, child_path: str, category: ContentCategory, min_age: ContentClassificationPegi,
                 data_manager: PathDataManager, fetch_file_stat: bool = True,
                 max_lists_size: int = 10, filters: List[IFilter] = [], invert_filters: bool = False):
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
        super().__init__()
        if not base_path:
            raise ValueError('base_path is mandatory: please provide the root path of the location to be scanned')
        self.base_path = base_path if base_path.endswith('/') else f"{base_path}/"
        if not self.base_path.startswith('/'):
            self.base_path = f"/{self.base_path}"

        if not child_path:
            raise ValueError('child_path is mandatory: please provide the path of the directory to be scanned, from the root location')
        self.child_path = child_path
        if self.child_path.startswith('/'):
            self.child_path = self.child_path[1:]
        if self.child_path.endswith('/'):
            self.child_path = self.child_path[:-1]

        self.path_to_scan = f"{self.base_path}{self.child_path}"
        p: Path = Path(self.path_to_scan)
        if not p.exists():
            raise ValueError(f"The Path '{p}' does not exists")
        if not p.is_dir():
            raise ValueError(f"The Path '{p}' is not a directory")
        logger.success(f"Set path to scan: '{self.path_to_scan}'")
        self.path_to_scan = p.expanduser().resolve()

        self.category = category
        self.min_age = min_age

        self.data_manager = data_manager

        self.fetch_file_stat = fetch_file_stat
        self.invert_filters = invert_filters
        self.max_lists_size = max_lists_size
        self.filters = filters

        self.total_files = 0
        self.total_size = 0

        self.found_dirs = 0
        self.ignored_dirs = 0
        self.scanned_dirs = 0
        self.found_files = 0
        self.ignored_files = 0
        self.scanned_files = 0
        self.empty_dirs = 0
        self.ignored_files_list = set()
        self.ignored_dirs_list = set()
        self.ignored_extensions_list = set()
        self.scanned_extensions_list = set()
        self.empty_dirs_list = set()
        self.errored_paths = {}

    def should_skip_path(self, entry: os.DirEntry, stat: os.stat_result = None) -> (str, bool):
        file_extension = str(entry.name.split('.')[-1]).lower() if entry.is_file(follow_symlinks=False) else None
        should_skip = False
        if self.filters:
            for f in self.filters:
                if not f.authorize(entry=entry, stat=stat):
                    should_skip = True
                    logger.debug(f"should_skip set to True by {f} for path {entry}")
                    break
        if self.invert_filters:
            should_skip = not should_skip
        return file_extension, should_skip

    def scan(self):
        _start = time.time()
        if self.data_manager:
            with self.data_manager.create_cursor() as cur:
                self.total_size, self.total_files = self._get_tree_size(path=self.path_to_scan, cursor=cur)
                # Save as well root dir stats
                self.data_manager._save_path(cursor=cur, full_path=str(self.path_to_scan), extension=None,
                                             name=self.path_to_scan.name, is_dir=True, files_in_dir=self.total_files,
                                             size=self.total_size, stage=PathStage.CRAWLED,
                                             category=self.category, min_age=self.min_age)
                cur.connection.commit()
        else:
            self.total_size, self.total_files = self._get_tree_size(path=self.path_to_scan, cursor=None)
        _end = time.time()
        _duration = _end - _start
        logger.success(f"Total size: {round(self.total_size / 1024 / 1024 / 1024, 3)} Go - "
                       f"Scanned {self.total_files} files / Skipped {fc.ignored_files} files in {_duration:.2f} sec")
        if self.errored_paths:
            logger.error(f"Error happened for scanning {len(self.errored_paths)} paths:")
            for path, error in self.errored_paths.items():
                logger.error(f"{path}: {error}")

    def _get_tree_size(self, path, cursor) -> (int, int):
        """Return total size of files in path and subdirs.
        Assume zero size if stat errors (for example, file has been deleted).
        """
        dir_total_size = 0
        dir_total_files_nb = 0
        # scandir is the fastest way to iterate over filesystem: https://peps.python.org/pep-0471/
        for entry in os.scandir(path):
            try:
                try:
                    is_dir = entry.is_dir(follow_symlinks=False)
                except OSError as error:
                    msg = f"Error calling is_dir() for path '{path}'. Error: {error}"
                    self.errored_paths[path] = msg
                    continue
                if is_dir:
                    self.found_dirs += 1
                    file_extension, ignore = self.should_skip_path(entry)
                    # ignore = False
                    if ignore:
                        logger.debug(f"Ignoring directory '{entry.path}'")
                        self.ignored_dirs += 1
                        if self.ignored_dirs < self.max_lists_size:
                            self.ignored_dirs_list.add(entry.path)
                        continue
                    sub_dir_total_size, sub_dir_total_files_nb = self._get_tree_size(entry.path, cursor)
                    if sub_dir_total_size < 1 and sub_dir_total_files_nb < 1:
                        self.empty_dirs += 1
                        if self.empty_dirs < self.max_lists_size:
                            self.empty_dirs_list.add(entry.path)
                    dir_total_size += sub_dir_total_size
                    dir_total_files_nb += sub_dir_total_files_nb
                    self.scanned_dirs += 1
                    if cursor:
                        self.data_manager._save_path(cursor=cursor, full_path=entry.path, extension=None,
                                                     name=entry.name, is_dir=True, files_in_dir=dir_total_files_nb,
                                                     size=dir_total_size, stage=PathStage.CRAWLED,
                                                     category=self.category, min_age=self.min_age)
                    logger.debug(f"Scanned dir '{entry.path}'")
                    if self.scanned_dirs % 10000 == 0:
                        logger.success(f"Scanned {self.scanned_files} files / {self.scanned_dirs} dirs")
                        if cursor:
                            cursor.connection.commit()
                else:
                    try:
                        self.found_files += 1
                        file_extension, ignore = self.should_skip_path(entry)
                        if ignore:
                            logger.debug(f"Ignoring file '{entry.path}'")
                            self.ignored_files += 1
                            if self.ignored_files < self.max_lists_size:
                                self.ignored_files_list.add(entry.path)
                            self.ignored_extensions_list.add(file_extension)
                            continue
                        if file_extension:
                            self.scanned_extensions_list.add((file_extension, entry.path))
                        entry_stat = None
                        size = None
                        if self.fetch_file_stat:
                            entry_stat = entry.stat(follow_symlinks=False)
                            size = entry_stat.st_size
                            dir_total_size += size
                        dir_total_files_nb += 1
                        self.scanned_files += 1
                        if cursor:
                            self.data_manager._save_path(cursor=cursor, full_path=entry.path, extension=file_extension,
                                                         name=entry.name, is_dir=False, files_in_dir=None,
                                                         size=size, stage=PathStage.CRAWLED,
                                                         category=self.category, min_age=self.min_age)
                        if self.scanned_files % 5000 == 0:
                            logger.info(f"Scanned {self.scanned_files} files / {self.scanned_dirs} dirs")
                            if cursor:
                                cursor.connection.commit()
                        elif self.scanned_files % 10000 == 0:
                            logger.success(f"Scanned {self.scanned_files} files / {self.scanned_dirs} dirs")
                    except OSError as error:
                        msg = f"Error calling stat() for path '{path}'. Error: {error}"
                        self.errored_paths[path] = msg
                        continue
            except Exception as ex:
                self.errored_paths[entry.path] = str(ex)
        return dir_total_size, dir_total_files_nb


if __name__ == '__main__':
    base_volume = '/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b1/'
    dev_dir = "/Développement/"
    test_dir = "Développement/Dev/v3.5/src/trunk/Evaluant.Uss.DomainModel/ClassModel"

    filters: List[IFilter] = []
    filters.append(NameFilter(excluded_names={".idea", ".Trashes", "out", ".idea_modules", "build", "dist", "lib", "venv",
                          ".pyenv", "python", "bin", "obj", "debug", ".git", "@angular", "node_modules",
                          "botocore", "boto3", ".terraform", ".terraformrc", "package", "target",
                          "__pycache__", "mypy_boto3_builder", ".gradle", ".mvn", ".npm", ".nvm",
                          ".npm-packages", ".node-gyp", ".node_repl_history", ".m2", ".plugins", ".cache",
                          ".docker", "dockervolumes", "jenkins", ".eclipse", ".Trash", ".krew", "kube",
                          ".android", ".bash_sessions", ".sqldeveloper", "Quarantine", ".atom", ".class",
                          ".oracle_jre_usage", ".poetry", ".psql_history", ".pylint.d", ".rnd", ".vnc", "bin"
                          "kubepug", "Library", "chromedriver", "tmp", "guest", "@eaDir", "poubelle", "build",
                          ".storage", ".svn", "debug", "release", "testresults", "temp", "temporary_files", "logs"}))
    filters.append(PatternFilter(excluded_path_pattern="/Développement/Projets Clients/CDM/ALCRG/BDD/"))
    filters.append(PatternFilter(excluded_path_pattern="/TestData/"))
    filters.append(PatternFilter(excluded_path_pattern="/Lucene/Documentation/"))
    filters.append(PatternFilter(excluded_path_pattern="/DataFiles/"))
    filters.append(ExtensionFilter(excluded_extensions={'svn-base', "gitattributes", "uYlOfa", "sublime-project", "sqlite3", "log",
                     "cpp_disabled_avr_specific", "tmp", "temp",
                     "dat", "bak", "db", "ibd", "pyc", "class", "jar", "war", "DS_Store", "AppleDouble", "LSOverride",
                     "tab", "so", "gz", "tar",
                     "__styleext__", "APACHE2", "apk", "appcache", "attic", "babelrc", "before", "bin", "bnf", "BSD",
                     "cache", "backup", "pbxproj", "uuid", "jbf", "dump", "vdproj",
                     "clonedeep", "debounce", "def", "delivery", "disabled", "dist", "dist - info", "dmg",
                     "editorconfig", "!bt", "onetoc2", ".com.google.Chrome", "_____padding_file_",
                     "gitmodules", "lock", "pyc", "sample", "map", "svn", "svn-base", "pdb", "ldf", "bup", "ds_store",
                     ".ifo", ".vob", "_"}))
    #filters.append(RegexPatternFilter(excluded_path_pattern="python[0-9]\.[0-9]"))
    #filters.append(RegexPatternFilter(excluded_path_pattern="[r]?[0-9]{2}$"))
    #filters.append(RegexPatternFilter(excluded_path_pattern="\.[0-9-]+$"))
    #filters.append(RegexPatternFilter(excluded_path_pattern=".*~$"))
    #filters.append(RegexPatternFilter(excluded_path_pattern="^~.*"))

    data_manager: PathDataManager = PathDataManager()

    fc: FastCrawler = FastCrawler(base_path=base_volume, child_path=dev_dir, fetch_file_stat=False,
                                  category=ContentCategory.CODE, min_age=ContentClassificationPegi.TWELVE_OR_MORE,
                                  filters=filters, data_manager=data_manager)

    start = time.time()
    fc.scan()
    end = time.time()
    duration = end - start
    print(f"Total size: {round(fc.total_size / 1024 / 1024 / 1024, 3)} Go - Scanned {fc.total_files} files / Skipped {fc.ignored_files} files in {duration:.2f} sec")

    print("\n==============")
    print("Ignored dirs:")
    for name in sorted(fc.ignored_dirs_list)[:100]:
        print(name)

    print("\n==============")
    print("Ignored files:")
    for name in sorted(fc.ignored_files_list)[:100]:
        print(name)

    print("\n==============")
    print("Ignored extensions:")
    for name in sorted(fc.ignored_extensions_list)[:100]:
        print(name)

    print("\n==============")
    print("Scanned extensions:")
    for name in sorted(fc.scanned_extensions_list)[:100]:
        print(name)

    print("\n==============")
    print("Empty directories:")
    for name in sorted(fc.empty_dirs_list)[:100]:
        print(name)

    # crawl_directory(base_dir_path=f"{base_volume}Test",
    #                 category=ContentCategory.ADULT,
    #                 min_age=ContentClassificationPegi.EIGHTEEN_OR_MORE)
    # crawl_directory(base_dir_path=f"{base_volume}Développement",
    #                 category=ContentCategory.CODE,
    #                 min_age=ContentClassificationPegi.TWELVE_OR_MORE)
    # crawl_directory(base_dir_path=f"{base_volume}A trier",
    #                 category=None,
    #                 min_age=ContentClassificationPegi.EIGHTEEN_OR_MORE)
