from loguru import logger

from crawler.events.crawlCompletedEventArgs import CrawlCompletedEventArgs
from crawler.events.crawlErrorEventArgs import CrawlErrorEventArgs
from crawler.events.crawlProgressEventArgs import CrawlProgessEventArgs
from crawler.events.crawlStartingEventArgs import CrawlStartingEventArgs
from crawler.events.crawlStoppedEventArgs import CrawlStoppedEventArgs
from crawler.events.directoryCrawledEventArgs import DirectoryCrawledEventArgs
from crawler.events.directoryFoundEventArgs import DirectoryFoundEventArgs
from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from crawler.events.fileFoundEventArgs import FileFoundEventArgs
from crawler.events.pathFoundEventArgs import PathFoundEventArgs
from crawler.events.pathSkippedEventArgs import PathSkippedEventArgs
from interfaces.iCrawlerObserver import ICrawlerObserver


class LoggingObserver(ICrawlerObserver):

    def crawl_starting(self, crawl_event: CrawlStartingEventArgs):
        logger.info(f"Crawl started at: {crawl_event.crawler.start_time.isoformat()}")

    def path_found(self, crawl_event: PathFoundEventArgs):
        super().path_found(crawl_event)

    def path_skipped(self, crawl_event: PathSkippedEventArgs):
        super().path_skipped(crawl_event)

    def processing_file(self, crawl_event: FileFoundEventArgs):
        super().processing_file(crawl_event)

    def processed_file(self, crawl_event: FileCrawledEventArgs):
        super().processed_file(crawl_event)
        logger.info(f"Found file {crawl_event.path}: {crawl_event.size_in_mb:0.2f} Mb")

    def processing_directory(self, crawl_event: DirectoryFoundEventArgs):
        super().processing_directory(crawl_event)

    def processed_directory(self, crawl_event: DirectoryCrawledEventArgs):
        super().processed_directory(crawl_event)
        logger.info(f"Found dir {crawl_event.path}: {crawl_event.size_in_mb} ({crawl_event.files_in_dir}) files")

    def crawl_progress(self, crawl_event: CrawlProgessEventArgs):
        logger.info(f"Crawled so far:"
                    f"\n\t- paths found: {len(crawl_event.crawler.paths_found)}"
                    f"\n\t- paths skipped: {len(crawl_event.crawler.paths_skipped)}"
                    f"\n\t- directories processed: {len(crawl_event.crawler.directories_processed)}"
                    f"\n\t- files processed: {len(crawl_event.crawler.files_processed)}"
                    f"\n\t- total crawled paths: {len(crawl_event.crawler.crawled_paths)}"
                    f"\n\t- total processed file size: {crawl_event.crawler.crawled_files_size:0.2f} Mb")

    def crawl_error(self, crawl_event: CrawlErrorEventArgs):
        logger.info(f"Error while scrawling path '{crawl_event.path}': {crawl_event.error}")

    def crawl_stopped(self, crawl_event: CrawlStoppedEventArgs):
        logger.info(f"Crawl stopped at: {crawl_event.crawler.end_time.isoformat()}")

    def crawl_completed(self, crawl_event: CrawlCompletedEventArgs):
        logger.info(f"Crawl completed at: {crawl_event.crawler.end_time.isoformat()}")
