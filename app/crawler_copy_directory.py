#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import List

from loguru import logger

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

from app.helpers.filesize_helper import format_file_size
from app.crawler.file_system_crawler import FileSystemCrawler
from app.crawling_queue_consumer import CrawlingQueueConsumer
from app.filters.path_pattern_filter import PatternFilter
from app.interfaces.iFilter import IFilter
from app.interfaces.iPathProcessor import IPathProcessor
from app.observers.metrics_observer import MetricsObserver
from app.observers.queue_observer import QueueObserver
from app.processors.copy_path_processor import CopyPathProcessor
from app.processors.delete_path_processor import DeletePathProcessor

roots: dict = {
    f"{Path.home()}/Downloads": f"{Path.home()}/"  # Path, Root part from the mapped volume
}
trash_path = f"{Path.home()}/.delete"  # A directory used a virtual trash (unwanted files would be moved here, preserving the file structure)
backup_path = f"{Path.home()}/backup"  # The target directory to backup files

delete_patterns = ['/dist/', '/jMeter/', '.DS_Store', '.AppleDouble', '.LSOverride', '.Trashes', 'out/', 'build/',
                   'dist/', '@angular', 'node_modules/', '.jar$', '.war$', '.class$', 'target/', '.pyc$', '.dat$',
                   '.bak$', '.log$', '.npm/', '.nvm/', '.npm-packages/', '.node-gyp/', '.node_repl_history',
                   '.plugins/', '.cache/', '/jenkins/', 'testcontainers.properties', '.eclipse/', '.Trash/',
                   '.krew/', 'kube/cache/', 'kube/http-cache/', '.android/', '.bash_sessions/', '.sqldeveloper/',
                   '/Quarantine/', '.atom/', '.oracle_jre_usage/', '.poetry/', '.psql_history/', '.pylint.d/',
                   '.rnd/', '.splunk/', '.splunkrc/', '.vnc/', '/kubepug/', '/open-zwave.git/', '/chromedriver/',
                   '/tmp/', '/tutorials/guest/', '/navifycli_py3/', '/.ApacheDirectoryStudio/', '.!bt']

ignore_patterns = ['/.git/', '.idea/', '.idea_modules/', 'lib/', '/venv', '.pyenv/', '/env/lib/python',
                   '/python2.7/', '/bin/', '/.git/', '.git/objects', 'botocore/', 'boto3/', '.terraform/',
                   '.terraformrc/', 'package/', '__pycache__', 'mypy_boto3_builder/', '.gradle/', '.mvn/', '.db$',
                   '.ibd', '.m2/', '.docker/', 'dockervolumes/', '/Library/', trash_path]


def process_path(roots: dict, skip_filters: List[IFilter] = [], notify_filters: List[IFilter] = [],
                 processors: List[IPathProcessor] = []) -> object:
    crawler = FileSystemCrawler(roots=roots, skip_filters=skip_filters, notify_filters=notify_filters)

    crawling_queue: Queue = Queue()
    metricsObserver = MetricsObserver()
    crawler.add_observer(metricsObserver)
    crawler.add_observer(QueueObserver(crawling_queue=crawling_queue))

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
    logger.info(f"Crawled {len(crawler.files_processed)} files (total of {format_file_size(crawler.crawled_files_size)})"
                f"in {crawl_duration} sec")
    metricsObserver.print_statistics()


def delete_unwanted_files(roots: dict, delete_patterns: List[str], trashbin_path: str = f"{Path.home()}/.delete"):
    logger.info("Deleting unwanted files")

    filters: List[IFilter] = []
    for pattern in delete_patterns:
        filters.append(PatternFilter(authorized_path_pattern=pattern))

    return process_path(roots=roots,
                        skip_filters=[
                            PatternFilter(excluded_path_pattern=trash_path)
                        ],
                        notify_filters=filters,
                        processors=[
                            DeletePathProcessor(trashbin_path=trashbin_path)
                        ])


def copy_files(roots: dict, ignore_patterns: List[str], dest_dir_path: str):
    logger.info(f"Copying files to '{dest_dir_path}'")

    filters: List[IFilter] = []
    for pattern in ignore_patterns:
        filters.append(PatternFilter(excluded_path_pattern=pattern))

    return process_path(roots=roots,
                        skip_filters=filters,
                        processors=[
                            CopyPathProcessor(dest_dir_path=dest_dir_path)
                        ])


def main():
    # First cleanup rubbish items
    # delete_unwanted_files(roots=roots, delete_patterns=delete_patterns)

    # Then copy all files excluding unwanted ones (if any left)
    delete_patterns.extend(ignore_patterns)
    copy_files(roots=roots, ignore_patterns=delete_patterns, dest_dir_path=backup_path)


if __name__ == '__main__':
    main()
