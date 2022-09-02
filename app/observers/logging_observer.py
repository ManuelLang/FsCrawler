from loguru import logger

from crawler.events.crawlErrorEventArgs import CrawlErrorEventArgs
from crawler.events.crawlProgressEventArgs import CrawlProgessEventArgs
from crawler.events.crawlStatusEventArgs import CrawlStatusEventArgs
from crawler.events.pathEventArgs import PathEventArgs
from interfaces.iCrawlerObserver import ICrawlerObserver


class LoggingObserver(ICrawlerObserver):

    def crawl_starting(self, scan_event: CrawlStatusEventArgs):
        logger.info(f"Crawl started at: {scan_event.crawler.start_time.isoformat()}")

    def path_found(self, scan_event: PathEventArgs):
        super().path_found(scan_event)

    def path_skipped(self, scan_event: PathEventArgs):
        super().path_skipped(scan_event)

    def processing_file(self, scan_event: PathEventArgs):
        super().processing_file(scan_event)

    def processing_directory(self, scan_event: PathEventArgs):
        super().processing_directory(scan_event)

    def path_processed(self, scan_event: PathEventArgs):
        super().path_processed(scan_event)

    def crawl_progress(self, scan_event: CrawlProgessEventArgs):
        logger.info(f"Crawled so far:"
                    f"\n\t- paths found: {len(scan_event.crawler.paths_found)}"
                    f"\n\t- paths skipped: {len(scan_event.crawler.paths_skipped)}"
                    f"\n\t- directories processed: {len(scan_event.crawler.directories_processed)}"
                    f"\n\t- files processed: {len(scan_event.crawler.files_processed)}"
                    f"\n\t- total crawled paths: {len(scan_event.crawler.crawled_paths)}"
                    f"\n\t- total processed file size: {scan_event.crawler.crawled_files_size:0.2f} Gb")

    def crawl_error(self, scan_event: CrawlErrorEventArgs):
        logger.info(f"Error while scrawling path '{scan_event.path}': {scan_event.error}")

    def crawl_stopped(self, scan_event: CrawlStatusEventArgs):
        logger.info(f"Crawl stopped at: {scan_event.crawler.end_time.isoformat()}")

    def crawl_completed(self, scan_event: CrawlStatusEventArgs):
        logger.info(f"Crawl completed at: {scan_event.crawler.end_time.isoformat()}")
