import numpy as np

import threading

from nephelae.types import Bounds

from .MapInterface import MapInterface
from .GprPredictor import GprPredictor

class ValueMap(MapInterface):
    def __init__(self, name, gpr, sampleSize=1):
        super().__init__(name)
        self.sampleSize = sampleSize
        if not isinstance(gpr, GprPredictor):
            raise ValueError('Gpr MUST be a GprPredictor type')
        self.gpr = gpr
        self.keys = None

    def at_locations(self, locations):
        if self.gpr.locationsLock.acquire(blocking=True, timeout=1.0):
            try:
                if not self.gpr.checkCache(self.keys):
                    self.gpr.setKeys(self.keys)
                    self.gpr.computeMaps(locations)
                res = self.gpr.cache[0]
            finally:
                self.gpr.locationsLock.release()
        else:
            cond = threading.Condition(self.gpr.locationsLock)
            cond.wait_for(cond.wait())
            res = self.at_locations(locations)
        return res

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
        if self.gpr.getItemLock.acquire(blocking=True, timeout=1.0):
            try:
                self.setKeys(keys)
                res = super().__getitem__(keys)
            finally:
                self.gpr.getItemLock.release()
        else:
            cond = threading.Condition(self.gpr.getItemLock)
            cond.wait_for(cond.wait())
            res = self.__getitem__(keys)
        return res

    def setKeys(self, keys):
        self.keys = keys
