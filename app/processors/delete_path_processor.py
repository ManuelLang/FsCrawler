#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
import re
import shutil
import sys
from os import path
from pathlib import Path

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO")

from app.crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from app.interfaces.iPathProcessor import IPathProcessor
from app.models.path import PathModel
from app.models.path_type import PathType
from app.helpers.shutil_custom import _ensure_directory


class DeletePathProcessor(IPathProcessor):

    def __init__(self, trashbin_path: str = f"{Path.home()}/.delete") -> None:
        super().__init__()
        self.dest_dir_path = trashbin_path
        _ensure_directory(self.dest_dir_path)
        if self.dest_dir_path[-1] == '/':
            self.dest_dir_path = self.dest_dir_path[:-1]
        self.path_home_str = str(Path.home())

    @property
    def processor_type(self) -> PathType:
        return PathType.ALL

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        item: str = 'directory' if crawl_event.is_dir else 'file'
        logger.info(f"Deleting {item}: {path_model.path_root}{path_model.relative_path}")

        if not crawl_event.path.exists():
            logger.debug(f"Path does not exists anymore. Ignoring {crawl_event.path}")
            return

        crawled_path = str(crawl_event.path)[:-1] if str(crawl_event.path)[-1] == '/' else str(crawl_event.path)
        if crawled_path == self.path_home_str or crawled_path == self.dest_dir_path:
            logger.debug(f"Ignoring {crawl_event.path} because it's a special path")
            return

        try:
            dest_sub_dir_path = str(crawl_event.path).replace(str(crawl_event.root_dir_path), '')
            dstname = f"{self.dest_dir_path}/{dest_sub_dir_path}"

            _ensure_directory(dstname)

            # Make sure the file does not exist in the destination directory, else add incremental suffix
            i = 0
            _rex = re.compile("(\d+)$")
            while path.exists(dstname) and i < 10:
                i += 1
                filename, file_extension = path.splitext(dstname)
                if _rex.fullmatch(filename):
                    filename = filename[0:filename.rfind('(')]

                dstname = f"{filename} ({i}).{file_extension}" if file_extension else f"{filename} ({i})"

            src_file = str(crawl_event.path)

            shutil.move(src_file, dstname)
            logger.debug(f"Done deleting {item} {path_model.full_path}")
        except Exception as ex:
            logger.error(f"Unable to delete {item} '{path_model.full_path}': {ex}")
