#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from loguru import logger

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from helpers.shutil_custom import _ensure_directory, copy2
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType

BUF_SIZE = 64 * 1024 * 100  # lets read stuff in 6,4 Mb chunks!


class CopyFileProcessor(IPathProcessor):

    def __init__(self, dest_dir_path: str) -> None:
        super().__init__()
        self.dest_dir_path = dest_dir_path
        _ensure_directory(self.dest_dir_path)
        if self.dest_dir_path[-1] == '/':
            self.dest_dir_path = self.dest_dir_path[:-1]

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.info(f"Hashing file: {path_model}")
        try:
            dest_sub_dir_path = str(crawl_event.path).replace(str(crawl_event.root_dir_path) + '/', '')
            dstname = f"{self.dest_dir_path}/{dest_sub_dir_path}"
            _ensure_directory(dstname)
            dst_file, fsize = copy2(crawl_event.path, dstname)
            logger.debug(f"Done copying file {path_model.full_path}")
        except Exception as ex:
            logger.error(f"Unable to copy file '{path_model.full_path}': {ex}")
