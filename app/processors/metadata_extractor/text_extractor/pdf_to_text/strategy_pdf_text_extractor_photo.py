import os
import random
import string
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from loguru import logger

from processors.metadata_extractor.picture_exporter.pdf_picture_printer import PdfPicturePrinter
from processors.metadata_extractor.text_extractor.itext_extractor import ITextExtractor
from processors.metadata_extractor.text_extractor.picture_text_extractor import PictureTextExtractor


class PdfTextExtractorPhoto(ITextExtractor):

    def __init__(self) -> None:
        super().__init__()
        self._errors = defaultdict(list)

    @property
    def errors(self) -> Dict[str, List[str]]:
        return self._errors

    def extract_text(self, path: Path) -> str:
        result: str = ''
        string_path = str(path)
        random_name = ''.join(random.choice(string.ascii_lowercase) for i in range(12))
        temp_dir_path = Path(os.path.join(tempfile.gettempdir(), 'PdfTextExtractorPhoto', random_name))
        temp_dir_path.mkdir(parents=True, exist_ok=True)
        text_pages: List[str] = []
        pdf_picture_printer = PdfPicturePrinter()
        photo_text_extractor = PictureTextExtractor()
        try:
            if pdf_picture_printer.save_as_picture(path=path, out_directory=temp_dir_path):
                for dir_item in sorted(temp_dir_path.iterdir()):
                    if not dir_item.is_file():
                        continue
                    text_pages.append(photo_text_extractor.extract_text(path=dir_item))
                if photo_text_extractor.errors.get(string_path, []):
                    self._errors[string_path].extend(photo_text_extractor.errors[string_path])
            if pdf_picture_printer.errors.get(string_path, []):
                self._errors[string_path].extend(pdf_picture_printer.errors[string_path])
            logger.success(f"File {path} processed!")
        except Exception as ex:
            message = f"Unable to extract text from PDF file: '{path}'. Error: {ex}"
            logger.error(message)
            self._errors[str(path)].append(message)
        return result
