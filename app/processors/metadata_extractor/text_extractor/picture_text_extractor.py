#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import cv2
from loguru import logger
from pytesseract import image_to_string

from processors.metadata_extractor.text_extractor.itext_extractor import ITextExtractor


class PictureTextExtractor(ITextExtractor):

    def __init__(self) -> None:
        super().__init__()
        self._errors = defaultdict(list)

    @property
    def errors(self) -> Dict[str, List[str]]:
        return self._errors

    def extract_text(self, path: Path) -> str:
        """
        https://stackoverflow.com/questions/65802129/pytesseract-output-is-extremely-inaccurate-mac
        :param path:
        :return:
        """
        result: str = ''
        try:
            img = cv2.imread(path)
            # kernel = np.ones((4,4),np.uint8)
            # opn = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
            txt = image_to_string(img)
            txt = txt.split("\n")
            result = ''.join([i.strip() for i in txt if i != '' and len(i) > 3])
            logger.success(f"File {path} processed!")
        except Exception as ex:
            message = f"Unable to convert PDF file to images: '{path}'. Error: {ex}"
            logger.error(message)
            self._errors[str(path)].append(message)
        return result
