import numpy as np
from scipy import ndimage

from nephelae.types import Bounds
class CloudData:
    
    def __init__(self, scArr, dataLabeled, index):
        self.__scArr = scArr
        self.__dataLabeled = dataLabeled
        self.__index = index

        self.__locations = None
        self.__com = None
        self.__surface = None
        self.__boundingBox = []


    def get_com(self):
        if self.__com is None:
            self.__compute_com()
        return self.__com
    
    def get_surface(self):
        if self.__surface is None:
            self.__compute_surface()
        return self.__surface

    def get_locations(self):
        if self.__locations is None:
            self.__compute_locations()
        return self.__locations

    def get_bounding_box(self):
        if not self.__boundingBox:
            self.__compute_bounding_box()
        return self.__boundingBox

    def is_in_bounding_box(self, coords):
        return all(self.get_bounding_box()[i].isinside(coords[i]) for i in
                range(len(coords)))

    @classmethod
    def from_scaledArray(cls, scArr):
        dataLabeled, number_of_elements = \
        ndimage.measurements.label(scArr.data)
        return [CloudData(scArr, dataLabeled, i)
                for i in range(1, number_of_elements+1)]

    def __compute_com(self):
        indices = tuple(np.array(self.get_locations()[i]) for i in
                range(self.get_locations().shape[0]))
        data = self.__scArr.data[indices].ravel()
        self.__com = (np.sum(self.get_locations()*data,
                axis=1)/np.sum(data)).tolist()

    def __compute_locations(self):
        out = np.where(self.__dataLabeled == self.__index)
        self.__locations = np.array([X for X in out])

    def __compute_bounding_box(self):
        mins = self.__scArr.dimHelper.to_unit(np.amin(self.get_locations(),
            axis=1).tolist())
        maxs = self.__scArr.dimHelper.to_unit(np.amax(self.get_locations(),
            axis=1).tolist())
        self.__boundingBox = [Bounds(mins[i], maxs[i]) for i in range(len(mins))]


    def __compute_surface(self):
        self.__surface = self.get_locations().shape[1]
