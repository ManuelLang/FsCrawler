#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import hashlib
import os
import sys
import threading
from datetime import datetime
from queue import Queue
from typing import List
import platform

from loguru import logger
import xxhash

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

from app.config import config
from app.helpers.filesize_helper import format_file_size
from app.crawler.file_system_crawler import FileSystemCrawler
from app.crawling_queue_consumer import CrawlingQueueConsumer
from app.database.data_manager import PathDataManager
from app.filters.path_pattern_filter import PatternFilter
from app.interfaces.iPathProcessor import IPathProcessor
from app.observers.metrics_observer import MetricsObserver
from app.observers.queue_observer import QueueObserver
from app.processors.hash_file_processor import HashFileProcessor
from app.processors.metadata_extractor.extended_attributes_file_processor import ExtendedAttributesFileProcessor
from app.processors.metadata_extractor.rating_file_processor import RatingFileProcessor
from app.processors.metadata_extractor.keywords_file_processor import KeywordsFileProcessor
from app.filters.extension_filter import ExtensionFilter
from app.filters.path_regex_pattern_filter import RegexPatternFilter

if platform.system() == "Darwin":
    from app.processors.metadata_extractor.mac_finfer_tags_extractor import MacFinderTagsExtractorFileProcessor


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
        '/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b/Test/': '/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b/'
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
                                      ".storage", ".svn"]
    for skip_dir in directories_to_skip:
        if skip_dir:
            crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=f"\/{skip_dir}\/"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern="testcontainers.properties"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern="Thumbs.db"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=".com.google.Chrome"))
    crawler.add_skip_filter(RegexPatternFilter(excluded_path_pattern=".*~$"))
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
        "gitmodules", "lock", "pyc", "sample", "map", "svn"
    ]))

    crawling_queue: Queue = Queue(maxsize=config.QUEUE_MAX_SIZE)
    # crawler.add_observer(LoggingObserver())
    metricsObserver = MetricsObserver()
    crawler.add_observer(metricsObserver)
    crawler.add_observer(QueueObserver(crawling_queue=crawling_queue))

    processors: List[IPathProcessor] = []

    hash_algos = {}
    # hash_algos['xxh32'] = xxhash.xxh32()      # 15 sec to hash 10 Go
    hash_algos['xxh3_64'] = xxhash.xxh3_64()    # 15 sec to hash 10 Go
    # hash_algos['md5'] = hashlib.md5()         # 22 sec to hash 10 Go
    # hash_algos['sha256'] = hashlib.sha256()   # 28 sec to hash 10 Go - Avoids risk of collisions, but much slower
    # processors.append(HashFileProcessor(hash_algorithms=hash_algos))
    processors.append(RatingFileProcessor())
    processors.append(KeywordsFileProcessor())
    processors.append(ExtendedAttributesFileProcessor())
    if platform.system() == "Darwin":
        processors.append(MacFinderTagsExtractorFileProcessor())

    data_manager: PathDataManager = PathDataManager()  # Providing the data manager will persist processed paths into DB
    queue_consumer = CrawlingQueueConsumer(crawling_queue=crawling_queue,
                                           path_processors=processors,
                                           data_manager=data_manager,
                                           update_existing_paths=False)

    producer_thread = threading.Thread(target=crawler.start, name="FileCrawler - producer")  # Search paths
    consumer_thread = threading.Thread(target=queue_consumer.start, name="File consumer")  # Process paths

    consumer_thread.start()
    producer_thread.start()

    producer_thread.join()
    consumer_thread.join()

    crawl_duration = datetime.now() - crawler.start_time
    logger.warning(f"Crawled {len(crawler.files_processed)} files (total of {format_file_size(crawler.crawled_files_size)}) "
                   f"in {crawl_duration} sec")
    metricsObserver.print_statistics()


# endregion


if __name__ == '__main__':
    main()
