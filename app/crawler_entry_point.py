#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import hashlib
import threading
from datetime import datetime
from queue import Queue
from typing import List

import psutil
from loguru import logger

from crawler.file_system_crawler import FileSystemCrawler
from crawling_queue_consumer import CrawlingQueueConsumer
from database.data_manager import PathDataManager
from filters.path_pattern_filter import PatternFilter
from interfaces.iPathProcessor import IPathProcessor
from observers.metrics_observer import MetricsObserver
from observers.queue_observer import QueueObserver
from processors.extended_attributes_file_processor import ExtendedAttributesFileProcessor
from processors.hash_file_processor import HashFileProcessor

drps = psutil.disk_partitions()
drives = [dp.device for dp in drps if dp.fstype == 'NTFS']


def main():
    crawler = FileSystemCrawler(roots=['/Volumes/data-music/zz_recycle/Mc Solaar'])
    crawler.add_filter(PatternFilter(excluded_path_pattern=".DS_Store"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".AppleDouble"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".LSOverride"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".idea/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".Trashes"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="out/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".idea_modules/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="build/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="dist/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="lib/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="venv/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".pyenv/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="bin/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".git"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="@angular*"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="node_modules/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="botocore/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="boto3/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="*.jar"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="*.war"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".terraform/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="package/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="*.class"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="target/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="__pycache__"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="*.pyc"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="mypy_boto3_builder/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".gradle/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".mvn/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="*.db"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="*.dat"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="*.bak"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="*.log"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".npm/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".nvm/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".npm-packages/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".m2/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".plugins/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".cache/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".docker/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="dockervolumes/"))

    crawling_queue: Queue = Queue()
    # crawler.add_observer(LoggingObserver())
    metricsObserver = MetricsObserver()
    crawler.add_observer(metricsObserver)
    crawler.add_observer(QueueObserver(crawling_queue=crawling_queue))

    processors: List[IPathProcessor] = []

    hash_algos = {}
    hash_algos['md5'] = hashlib.md5()
    # hash_algos['sha256'] = hashlib.sha256()   # Avoids risk of collisions, but super slow
    processors.append(HashFileProcessor(hash_algorithms=hash_algos))
    processors.append(ExtendedAttributesFileProcessor())

    data_manager: PathDataManager = PathDataManager()
    queue_consumer = CrawlingQueueConsumer(crawling_queue=crawling_queue, path_processors=processors)

    # region crawling
    producer_thread = threading.Thread(target=crawler.start, name="FileCrawler - producer")  # Search paths
    consumer_thread = threading.Thread(target=queue_consumer.start, name="File consumer")  # Process paths

    consumer_thread.start()
    producer_thread.start()

    producer_thread.join()
    consumer_thread.join()

    crawl_duration = datetime.now() - crawler.start_time
    logger.info(f"Crawled {len(crawler.files_processed)} files (total of {crawler.crawled_files_size:0.2f} Mb) "
                f"in {crawl_duration} sec")
    metricsObserver.print_statistics()
    # endregion

    # region database
    logger.info(f"Saving now {len(queue_consumer.processed_files)} files into DB...")

    for file in queue_consumer.processed_files:
        data_manager.save_path(file)
        logger.debug(f"Saved file {file.path} into DB")
    logger.info(f"Done saving files! {len(queue_consumer.processed_files)} files saved to DB")

    for dir in queue_consumer.processed_directories:
        data_manager.save_path(dir)
        logger.debug(f"Saved dir {dir.path} into DB")
    logger.info(f"Done saving directories! {len(queue_consumer.processed_directories)} directories saved to DB")

    total_duration = datetime.now() - crawler.start_time
    logger.info(
        f"Crawled and processed {len(crawler.files_processed)} files (total of {crawler.crawled_files_size:0.2f} Mb) "
        f"in {total_duration} sec")
    metricsObserver.print_statistics()


# endregion


if __name__ == '__main__':
    main()
