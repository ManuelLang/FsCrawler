from loguru import logger

from crawler.events.crawlErrorEventArgs import CrawlErrorEventArgs
from crawler.events.crawlProgressEventArgs import CrawlProgessEventArgs
from crawler.events.crawlStatusEventArgs import CrawlStatusEventArgs
from crawler.events.directoryProcessedEventArgs import DirectoryProcessedEventArgs
from crawler.events.pathEventArgs import PathEventArgs
from interfaces.iCrawlerObserver import ICrawlerObserver


class LoggingObserver(ICrawlerObserver):

    def crawl_starting(self, crawl_event: CrawlStatusEventArgs):
        logger.info(f"Crawl started at: {crawl_event.crawler.start_time.isoformat()}")

    def path_found(self, crawl_event: PathEventArgs):
        super().path_found(crawl_event)

    def path_skipped(self, crawl_event: PathEventArgs):
        super().path_skipped(crawl_event)

    def processing_file(self, crawl_event: PathEventArgs):
        super().processing_file(crawl_event)

    def processed_file(self, crawl_event: PathEventArgs):
        super().processed_file(crawl_event)
        logger.info(f"Found file {crawl_event.path}: {crawl_event.size_in_mb}")

    def processing_directory(self, crawl_event: PathEventArgs):
        super().processing_directory(crawl_event)

    def processed_directory(self, crawl_event: DirectoryProcessedEventArgs):
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

    def crawl_stopped(self, crawl_event: CrawlStatusEventArgs):
        logger.info(f"Crawl stopped at: {crawl_event.crawler.end_time.isoformat()}")

    def crawl_completed(self, crawl_event: CrawlStatusEventArgs):
        logger.info(f"Crawl completed at: {crawl_event.crawler.end_time.isoformat()}")
