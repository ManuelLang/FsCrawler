#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
import re
from loguru import logger

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType

from models.rating import Rating


class RatingFileProcessor(IPathProcessor):
    def __init__(self) -> None:
        super().__init__()

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.debug(f"Fetching content rating based on naming convention: {path_model.full_path}")
        matches = re.findall(r'([\+]+)', path_model.full_path)
        if matches:
            counter = matches[0].count('+')
            rating = min(int(counter), Rating.EXCELLENT.value)
            if rating > 0:
                path_model.content_rating = Rating(rating)
                logger.info(f"Found rating: {path_model.content_rating} ({path_model.name})")
        logger.debug(f"Done fetching file's rating: {path_model.content_rating}\n{path_model.full_path}")


