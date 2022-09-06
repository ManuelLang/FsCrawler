from abc import ABC, abstractmethod


class ICrawlingQueueConsumer(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'pop_item') and
                callable(subclass.pop_item))

    @abstractmethod
    def pop_item(self):
        raise NotImplementedError()
