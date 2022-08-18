from pathlib import Path

from app.helpers.serializationHelper import JsonDumper
from app.interfaces.iAccountCrawler import IAccountCrawler
from app.interfaces.iFilter import IFilter


class Filter(IFilter):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'can_process') and
                callable(subclass.can_process) and
                hasattr(subclass, 'authorize') and
                callable(subclass.authorize))

    def can_process(self, crawler: IAccountCrawler, path: Path) -> bool:
        return True if path and path.exists() else False

    def authorize(self, crawler: IAccountCrawler, path: Path) -> bool:
        return self.can_process(crawler, path)

    def to_json(self) -> dict:
        return {}

    def __str__(self) -> str:
        return JsonDumper.dumps({
            self.__class__.__name__: self.to_json()
        })
