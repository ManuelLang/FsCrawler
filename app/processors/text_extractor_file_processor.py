#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import os
from pathlib import Path

import textract
from loguru import logger

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iPathProcessor import IPathProcessor
from models.content import ContentFamily
from models.path import PathModel
from models.path_type import PathType
from processors.metadata_extractor.text_extractor.itext_extractor import ITextExtractor
from processors.metadata_extractor.text_extractor.pdf_text_extractor import PdfTextHandler
from processors.metadata_extractor.text_extractor.picture_text_extractor import PictureTextExtractor


class TextExtractorFileProcessor(IPathProcessor):

    def __init__(self, out_text_directory: Path) -> None:
        super().__init__()
        if not out_text_directory or not out_text_directory.is_dir():
            raise ValueError(f"The given path is not a valid directory: '{out_text_directory}'")
        self.out_text_directory = out_text_directory
        self.max_size: int = 10 * 1024 * 1024

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.debug(f"Extracting file's text: {path_model}")
        text: str = ''
        try:
            if crawl_event.size < self.max_size:
                text = textract.process(crawl_event.path)
        except Exception as ex:
            try:
                text_extractor: ITextExtractor = None
                if path_model.content_family == ContentFamily.PICTURE:
                    text_extractor = PictureTextExtractor()
                elif path_model.extension == 'pdf':
                    text_extractor = PdfTextHandler()

                text = text_extractor.extract_text(crawl_event.path)
            except Exception as ex2:
                logger.error(f"Unable to extract text from file '{path_model.full_path}': {ex}")

        if text:
            text_output_path = os.path.join(self.out_text_directory, f"{path_model.hash_md5}.txt")
            with open(text_output_path, 'w') as f:
                f.write(text)
