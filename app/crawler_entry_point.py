#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import os
import re
import sys
import threading
import time
from datetime import datetime
from queue import Queue
from typing import List
import platform

from loguru import logger
import xxhash

from crawler.crawl_directory import crawl_directory
from observers.empty_directory_observer import EmptyDirectoryObserver

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

from config import config
from helpers.filesize_helper import format_file_size
from crawler.file_system_crawler import FileSystemCrawler
from crawling_queue_consumer import CrawlingQueueConsumer
from database.data_manager import PathDataManager
from interfaces.iPathProcessor import IPathProcessor
from observers.metrics_observer import MetricsObserver
from observers.queue_observer import QueueObserver
from processors.hash_file_processor import HashFileProcessor
from processors.metadata_extractor.extended_attributes_file_processor import ExtendedAttributesFileProcessor
from processors.metadata_extractor.rating_file_processor import RatingFileProcessor
from processors.metadata_extractor.keywords_file_processor import KeywordsFileProcessor
from filters.extension_filter import ExtensionFilter
from filters.path_regex_pattern_filter import RegexPatternFilter
from models.content import ContentClassificationPegi, ContentCategory

if platform.system() == "Darwin":
    from processors.metadata_extractor.mac_finfer_tags_extractor import MacFinderTagsExtractorFileProcessor


# TODO: list partitions, get their UUID and map them with the roots to be crawled
# drps = psutil.disk_partitions()
#
# if platform.system() == "Windows":
#     drives = [dp.device for dp in drps if dp.fstype == 'NTFS']  # Windows
# elif platform.system() == "Linux":
#     drives = os.popen("hdparm -I /dev/sda | grep 'Serial Number'").read().split()   # Linux
# elif platform.system() == "Darwin":
#     # Mac OS
#     drives = []


def main():
    roots: dict = {

        # Path, Root part from the mapped volume
    }
    crawler = FileSystemCrawler(roots=roots)
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=".*\.ino$"))
    directories_to_skip: List[str] = [".idea", ".Trashes", "out", ".idea_modules", "build", "dist", "lib", "venv.*",
                                      ".pyenv", "python[0-9]\.[0-9]", "bin", ".git", "@angular.*", "node_modules",
                                      "botocore", "boto3", ".terraform", ".terraformrc", "package", "target",
                                      "__pycache__", "mypy_boto3_builder", ".gradle", ".mvn", ".npm", ".nvm",
                                      ".npm-packages", ".node-gyp", ".node_repl_history", ".m2", ".plugins", ".cache",
                                      ".docker", "dockervolumes", "jenkins", ".eclipse", ".Trash", ".krew", "kube",
                                      ".android", ".bash_sessions", ".sqldeveloper", "Quarantine", ".atom",
                                      ".oracle_jre_usage", ".poetry", ".psql_history", ".pylint.d", ".rnd", ".vnc",
                                      "kubepug", "Library", "chromedriver", "tmp", "tutorials\/guest", "@eaDir",
                                      ".storage", ".svn", "Debug", "bin\/Debug", "Release", "obj\/Debug", "poubelle"]
    for skip_dir in directories_to_skip:
        if skip_dir:
            crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=f"\/{skip_dir}\/"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern="testcontainers.properties"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern="Thumbs.db"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=".com.google.Chrome"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=".*~$"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern="\/.svn$"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern="^~.*"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=".*\.[!]?bt$"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=".*@SynoEAStream$"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=".*\.[r]?[0-9]{2}"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern="_____padding_file_"))
    crawler.add_skip_filter(ExtensionFilter(excluded_extensions=[
        "gitattributes", "uYlOfa", "sublime-project", "sqlite3", "log", "cpp_disabled_avr_specific", "tmp", "temp",
        "dat", "bak", "db", "ibd", "pyc", "class", "jar", "war", "DS_Store", "AppleDouble", "LSOverride", "tab", "so",
        "__styleext__", "APACHE2", "apk", "appcache", "attic", "babelrc", "before", "bin", "bnf", "BSD", "cache",
        "clonedeep", "debounce", "def", "delivery", "disabled", "dist", "dist - info", "dmg", "editorconfig",
        "gitmodules", "lock", "pyc", "sample", "map", "svn", "svn-base", "pdb", "ldf", "bup", "ds_store", ".ifo", ".vob"
    ]
    ))
    # crawler.add_skip_filter(ExtensionFilter(authorized_extensions=['avi', 'mpg', 'mpeg', 'flv', 'mp4', 'wmv']))
    # crawler.add_skip_filter(ExtensionFilter(authorized_extensions=['nfo', 'txt']))

    crawling_queue: Queue = Queue(maxsize=config.QUEUE_MAX_SIZE)
    # crawler.add_observer(LoggingObserver())
    crawler.add_observer(EmptyDirectoryObserver())
    metricsObserver = MetricsObserver()
    crawler.add_observer(metricsObserver)
    crawler.add_observer(QueueObserver(crawling_queue=crawling_queue))

    processors: List[IPathProcessor] = []

    hash_algos = {}
    # hash_algos['xxh32'] = xxhash.xxh32()      # 15 sec to hash 10 Go
    hash_algos['xxh3_64'] = xxhash.xxh3_64()    # 15 sec to hash 10 Go
    # hash_algos['md5'] = hashlib.md5()         # 22 sec to hash 10 Go
    # hash_algos['sha256'] = hashlib.sha256()   # 28 sec to hash 10 Go - Avoids risk of collisions, but much slower
    processors.append(HashFileProcessor(hash_algorithms=hash_algos))
    processors.append(RatingFileProcessor())
    processors.append(KeywordsFileProcessor())
    processors.append(ExtendedAttributesFileProcessor())
    if platform.system() == "Darwin":
        processors.append(MacFinderTagsExtractorFileProcessor())

    data_manager: PathDataManager = PathDataManager()  # Providing the data manager will persist processed paths into DB
    queue_consumer = CrawlingQueueConsumer(crawling_queue=crawling_queue,
                                           path_processors=processors,
                                           data_manager=None,
                                           update_existing_paths=False)

    producer_thread = threading.Thread(target=crawler.start, name="FileCrawler - producer")  # Search paths
    consumer_thread = threading.Thread(target=queue_consumer.start, name="File consumer")  # Process paths

    consumer_thread.start()
    producer_thread.start()

    producer_thread.join()
    consumer_thread.join()

    crawl_duration = datetime.now() - crawler.start_time
    logger.warning(
        f"Crawled {len(crawler.files_processed)} files (total of {format_file_size(crawler.crawled_files_size)}) "
        f"in {crawl_duration} sec")
    metricsObserver.print_statistics()


