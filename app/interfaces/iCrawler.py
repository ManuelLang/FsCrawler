from abc import ABC, abstractmethod


class ICrawler(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_filters') and
                callable(subclass.get_filters) and
                hasattr(subclass, 'get_observers') and
                callable(subclass.get_observers))

    @abstractmethod
    def get_filters(self):
        pass

    @abstractmethod
    def get_observers(self):
        pass
