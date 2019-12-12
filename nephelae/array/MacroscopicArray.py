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
        """
        Compute all CloudData, using a clustering of the data to isolate all
        the clouds.

        Parameters
        ---------

        Returns
        ---------
        """
        dataLabeled, number_of_elements = \
        ndimage.measurements.label(self.data)
        self.list_blobs = [CloudData(self, dataLabeled, i) for i in range(1,
            number_of_elements+1)]

    def coms(self):
        """
        Returns all centers of mass of all clouds present in the slice of data

        Parameters
        ---------

        Returns
        ---------
        List of Tuple
            Returns the list of coordinates on each axis of each cloud.
        """
        return [x.get_com() for x in self.list_blobs]

    def surfaces(self):
        """
        Returns all surfaces of all clouds present in the slice of data

        Parameters
        ---------

        Returns
        ---------
        List of Numbers
            Return the list of all the surfaces of clouds.
        """
        return [x.get_surface() for x in self.list_blobs]

    def bounding_boxes(self):
        """
        Returns all bounding boxes of all clouds present in the slice of data

        Parameters
        ---------

        Returns
        ---------
        List of List of Bounds
            Returns the list of the list of bounds on each coordinates
        """
        return [x.get_bounding_box() for x in self.list_blobs]

    def get_blob(self, coords):
        """
        Returns a CloudData object using a tuple a coordinates.

        Parameters
        ---------
        coords : Tuple
            A tuple of coordinates

        Returns
        ---------
        CloudData
            Returns a CloudData where coords point to, None if there is no
            Cloud.
        """
        return next((blob for blob in self.list_blobs 
                if all(blob.get_bounding_box()[i].isinside(coords[i]) for i in
                    range(len(coords)))), None)

