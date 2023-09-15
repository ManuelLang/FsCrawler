#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from os import path
from pathlib import Path

from loguru import logger

from app.crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from app.helpers.shutil_custom import _ensure_directory, copy2
from app.interfaces.iPathProcessor import IPathProcessor
from app.models.path import PathModel
from app.models.path_type import PathType
from app.processors.delete_path_processor import DeletePathProcessor
from models.file import FileModel

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
        logger.info(f"Copying file '{path_model.full_path}' to '{self.dest_dir_path}'")

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

            dest_path = Path(dstname)
            if dest_path.exists() and dest_path.is_file():
                if path.getsize(crawl_event.path) == path.getsize(dstname):
                    logger.debug(f"Skip path {crawl_event.path} because it already exists")
                    return  # Same filename and same size: skip the file (duplicate)
                else:
                    # Same filename, different size: perform a soft delete
                    logger.info(
                        f"Deleting file {path_model.full_path} (because destination already exists and have different size)")
                    dst_file_model = FileModel(root=path_model.root, path=dest_path, size_in_mb=path_model.size_in_mb)
                    self.delete_file_processor.process_path(
                        crawl_event=FileCrawledEventArgs(
                            crawler=crawl_event.crawler,
                            path=dest_path,
                            is_dir=False,
                            is_file=True,
                            size_in_mb=crawl_event.size_in_mb,
                            root_dir_path=crawl_event.root_dir_path
                        ),
                        path_model=dst_file_model)

            # https://stackoverflow.com/questions/123198/how-to-copy-files
            dst_file, fsize = copy2(crawl_event.path, dstname)
            logger.info(f"Done copying file {path_model.full_path} ({dst_file}/{fsize})")
        except Exception as ex:
            logger.error(f"Unable to copy file '{path_model.full_path}': {ex}")
