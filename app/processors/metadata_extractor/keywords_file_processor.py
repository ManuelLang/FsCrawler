#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
import sys
from pathlib import Path

if __name__ == '__main__':
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[2]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError:  # Already removed
        pass

    __package__ = 'app'

import re
from loguru import logger

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType


class KeywordsFileProcessor(IPathProcessor):
    def __init__(self) -> None:
        super().__init__()

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.debug(f"Fetching keywords based on naming convention: {path_model.full_path}")
        if '- ' in path_model.name:
            parts = reversed(path_model.name.split('-'))
            for part in parts:
                if path_model.keywords:
                    break
                path_model.keywords = self.split_words(part)
        if not path_model.keywords:
            parts = reversed(path_model.name.split('['))
            for part in parts:
                part = part.replace(']', '')
                if path_model.keywords:
                    break
                path_model.keywords = self.split_words(part)
        if path_model.keywords:
            logger.info(f"Found keywords: {path_model.keywords} ({path_model.name})")
        logger.debug(f"Done fetching file's keywords: {path_model.keywords}\n{path_model.full_path}")

    def find_keywords_part(self, path_model: PathModel, part_start: str = '[', part_end: str = ']'):
        if part_start not in path_model.name:
            return None
        parts = reversed(path_model.name.split(part_start))
        start_index = str(path_model.name).rfind(part_start)
        end_index = str(path_model.name).rfind(part_end)
        if start_index < 0 or end_index < start_index:
            return None
        for part in parts:
            part = part.replace(']', '')
            keywords = self.split_words(part)
            return keywords
        return None

    def split_words(self, part: str) -> str | None:
        part = part.replace('.', ', ').replace('_', ', ')
        if ', ' in part:
            if re.findall('[^a-zA-Z0-9,\s\]]+', part):
                return None
            keywords = [str(k).strip() for k in part.split(', ')]
            return ','.join(keywords)
        return None


# if __name__ == '__main__':
#     KeywordsFileProcessor().process_path(
#         None,
#         PathModel(root='/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b/',
#                   path='/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b/xyz')
#     )
