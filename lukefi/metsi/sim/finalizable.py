from abc import ABC, abstractmethod


class Finalizable(ABC):
    @abstractmethod
    def finalize(self):
        pass
