from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from loguru import logger

from processors.metadata_extractor.text_extractor.itext_extractor import ITextExtractor
from processors.metadata_extractor.text_extractor.pdf_to_text.strategy_pdf_text_extractor_photo import \
    PdfTextExtractorPhoto
from processors.metadata_extractor.text_extractor.pdf_to_text.strategy_pdf_text_extractor_pyPdf2 import \
    PdfTextExtractorPyPdf2
from processors.metadata_extractor.text_extractor.pdf_to_text.strategy_pdf_text_extractor_pymupdf import \
    PdfTextExtractorPyMuPDF
from processors.metadata_extractor.text_extractor.pdf_to_text.strategy_pdf_text_extractor_tika import \
    PdfTextExtractorTika


class PdfTextHandler(ITextExtractor):

    def __init__(self) -> None:
        super().__init__()
        self._errors = defaultdict(list)

        self.handlers: List[ITextExtractor] = []

        # https://github.com/py-pdf/benchmarks
        self.handlers.append(PdfTextExtractorPyMuPDF())
        self.handlers.append(PdfTextExtractorTika())
        self.handlers.append(PdfTextExtractorPyPdf2())
        self.handlers.append(PdfTextExtractorPhoto())

    @property
    def errors(self) -> Dict[str, List[str]]:
        return self._errors

    def extract_text(self, path: Path) -> str:
        result_text = ''
        string_path = str(path)
        for handler in self.handlers:
            result_text = handler.extract_text(path=path)
            if handler.errors.get(string_path, []):
                self._errors[string_path].extend(handler.errors[string_path])
            elif result_text:
                return result_text
        logger.error(f"Unable to extract text from PDF file '{path}'. All strategies failed.")
        return result_text