# endregion

found_dirs = 0
ignored_dirs = 0
scanned_dirs = 0
found_files = 0
ignored_files = 0
scanned_files = 0
ignored_files_list = set()
ignored_dirs_list = set()
ignored_extensions_list = set()
scanned_extensions_list = set()
empty_dirs_list = set()

ignore_extensions = {'svn-base', "gitattributes", "uYlOfa", "sublime-project", "sqlite3", "log",
                     "cpp_disabled_avr_specific", "tmp", "temp",
                     "dat", "bak", "db", "ibd", "pyc", "class", "jar", "war", "DS_Store", "AppleDouble", "LSOverride",
                     "tab", "so", "gz", "zip", "tar", "rar", "7z",
                     "__styleext__", "APACHE2", "apk", "appcache", "attic", "babelrc", "before", "bin", "bnf", "BSD",
                     "cache", "backup", "pbxproj", "uuid", "jbf", "dump", "vdproj",
                     "clonedeep", "debounce", "def", "delivery", "disabled", "dist", "dist - info", "dmg",
                     "editorconfig", "!bt", "onetoc2", ".com.google.Chrome", "_____padding_file_",
                     "gitmodules", "lock", "pyc", "sample", "map", "svn", "svn-base", "pdb", "ldf", "bup", "ds_store",
                     ".ifo", ".vob"}
ignore_directory_names = {".idea", ".Trashes", "out", ".idea_modules", "build", "dist", "lib", "venv",
                          ".pyenv", "python", "bin", "obj", "debug", ".git", "@angular", "node_modules",
                          "botocore", "boto3", ".terraform", ".terraformrc", "package", "target",
                          "__pycache__", "mypy_boto3_builder", ".gradle", ".mvn", ".npm", ".nvm",
                          ".npm-packages", ".node-gyp", ".node_repl_history", ".m2", ".plugins", ".cache",
                          ".docker", "dockervolumes", "jenkins", ".eclipse", ".Trash", ".krew", "kube",
                          ".android", ".bash_sessions", ".sqldeveloper", "Quarantine", ".atom",
                          ".oracle_jre_usage", ".poetry", ".psql_history", ".pylint.d", ".rnd", ".vnc",
                          "kubepug", "Library", "chromedriver", "tmp", "guest", "@eaDir", "poubelle",
                          ".storage", ".svn", "debug", "release", "testresults", "temp", "temporary_files", "logs"}
ignore_dir_regex_patterns = {
    re.compile("python[0-9]\.[0-9]")
}
ignore_extensions_regex_patterns = {
    re.compile("[r]?[0-9]{2}$"),
    re.compile(".*~$"),
    re.compile("^~.*")
}


def should_ignore_dir(entry, ignore_directory_names, ignore_dir_regex_patterns) -> bool:
    if entry.name in ignore_directory_names:
        return True
    if ignore_dir_regex_patterns:
        for pattern in ignore_dir_regex_patterns:
            if re.findall(pattern, entry.name):
                return True
    return False


