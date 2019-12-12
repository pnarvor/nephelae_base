import numpy as np
from scipy import ndimage

from .ScaledArray import ScaledArray
from nephelae.database import CloudData

class MacroscopicArray(ScaledArray):

    def __init__(self, data, dimHelper, interpolation='nearest'):
        super().__init__(data, dimHelper, interpolation)
        # -- Element Clustering --
        self.__compute_blobs()

    def __compute_blobs(self):
        dataLabeled, number_of_elements = \
        ndimage.measurements.label(self.data)
        self.list_blobs = [CloudData(self, dataLabeled, i) for i in range(1,
            number_of_elements+1)]

    def coms(self):
        return [x.get_com() for x in self.list_blobs]

    def surfaces(self):
        return [x.get_surface() for x in self.list_blobs]

    def bounding_boxes(self):
        return [x.get_bounding_box() for x in self.list_blobs]

    def getBlob(self, coords):
        return next(blob for blob in self.list_blobs 
                if all(bounds.is_inside(coord) for coord in coords
                    for bounds in blob.boundingBox))

