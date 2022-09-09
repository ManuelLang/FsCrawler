from abc import ABC, abstractmethod

from crawler.events.pathEventArgs import PathEventArgs
from models.path import PathModel
from models.path_type import PathType


class IPathProcessor(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'processor_type') and
                callable(subclass.processor_type) and
                hasattr(subclass, 'process_path') and
                callable(subclass.process_path)
                )

    @property
    def processor_type(self) -> PathType:
        raise NotImplementedError()

    @abstractmethod
    def process_path(self, crawl_event: PathEventArgs, path_model: PathModel):
        raise NotImplementedError()