def should_ignore_file(entry, ignore_extensions, ignore_extensions_regex_patterns) -> (str, bool):
    file_extension = str(entry.name.split('.')[-1]).lower()
    if file_extension and file_extension in ignore_extensions:
        return file_extension, True
    if ignore_extensions_regex_patterns:
        for pattern in ignore_extensions_regex_patterns:
            file_path = entry.path
            if re.findall(pattern, file_path):
                return file_extension, True
    return file_extension, False


def get_tree_size(path) -> (str, str):
    """Return total size of files in path and subdirs. If
    is_dir() or stat() fails, print an error message to stderr
    and assume zero size (for example, file has been deleted).
    """
    global found_dirs
    global ignored_dirs
    global ignored_dirs_list
    global scanned_dirs
    global found_files
    global ignored_files
    global ignored_files_list
    global scanned_files
    global ignore_extensions
    global ignore_directory_names
    global ignored_extensions_list
    global scanned_extensions_list
    global ignore_dir_regex_patterns
    global ignore_extensions_regex_patterns
    global empty_dirs_list

    total_size = 0
    total_files_nb = 0
    for entry in os.scandir(path):
        try:
            is_dir = entry.is_dir(follow_symlinks=False)
        except OSError as error:
            print('Error calling is_dir():', error, file=sys.stderr)
            continue
        if is_dir:
            found_dirs += 1
            if should_ignore_dir(entry, ignore_directory_names, ignore_dir_regex_patterns):
                # print(f"Ignoring directory '{entry.path}'")
                ignored_dirs += 1
                if len(ignored_dirs_list) < 100:
                    ignored_dirs_list.add(entry.path)
                continue
            sub_dir_total_size, sub_dir_total_files_nb = get_tree_size(entry.path)
            if sub_dir_total_size < 1 and sub_dir_total_files_nb < 1:
                empty_dirs_list.add(entry.path)
            total_size += sub_dir_total_size
            total_files_nb += sub_dir_total_files_nb
            scanned_dirs += 1
            # print(f"Scanned dir '{entry.path}'")
            if scanned_dirs % 10000 == 0:
                print(f"Scanned {scanned_files} files / {scanned_dirs} dirs")
        else:
            try:
                found_files += 1
                file_extension, ignore = should_ignore_file(entry, ignore_extensions, ignore_extensions_regex_patterns)
                if ignore:
                    # print(f"Ignoring file '{entry.path}'")
                    ignored_files += 1
                    if len(ignored_files_list) < 100:
                        ignored_files_list.add(entry.path)
                    ignored_extensions_list.add(file_extension)
                    continue
                scanned_extensions_list.add(file_extension)
                entry_stat = entry.stat(follow_symlinks=False)
                total_size += entry_stat.st_size
                total_files_nb += 1
                scanned_files += 1
                if scanned_files % 10000 == 0:
                    print(f"Scanned {scanned_files} files / {scanned_dirs} dirs")
            except OSError as error:
                print('Error calling stat():', error, file=sys.stderr)
    return total_size, total_files_nb


if __name__ == '__main__':
    base_volume = '/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b1/'
    dev_dir = f"{base_volume}Développement"
    test_dir = f"{base_volume}Développement/Dev/v3.5/src/trunk/Evaluant.Uss.DomainModel/ClassModel/"
    start = time.time()
    total_size, total_files_nb = get_tree_size(dev_dir)
    end = time.time()
    duration = end - start
    print(f"Total size: {round(total_size / 1024 / 1024 / 1024, 3)} Go - Scanned {total_files_nb} files / Skipped {ignored_files} files in {duration} sec")

    print("\n==============")
    print("Ignored dirs:")
    for name in sorted(ignored_dirs_list)[:100]:
        print(name)

    print("\n==============")
    print("Ignored files:")
    for name in sorted(ignored_files_list)[:100]:
        print(name)

    print("\n==============")
    print("Ignored extensions:")
    for name in sorted(ignored_extensions_list)[:100]:
        print(name)

    print("\n==============")
    print("Scanned extensions:")
    for name in sorted(scanned_extensions_list)[:100]:
        print(name)

    print("\n==============")
    print("Empty directories:")
    for name in sorted(empty_dirs_list)[:100]:
        print(name)


    # crawl_directory(base_dir_path=f"{base_volume}Développement",
    #                 category=ContentCategory.CODE,
    #                 min_age=ContentClassificationPegi.TWELVE_OR_MORE)
    # crawl_directory(base_dir_path=f"{base_volume}A trier",
    #                 category=None,
    #                 min_age=ContentClassificationPegi.EIGHTEEN_OR_MORE)
