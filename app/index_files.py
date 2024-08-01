import time
from pathlib import Path
from typing import List

import xxhash
import logging
logging.basicConfig()
from loguru import logger

import platform

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from models.path_type import PathType

if platform.system() == "Darwin":
    from processors.metadata_extractor.mac_finfer_tags_extractor import MacFinderTagsExtractorFileProcessor
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_stage import PathStage
from processors.hash_file_processor import HashFileProcessor
from processors.metadata_extractor.extended_attributes_file_processor import ExtendedAttributesFileProcessor
from processors.metadata_extractor.keywords_file_processor import KeywordsFileProcessor
from processors.metadata_extractor.rating_file_processor import RatingFileProcessor
from database.data_manager import PathDataManager


def process_files():
    """
    Fetches scanned files from DB and then execute processor against them
    :return:
    """
    processors: List[IPathProcessor] = []

    hash_algos = {}
    # hash_algos['xxh32'] = xxhash.xxh32()      # 15 sec to hash 10 Go
    hash_algos['xxh3_64'] = xxhash.xxh3_64()  # 15 sec to hash 10 Go
    # hash_algos['md5'] = hashlib.md5()         # 22 sec to hash 10 Go
    # hash_algos['sha256'] = hashlib.sha256()   # 28 sec to hash 10 Go - Avoids risk of collisions, but much slower
    processors.append(HashFileProcessor(hash_algorithms=hash_algos))
    processors.append(RatingFileProcessor())
    processors.append(KeywordsFileProcessor())
    processors.append(ExtendedAttributesFileProcessor())
    if platform.system() == "Darwin":
        processors.append(MacFinderTagsExtractorFileProcessor())

    data_manager: PathDataManager = PathDataManager()

    process_start = time.time()
    process_size = 0
    process_nb_files = 0

    while True:
        paths: List[PathModel] = data_manager.find_paths_by_stage(PathType.FILE, PathStage.CRAWLED, max_items=2000)
        if not paths:
            logger.success("All files processed!")
            break
        total_items = len(paths)
        current_item = 0
        with data_manager.create_cursor() as cursor:
            for path_model in paths:
                current_item += 1
                process_nb_files += 1
                process_size += path_model.size
                if current_item % 30 == 0:
                    logger.info(f"{current_item}/{total_items}")
                    cursor.connection.commit()
                try:
                    for processor in processors:
                        processor.process_path(crawl_event=None, path_model=path_model)
                    path_model.path_stage = PathStage.HASH_COMPUTED
                    data_manager.save_path(cursor=cursor, path_model=path_model)
                except Exception as ex:
                    logger.error(f"{path_model.full_path}: {ex}", exec_info=True)
                    try:
                        path_model.path_stage = PathStage.PATH_DELETED
                        data_manager.save_path(cursor=cursor, path_model=path_model)
                    except Exception as ex2:
                        logger.error(f"Unable to mak path as deleted: '{path_model.full_path}'. Error: {ex2}", exec_info=True)
            if cursor:
                cursor.connection.commit()
                cursor.connection.close()

    process_end = time.time()
    duration = process_end - process_start
    logger.success(f"Total size: {process_size} Go - Scanned {process_nb_files} files in {duration:.2f} sec")


if __name__ == '__main__':
    process_files()
