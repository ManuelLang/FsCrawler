#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from os import path

from loguru import logger

from app.crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from app.helpers.shutil_custom import _ensure_directory, copy2
from app.interfaces.iPathProcessor import IPathProcessor
from app.models.path import PathModel
from app.models.path_type import PathType
from app.processors.delete_path_processor import DeletePathProcessor

BUF_SIZE = 64 * 1024 * 100  # lets read stuff in 6,4 Mb chunks!


class CopyPathProcessor(IPathProcessor):

    def __init__(self, dest_dir_path: str) -> None:
        super().__init__()
        self.dest_dir_path = dest_dir_path
        _ensure_directory(self.dest_dir_path)
        if self.dest_dir_path[-1] == '/':
            self.dest_dir_path = self.dest_dir_path[:-1]
        self.delete_file_processor = DeletePathProcessor()

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.info(f"Copying file '{path_model}' to '{self.dest_dir_path}'")

        if not crawl_event.path.exists():
            logger.debug(f"Path does not exists anymore. Ignoring {crawl_event.path}")
            return

        crawled_path = str(crawl_event.path)[:-1] if str(crawl_event.path)[-1] == '/' else str(crawl_event.path)
        if crawled_path == self.dest_dir_path:
            logger.debug(f"Ignoring {crawl_event.path} because it is the same as destination")
            return

        try:
            dest_sub_dir_path = str(crawl_event.path).replace(str(crawl_event.root_dir_path) + '/', '')
            dstname = f"{self.dest_dir_path}/{dest_sub_dir_path}"
            _ensure_directory(dstname)

            if path.exists(dstname):
                if path.getsize(crawl_event.path) == path.getsize(dstname):
                    return  # Same filename and same size: skip the file (duplicate)
                else:
                    # Same filename, different size: perform a soft delete
                    self.delete_file_processor.process_path(crawl_event=crawl_event, path_model=path_model)

            # https://stackoverflow.com/questions/123198/how-to-copy-files
            dst_file, fsize = copy2(crawl_event.path, dstname)
            logger.debug(f"Done copying file {path_model.full_path}")
        except Exception as ex:
            logger.error(f"Unable to copy file '{path_model.full_path}': {ex}")
