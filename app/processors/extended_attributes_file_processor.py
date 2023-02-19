import stat
from stat import UF_HIDDEN, SF_ARCHIVED, UF_COMPRESSED

import magic
from loguru import logger

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType


class ExtendedAttributesFileProcessor(IPathProcessor):

    def __init__(self) -> None:
        super().__init__()
        self.mime = magic.Magic(mime=True, uncompress=True)

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.info(f"Fetching file's extended attributes: {path_model}")
        path_model.reserved = crawl_event.path.is_reserved()
        path_model.mime_type = self.mime.from_file(crawl_event.path)
        path_model.content_family = PathModel.get_content_familiy_from_mime_type(mime_type=path_model.mime_type)

        lstat = crawl_event.path.lstat()
        path_model.is_windows_path = True \
            if hasattr(lstat, 'st_file_attributes') and lstat.st_file_attributes is not None \
            else False

        path_model.hidden = ExtendedAttributesFileProcessor.is_file_hidden(file_name=path_model.name, lstat=lstat)
        path_model.archive = ExtendedAttributesFileProcessor.is_file_archived(lstat=lstat)
        path_model.compressed = ExtendedAttributesFileProcessor.is_file_compressed(lstat=lstat)
        if path_model.is_windows_path:
            path_model.encrypted = lstat.st_file_attributes & stat.FILE_ATTRIBUTE_ENCRYPTED
            path_model.offline = lstat.st_file_attributes & stat.FILE_ATTRIBUTE_OFFLINE
            path_model.readonly = lstat.st_file_attributes & stat.FILE_ATTRIBUTE_READONLY
            path_model.system = lstat.st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM
            path_model.temporary = lstat.st_file_attributes & stat.FILE_ATTRIBUTE_TEMPORARY

        logger.info(f"Done fetching file's extended attributes: {path_model.path}")

    @staticmethod
    def is_file_hidden(file_name: str, lstat):
        if file_name.startswith('.'):
            return True
        if hasattr(lstat, 'st_file_attributes') and lstat.st_file_attributes:
            return lstat.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN

        if getattr(lstat, 'st_flags', 0) & UF_HIDDEN:  # OS X: file should not be displayed
            return True
        return False

    @staticmethod
    def is_file_compressed(lstat):
        if hasattr(lstat, 'st_file_attributes') and lstat.st_file_attributes:
            return lstat.st_file_attributes & stat.FILE_ATTRIBUTE_COMPRESSED

        if getattr(lstat, 'st_flags', 0) & UF_COMPRESSED:  # OS X: file is hfs-compressed
            return True
        return False

    @staticmethod
    def is_file_archived(lstat):
        if hasattr(lstat, 'st_file_attributes') and lstat.st_file_attributes:
            return lstat.st_file_attributes & stat.FILE_ATTRIBUTE_ARCHIVE

        if getattr(lstat, 'st_flags', 0) & SF_ARCHIVED:  # file may be archived
            return True
        return False
