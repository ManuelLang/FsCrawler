from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from loguru import logger
from tika import parser

from processors.metadata_extractor.text_extractor.itext_extractor import ITextExtractor


class PdfTextExtractorTika(ITextExtractor):

    def __init__(self) -> None:
        super().__init__()
        self._errors = defaultdict(list)

    @property
    def errors(self) -> Dict[str, List[str]]:
        return self._errors

    def extract_text(self, path: Path) -> str:
        """
        https://stackoverflow.com/questions/34837707/how-to-extract-text-from-a-pdf-file
        :param path:
        :return:
        """
        result: str = ''
        try:
            raw = parser.from_file(path)
            result = raw['content']
            logger.success(f"File {path} processed!")
        except Exception as ex:
            message = f"Unable to extract text from PDF file: '{path}'. Error: {ex}"
            logger.error(message)
            self._errors[str(path)].append(message)
        return result
