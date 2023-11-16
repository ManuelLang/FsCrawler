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

import psutil
from loguru import logger

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

from app.config import config
from app.crawler.file_system_crawler import FileSystemCrawler
from app.crawling_queue_consumer import CrawlingQueueConsumer
from app.database.data_manager import PathDataManager
from app.filters.path_pattern_filter import PatternFilter
from app.interfaces.iPathProcessor import IPathProcessor
from app.observers.metrics_observer import MetricsObserver
from app.observers.queue_observer import QueueObserver
from app.processors.hash_file_processor import HashFileProcessor
from app.processors.metadata_extractor.extended_attributes_file_processor import ExtendedAttributesFileProcessor
from app.filters.extension_filter import ExtensionFilter

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
        '/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b/blah/Sauveguarde MacBookProActelion/': '/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b/'
        # Path, Root part from the mapped volume
    }
    crawler = FileSystemCrawler(roots=roots)
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".DS_Store"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".AppleDouble"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".LSOverride"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".idea/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".Trashes"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="out/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".idea_modules/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="build/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="dist/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="lib/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/venv"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".pyenv/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/env/lib/python"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/python2.7/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/bin/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/.git/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".git/objects"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="@angular*"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="node_modules/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="botocore/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="boto3/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".terraform/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".terraformrc/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="package/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="target/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="__pycache__"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="mypy_boto3_builder/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".gradle/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".mvn/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".npm/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".nvm/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".npm-packages/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".node-gyp/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".node_repl_history"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".m2/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".plugins/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".cache/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".docker/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="dockervolumes/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/jenkins/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="testcontainers.properties"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".eclipse/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".Trash/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".krew/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="kube/cache/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="kube/http-cache/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".android/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".bash_sessions/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".sqldeveloper/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/Quarantine/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".atom/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".oracle_jre_usage/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".poetry/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".psql_history/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".pylint.d/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".rnd/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".splunk/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".splunkrc/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".vnc/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/kubepug/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/Library/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/chromedriver/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/tmp/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern="/tutorials/guest/"))
    crawler.add_skip_filter(PatternFilter(excluded_path_pattern=".[0-9]+[_]?[a-z]*$"))
    crawler.add_skip_filter(ExtensionFilter(excluded_extensions=[
        "gitattributes", "uYlOfa", "sublime-project", "sqlite3", "log", "cpp_disabled_avr_specific", "tmp", "temp",
        "dat", "bak", "db", "ibd", "pyc", "class", "jar", "war", "DS_Store"
    ]))

    crawling_queue: Queue = Queue(maxsize=config.QUEUE_MAX_SIZE)
    # crawler.add_observer(LoggingObserver())
    metricsObserver = MetricsObserver()
    crawler.add_observer(metricsObserver)
    crawler.add_observer(QueueObserver(crawling_queue=crawling_queue))

    processors: List[IPathProcessor] = []

    hash_algos = {}
    hash_algos['md5'] = hashlib.md5()
    # hash_algos['sha256'] = hashlib.sha256()   # Avoids risk of collisions, but much slower
    processors.append(HashFileProcessor(hash_algorithms=hash_algos))
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
    logger.warning(f"Crawled {len(crawler.files_processed)} files (total of {crawler.crawled_files_size:0.2f} Mb) "
                   f"in {crawl_duration} sec")
    # metricsObserver.print_statistics()


# endregion


if __name__ == '__main__':
    main()
