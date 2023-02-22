#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from loguru import logger
from pdf2image.pdf2image import convert_from_path


class PdfPicturePrinter:

    def __init__(self) -> None:
        super().__init__()
        self._errors = defaultdict(list)

    @property
    def errors(self) -> Dict[str, List[str]]:
        return self._errors

    def save_as_picture(self, path: Path, out_directory: Path) -> bool:
        if not out_directory or not out_directory.is_dir():
            raise ValueError(f"The given path is not a valid directory: '{out_directory}'")
        success: bool = True
        try:
            pages = convert_from_path(path, 200)
            for i in range(len(pages)):
                try:
                    out_file = os.path.join(out_directory, f"{path.name}-page_{i}.jpg")
                    pages[i].save(out_file, 'JPEG')
                except Exception as page_ex:
                    success = False
                    message = f"Unable to convert page {i} for PDF file '{path}'. Error: {page_ex}"
                    logger.error(message)
                    self._errors[str(path)].append(message)
                if success:
                    logger.success(f"File {path} processed!")
        except Exception as ex:
            message = f"Unable to convert PDF file to images: '{path}'. Error: {ex}"
            logger.error(message)
            self._errors[str(path)].append(message)
            success = False
        return success
