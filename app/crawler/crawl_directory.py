#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import List
import platform

from loguru import logger
import xxhash

from interfaces.iFilter import IFilter
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


def get_parent_dir(base_dir_path: str) -> str:
    if not base_dir_path:
        raise ValueError("The parameter 'base_dir_path' is mandatory")
    p: Path = Path(base_dir_path)
    if not p.exists():
        raise ValueError(f"The given base path does not exists: '{base_dir_path}'")
    if not p.is_dir():
        raise ValueError(f"The given base path is not a directory: '{base_dir_path}'")
    parent_dir = p.parent
    if not parent_dir:
        raise ValueError(f"The given base path has no parent directory (it must be an absolute path): '{base_dir_path}'")
    return str(parent_dir)


def build_filters() -> List[IFilter]:
    filters: List[IFilter] = []
    filters.append(RegexPatternFilter(excluded_path_pattern=".*\.ino$"))
    directories_to_skip: List[str] = [".idea", ".Trashes", "out", ".idea_modules", "build", "dist", "lib", "venv.*",
                                      ".pyenv", "python[0-9]\.[0-9]", "bin", ".git", "@angular.*", "node_modules",
                                      "botocore", "boto3", ".terraform", ".terraformrc", "package", "target",
                                      "__pycache__", "mypy_boto3_builder", ".gradle", ".mvn", ".npm", ".nvm",
                                      ".npm-packages", ".node-gyp", ".node_repl_history", ".m2", ".plugins", ".cache",
                                      ".docker", "dockervolumes", "jenkins", ".eclipse", ".Trash", ".krew", "kube",
                                      ".android", ".bash_sessions", ".sqldeveloper", "Quarantine", ".atom",
                                      ".oracle_jre_usage", ".poetry", ".psql_history", ".pylint.d", ".rnd", ".vnc",
                                      "kubepug", "Library", "chromedriver", "tmp", "tutorials\/guest", "@eaDir",
                                      ".storage", ".svn", "Debug", "bin\/Debug", "Release", "obj\/Debug"]
    for skip_dir in directories_to_skip:
        if skip_dir:
            filters.append(RegexPatternFilter(excluded_path_pattern=f"\/{skip_dir}\/"))
    filters.append(RegexPatternFilter(excluded_path_pattern="testcontainers.properties"))
    filters.append(RegexPatternFilter(excluded_path_pattern="Thumbs.db"))
    filters.append(RegexPatternFilter(excluded_path_pattern=".com.google.Chrome"))
    filters.append(RegexPatternFilter(excluded_path_pattern=".*~$"))
    filters.append(RegexPatternFilter(excluded_path_pattern="\/.svn$"))
    filters.append(RegexPatternFilter(excluded_path_pattern="^~.*"))
    filters.append(RegexPatternFilter(excluded_path_pattern=".*\.[!]?bt$"))
    filters.append(RegexPatternFilter(excluded_path_pattern=".*@SynoEAStream$"))
    filters.append(RegexPatternFilter(excluded_path_pattern=".*\.[r]?[0-9]{2}"))
    filters.append(RegexPatternFilter(excluded_path_pattern="_____padding_file_"))
    filters.append(ExtensionFilter(excluded_extensions=[
        "gitattributes", "uYlOfa", "sublime-project", "sqlite3", "log", "cpp_disabled_avr_specific", "tmp", "temp",
        "dat", "bak", "db", "ibd", "pyc", "class", "jar", "war", "DS_Store", "AppleDouble", "LSOverride", "tab", "so",
        "__styleext__", "APACHE2", "apk", "appcache", "attic", "babelrc", "before", "bin", "bnf", "BSD", "cache",
        "clonedeep", "debounce", "def", "delivery", "disabled", "dist", "dist - info", "dmg", "editorconfig",
        "gitmodules", "lock", "pyc", "sample", "map", "svn", "svn-base", "pdb", "ldf", "bup", "ds_store", ".ifo", ".vob"
    ]
    ))
    return filters


def build_processors(category: ContentCategory) -> List[IPathProcessor]:
    processors: List[IPathProcessor] = []

    hash_algos = {}
    hash_algos['xxh3_64'] = xxhash.xxh3_64()  # 15 sec to hash 10 Go
    # hash_algos['md5'] = hashlib.md5()         # 22 sec to hash 10 Go
    # hash_algos['sha256'] = hashlib.sha256()   # 28 sec to hash 10 Go - Avoids risk of collisions, but much slower
    # processors.append(HashFileProcessor(hash_algorithms=hash_algos))
    processors.append(ExtendedAttributesFileProcessor())
    if category == ContentCategory.ADULT or category == ContentCategory.MUSIC:
        processors.append(KeywordsFileProcessor())
        processors.append(RatingFileProcessor())
    if platform.system() == "Darwin":
        processors.append(MacFinderTagsExtractorFileProcessor())
    return processors


def crawl_directory(base_dir_path: str, category: ContentCategory, min_age: ContentClassificationPegi):
    parent_dir_path = get_parent_dir(base_dir_path)
    roots: dict = {
        str(base_dir_path): {
            'root': f"{parent_dir_path}/",
            'category': category,
            'min_age': min_age,
            'target_table': 'path'
        }
    }
    crawler = FileSystemCrawler(roots=roots)
    crawler.add_skip_filters(build_filters())

    crawling_queue: Queue = Queue(maxsize=config.QUEUE_MAX_SIZE)
    crawler.add_observer(EmptyDirectoryObserver())
    metrics_observer = MetricsObserver()
    crawler.add_observer(metrics_observer)
    crawler.add_observer(QueueObserver(crawling_queue=crawling_queue))

    data_manager: PathDataManager = PathDataManager()  # Providing the data manager will persist processed paths into DB
    data_manager = None
    queue_consumer = CrawlingQueueConsumer(crawling_queue=crawling_queue,
                                           path_processors=build_processors(category=category),
                                           data_manager=data_manager,
                                           update_existing_paths=True)

    producer_thread = threading.Thread(target=crawler.start, name="FileCrawler - producer")  # Search paths
    consumer_thread = threading.Thread(target=queue_consumer.start, name="File consumer")  # Process paths

    consumer_thread.start()
    producer_thread.start()

    producer_thread.join()
    consumer_thread.join()

    crawl_duration = datetime.now() - crawler.start_time
    logger.warning(f"Crawled {len(crawler.files_processed)} files (total of {format_file_size(crawler.crawled_files_size)}) "
                   f"in {crawl_duration} sec")
    metrics_observer.print_statistics()


# if __name__ == '__main__':
#     crawl_code_dir('/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b1/Développement')
