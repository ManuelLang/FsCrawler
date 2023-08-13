#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import threading
from datetime import datetime
from queue import Queue
from typing import List

from loguru import logger

from crawler.file_system_crawler import FileSystemCrawler
from crawling_queue_consumer import CrawlingQueueConsumer
from filters.path_pattern_filter import PatternFilter
from interfaces.iPathProcessor import IPathProcessor
from observers.metrics_observer import MetricsObserver
from observers.queue_observer import QueueObserver
from processors.copy_file_processor import CopyFileProcessor


def main():
    roots: dict = {
        '/Users/langm27/metrcis_postgres_backup': '/Users/langm27'  # Path, Root part from the mapped volume
    }
    crawler = FileSystemCrawler(roots=roots)

    ignore_patterns = ['/dist/', '/.git/', '/jMeter/', '.DS_Store', '.AppleDouble', '.LSOverride', '.idea/', '.Trashes',
                       'out/', '.idea_modules/', 'build/', 'dist/', 'lib/', '/venv', '.pyenv/', '/env/lib/python',
                       '/python2.7/', '/bin/', '/.git/', '.git/objects', '@angular', 'node_modules/', 'botocore/',
                       'boto3/', '.jar$', '.war$', '.terraform/', '.terraformrc/', 'package/', '.class$', 'target/',
                       '__pycache__', '.pyc$']
    for pattern in ignore_patterns:
        crawler.add_filter(PatternFilter(excluded_path_pattern=pattern))

    crawler.add_filter(PatternFilter(excluded_path_pattern="mypy_boto3_builder/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".gradle/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".mvn/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".db$"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".dat$"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".bak$"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".log$"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".ibd"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".npm/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".nvm/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".npm-packages/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".node-gyp/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".node_repl_history"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".m2/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".plugins/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".cache/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".docker/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="dockervolumes/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/jenkins/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="testcontainers.properties"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".eclipse/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".Trash/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".krew/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="kube/cache/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="kube/http-cache/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".android/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".bash_sessions/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".sqldeveloper/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/Quarantine/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".atom/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".oracle_jre_usage/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".poetry/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".psql_history/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".pylint.d/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".rnd/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".splunk/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".splunkrc/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern=".vnc/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/kubepug/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/open-zwave.git/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/Library/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/chromedriver/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/tmp/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/tutorials/guest/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/navifycli_py3/"))
    crawler.add_filter(PatternFilter(excluded_path_pattern="/.ApacheDirectoryStudio/"))

    crawling_queue: Queue = Queue()
    # crawler.add_observer(LoggingObserver())
    metricsObserver = MetricsObserver()
    crawler.add_observer(metricsObserver)

    crawler.add_observer(QueueObserver(crawling_queue=crawling_queue))

    processors: List[IPathProcessor] = []
    processors.append(CopyFileProcessor(dest_dir_path='/Volumes/Data/Backups/2023-08-11_Roche/'))

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
    logger.info(f"Crawled {len(crawler.files_processed)} files (total of {crawler.crawled_files_size:0.2f} Mb) "
                f"in {crawl_duration} sec")
    metricsObserver.print_statistics()


# endregion


if __name__ == '__main__':
    main()
