import abc

from .MapInterface import MapInterface

class FactoryBorder(MapInterface):

    def __init__(self, name, sampleSize=1):
        super().__init__(name)
        self.sampleSize = sampleSize

    @abc.abstractmethod
    def get_arrays(self, keys):
        pass

    def sample_size(self):
        return self.sampleSize
    
    def shape(self):
        return (None, None, None, None)

    def span(self):
        return (None, None, None, None)
    
    def bounds(self):
        return (None, None, None, None)

    def __getitem__(self, keys):
        arrays = self.get_arrays(keys)
        return self.at_locations(arrays)
