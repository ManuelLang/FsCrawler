#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from typing import List

import macos_tags
from loguru import logger
from macos_tags._api import Tag

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType

_FINDER_INFO_TAG = u'com.apple.FinderInfo'

COLORS = {'none': 0, 'gray': 2, 'green': 4, 'purple': 6,
          'blue': 8, 'yellow': 10, 'red': 12, 'orange': 14}
NAMES = {0: 'none', 2: 'gray', 4: 'green', 6: 'purple',
         8: 'blue', 10: 'yellow', 12: 'red', 14: 'orange'}

BLANK = 32 * chr(0)


class MacFinderTagsExtractorFileProcessor(IPathProcessor):

    def __init__(self) -> None:
        super().__init__()

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.info(f"Fetching file's Finder labels: {path_model}")
        tags: List[Tag] = macos_tags.get_all(crawl_event.path)
        for t in tags:
            path_model.tags[t.name] = t.color.name
        logger.info(f"Done fetching file's labels from Finder: {path_model.full_path}")

# if __name__ == '__main__':
#     filepath = '/Volumes/Data/Films/This Is England.avi'
#     tags: List[Tag] = macos_tags.get_all(filepath)
#     file_labels_dict = [{"name": t.name, "color": t.color.name} for t in tags]
#     print(file_labels_dict)
# attrs = xattr(filepath)
# print(attrs.list())
# finder_label = ExtendedAttributesFileProcessor.get_finder_color(filepath)
# print(finder_label)
