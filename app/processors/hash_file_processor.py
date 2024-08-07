#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from typing import Dict

from loguru import logger

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType

BUF_SIZE = 64 * 1024 * 100  # lets read stuff in 6,4 Mb chunks!


class HashFileProcessor(IPathProcessor):

    def __init__(self, hash_algorithms: Dict[str, object]) -> None:
        super().__init__()
        self._hash_algorithms: Dict[str, object] = hash_algorithms

    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.debug(f"Hashing file: {path_model}")
        try:
            self._hash_digest(crawl_event=crawl_event, path_model=path_model)
            logger.debug(f"Done hashing file {path_model.full_path}")
        except Exception as ex:
            logger.error(f"Unable to hash file '{path_model.full_path}': {ex}")
            raise ex

    def _hash_digest(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        with open(path_model.full_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                for name, hash_algo in self._hash_algorithms.items():
                    hash_algo.update(data)
        for name, hash_algo in self._hash_algorithms.items():
            if len(self._hash_algorithms.keys()) == 1:
                path_model.hash = hash_algo.hexdigest()
            else:
                property_name = f"hash_{name.lower()}"
                if hasattr(path_model, property_name):
                    setattr(path_model, property_name, hash_algo.hexdigest())
                else:
                    logger.error(f"Hash algorithm not supported: {name}")
