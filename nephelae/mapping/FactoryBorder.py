import abc

class FactoryBorder(abc.ABC):

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def compute_borders(self, arrays):
        pass

    @abc.abstractmethod
    def get_arrays(self, keys):
        pass

    def __getitem__(self, keys):
        arrays = self.get_arrays(keys)
        return self.compute_borders(arrays)
