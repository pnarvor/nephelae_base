import numpy as np

from nephelae.types import Bounds
class CloudData:
    
    def __init__(self, scArr, dataLabeled, index):
        self.scArr = scArr
        self.dataLabeled = dataLabeled
        self.index = index

        self.locations = None
        self.com = None
        self.surface = None
        self.boundingBox = []


    def get_com(self):
        if self.com is None:
            self.__compute_com()
        return self.com
    
    def get_surface(self):
        if self.surface is None:
            self.__compute_surface()
        return self.surface

    def get_locations(self):
        if self.locations is None:
            self.__compute_locations()
        return self.locations

    def get_bounding_box(self):
        if not self.boundingBox:
            self.__compute_bounding_box()
        return self.boundingBox

    def __compute_com(self):
        indices = tuple(np.array(self.get_locations()[i]) for i in
                range(self.get_locations().shape[0]))
        data = self.scArr.data[indices].ravel()
        self.com = np.sum(self.get_locations()*data, axis=1)/np.sum(data)

    def __compute_locations(self):
        out = np.where(self.dataLabeled == self.index)
        self.locations = np.array([X for X in out])

    def __compute_bounding_box(self):
        mins = self.scArr.dimHelper.to_unit(np.amin(self.get_locations(),
            axis=1).tolist())
        maxs = self.scArr.dimHelper.to_unit(np.amax(self.get_locations(),
            axis=1).tolist())
        self.boundingBox = [Bounds(mins[i], maxs[i]) for i in range(len(mins))]

    def __compute_surface(self):
        self.surface = self.get_locations().shape[1]
