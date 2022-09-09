from loguru import logger

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType


class PreviewFileProcessor(IPathProcessor):

    def __init__(self) -> None:
        super().__init__()

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.info(f"Computing file's thumbnail: {path_model}")
