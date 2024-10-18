from typing import List
from zoneinfo import reset_tzpath

from loguru import logger
import yaml

from database.data_manager import PathDataManager
from fast_crawler import crawl
from filters.filter import Filter
from helpers.filterFactory import FilterFactory
from index_files import process_files
from interfaces.iFilter import IFilter
from models.content import ContentCategory, ContentClassificationPegi


def process():
    crawl()             # List all files on drive and store paths in DB
    process_files()     # Index files with post-processing (fetch from DB and extract metadata)

def load_config():
    paths_to_scan: dict = {}
    filters: List[IFilter] = []

    with open('../config.yml', 'r') as f:
        data = yaml.safe_load(f)
        logger.debug(f"Found following YAML config: {data}")
        paths_node = data.get('paths', None)
        if not paths_node:
            logger.error("Error - no path provided to be scanned. Exiting...")
            return
        logger.info(f"Loading paths from config file...")
        for path_configs in paths_node:
            try:
                for root_dir_path, path_config in path_configs.items():
                    try:
                        category = ContentCategory.from_name(path_config.get('ContentCategory', None))
                        min_age = ContentClassificationPegi.from_name(path_config.get('ContentClassificationPegi', None))
                        logger.info(root_dir_path)
                        paths_to_scan[root_dir_path] = (category, min_age)
                    except Exception as ex:
                        logger.error(f"Error while parsing configuration for path '{root_dir_path}': {ex}")
            except Exception as ex:
                logger.error(f"Error while parsing paths configuration:\n{path_configs}\nError: {ex}")

        filters_node = data.get('filters', None)
        if filters_node:
            logger.info(f"Loading filters from config file...")
            for filter_configs in filters_node:
                try:
                    for filter_name, filter_args in filter_configs.items():
                        try:
                            f: IFilter = FilterFactory.get_filter(filter_name=filter_name, **filter_args)
                            logger.info(f)
                            filters.append(f)
                        except Exception as ex:
                            logger.error(f"Error while parsing configuration for filter '{filter_configs}': {ex}")
                except Exception as ex:
                    logger.error(f"Error while parsing filters configuration:\n{filter_configs}\nError: {ex}")
        else:
            logger.warning("No filter set: listing all files can take long time!")

        save_in_db = str(data.get('save_in_db', 'true')).lower() in [1, 'yes', 'true']

        return paths_to_scan, filters, PathDataManager() if save_in_db else None


if __name__ == '__main__':
    # process()
    paths_to_scan, filters, data_manager = load_config()
    logger.success("Configuration loaded")
