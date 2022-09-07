import threading
import time
from queue import Queue

from crawler.file_system_crawler import FileSystemCrawler
from crawling_queue_consumer import CrawlingQueueConsumer
from filters.path_pattern_filter import PatternFilter
from observers.queue_observer import QueueObserver


def main():
    crawler = FileSystemCrawler(roots=['~/PERSONAL/'])
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
    crawler.add_observer(QueueObserver(crawling_queue=crawling_queue))

    queue_consumer = CrawlingQueueConsumer(crawling_queue=crawling_queue)

    producer_thread = threading.Thread(target=crawler.start, name="FileCrawler - producer")
    consumer_thread = threading.Thread(target=queue_consumer.start, name="File consumer")

    consumer_thread.start()
    time.sleep(1)
    producer_thread.start()

    producer_thread.join()
    consumer_thread.join()


if __name__ == '__main__':
    main()
