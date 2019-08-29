# abc = abstract class
import abc
import numpy as np

from nephelae.array import ScaledArray
from nephelae.array import DimensionHelper
from nephelae.types import Bounds

class MapInterface(abc.ABC):

    """MapInterface

    This is an interface designed to be subclassed with GprPredictor class
    and MesoNHVariable. Its goal is to give a unified access for static
    MesoNH data in simulation or real time data estimation with flying uavs.

    """

    def __init__(self, name):

        self.name = name


    @abc.abstractmethod
    def at_locations(self, locations):
        """
        return variable value at locations

        input:
            locations: N*D np.array (N location, D dimensions)

        output:
            NxM np.array : variable value at locations
                           (variable is M dimensionnal)
        """
        pass


    @abc.abstractmethod
    def shape(self):
        """
        List of number of data points in each dimensions.
        Can be empty if no dimensions, and element can be None
        if infinite dimension span
        """
        pass


    @abc.abstractmethod
    def span(self):
        """
        Returns a list of span of each dimension.
        Can be empty if no dimensions, and element can be None
        if infinite dimension span
        """
        pass


    @abc.abstractmethod
    def bounds(self):
        """
        Returns a list of bounds of each dimension.
        Can be empty if no dimensions, and element can be None
        if infinite dimension span
        """
        pass


    @abc.abstractmethod
    def resolution(self):
        """
        Return a list of resolution in each dimension
        Can be empty if no dimensions.
        Is ALWAYS defined for each dimension.
        """
        pass


    @abc.abstractmethod
    def computes_stddev(self):
        """
        Tells if a standard deviation is computed
        """
        pass
    
    
    # # @abc.abstractmethod
    # def sample_dims(self):
    #     """
    #     Returns the number of scalars in a single sample
    #     (Usually 1)
    #     """
    #     pass

    
    def range(self):
        """
        Returns bounds of values inside the map (mostly for display)
        Can be None if not computed

        Must be a list of instances of nephelae.types.Bounds
        """
        return None


    def __getitem__(self, keys):
        """
        return a slice of space filled with variable values.

        input:
            keys like reading a numpy.array (tuple of slice)

        output:
            numpy.array with values (squeezed in collapsed dimensions)
        """

        # print("keys :", keys)
        # print("resolution :", self.resolution())

        params = []
        for key, res in zip(keys, self.resolution()):
            if isinstance(key, slice):
                size = int((key.stop - key.start) / res) + 1
                params.append(np.linspace(key.start, key.start+(size-1)*res, size))
            else:
                params.append(key)

        T,X,Y,Z = np.meshgrid(params[0], params[1], params[2], params[3],
                              indexing='xy', copy=False)
        locations = np.array([T.ravel(), X.ravel(), Y.ravel(), Z.ravel()]).T

        # check this (sorting ?)
        # pred = self.at_locations(locations[np.argsort(locations[:,0]),:])
        # pred = self.at_locations(locations, False)
        # pred = self.at_locations(locations, True)
        pred = self.at_locations(locations)
        dims = DimensionHelper()
        for param in params:
            if np.array(param).shape:
                dims.add_dimension(param, 'LUT')
        # if isinstance(pred, (list, tuple)):
        if self.computes_stddev():
            outputShape = list(T.shape)
            res = [ScaledArray(pred[1].reshape(outputShape).squeeze(), dims)]
            if len(pred[0].shape) == 2:
                outputShape.append(pred[0].shape[1])
            res.insert(0,ScaledArray(pred[0].reshape(outputShape).squeeze(), dims))
            return res
        else:
            outputShape = list(T.shape)
            if len(pred.shape) == 2:
                outputShape.append(pred.shape[1])
            return ScaledArray(pred.reshape(outputShape).squeeze(), dims)

