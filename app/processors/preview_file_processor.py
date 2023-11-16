#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import os
from pathlib import Path

from loguru import logger
from thumbnail import generate_thumbnail

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType


class PreviewFileProcessor(IPathProcessor):

    def __init__(self, out_thumb_directory: Path) -> None:
        super().__init__()
        if not out_thumb_directory or not out_thumb_directory.is_dir():
            raise ValueError(f"The given path is not a valid directory: '{out_thumb_directory}'")
        self.out_thumb_directory = out_thumb_directory

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.debug(f"Computing file's thumbnail: {path_model}")
        options = {
            'trim': False,
            'height': 300,
            'width': 300,
            'quality': 85,
            'type': 'thumbnail'
        }
        try:
            thumb_output_path = os.path.join(self.out_thumb_directory, f"{path_model.hash_md5}.png")
            generate_thumbnail(crawl_event.path, thumb_output_path, options)
        except Exception as ex:
            logger.error(f"Unable to generate thumbnail from file '{path_model.full_path}': {ex}")
