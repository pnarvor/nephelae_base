import numpy as np

from nephelae.types import Bounds

from .MapInterface import MapInterface
from .GprPredictor import GprPredictor

class StdMap(MapInterface):
    def __init__(self, name, gpr, sampleSize=1):
        if not isinstance(gpr, GprPredictor):
            raise ValueError('Gpr MUST be a GprPredictor type')
        super().__init__(name, threshold=np.sqrt(gpr.kernel.variance))
        self.sampleSize = sampleSize
        self.gpr = gpr
        self.gpr.set_compute_std(True)

    def at_locations(self, locations):
        return self.gpr.at_locations[1]

    def shape(self):
        return (None, None, None, None)

    def span(self):
        return (None, None, None, None)

    def bounds(self):
        return (None, None, None, None)

    def resolution(self):
        return self.gpr.kernel.resolution()

    def sample_size(self):
        return self.sampleSize
    
    def __getitem__(self, keys):
        return self.gpr.get_std(keys)
