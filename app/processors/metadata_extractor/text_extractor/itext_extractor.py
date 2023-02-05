from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List


class ITextExtractor(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'extract_text') and
                callable(subclass.extract_text) and
                hasattr(subclass, 'errors') and
                callable(subclass.errors))

    @property
    def errors(self) -> Dict[str, List[str]]:
        raise NotImplementedError()

    @abstractmethod
    def extract_text(self, path: Path) -> str:
        raise NotImplementedError()
