# abc = abstract class
import abc
import numpy as np

from nephelae.array import ScaledArray
from nephelae.array import DimensionHelper
from nephelae.types import Bounds

class MapInterface(abc.ABC):

    """MapInterface

    This is an interface designed to be subclassed with
    nephelae.mappin.GprPredictor class and nephelae_mesonh.MesoNHVariable.
    Its goal is to give a unique access for static MesoNH data in simulation
    or real time data estimation with flying UAVs. This allows to simplify
    the design of the interface with the GUI components, since they only see
    maps of the same type.

    A map can be defined on a space with an arbitrary number of dimensions.
    A single map sample can also have an arbitrary number of dimensions.

    /!\ This in an abstract class. It cannot be instanciated, and must be
    subclassed. All the methods with the "abc.abstractmethod" decorator
    must be implemented in the sub-class. nephelae.mappin.GprPredictor class
    and nephelae_mesonh.MesoNHVariable are examples of classes derived from
    MapInterface.

    Attributes
    ----------

    name : str
        A unique identifer for this map instance.
    """

    def __init__(self, name):
        """
        Parameters
        ----------

        name : str
            A unique identifer for this map instance.
        """

        self.name = name


    @abc.abstractmethod
    def at_locations(self, locations):
        """Returns map value at sparse locations
        
        Parameters
        ----------

        input : NxD numpy.array
            Location of the sample to fetch.
            (N : number of locations, D : number dimensions of space)

        output : NxM numpy.array
            Map value at each location.
            (N : number of locations, M : number of dimensions of a map sample)
        """
        pass


    @abc.abstractmethod
    def shape(self):
        """
        List size of each dimension. Must be empty if no dimensions,
        and a size can be equal to None if the dimension if infinite.
        (For example with a periodic dimension).

        Returns
        -------
            tuple(int,None,...) or ()
        """
        pass


    @abc.abstractmethod
    def span(self):
        """
        Physical length of each dimension (for example in meters).
        Must be empty if no dimensions, and a length can be equal to None if
        the dimension if infinite. (For example with a periodic dimension).

        Returns
        -------
            tuple(float,None,...) or ()
        """
        pass


    @abc.abstractmethod
    def bounds(self):
        """
        Physical bounds of each dimension (mix and max value in each dimension).
        Must be empty if no dimensions, and an element can be equal to None if
        the dimension if infinite. (For example with a periodic dimension).

        Returns
        -------
            tuple(nephelae.type.Bounds,None,...) or ()
        """
        pass


    @abc.abstractmethod
    def resolution(self):
        """
        Resolution of each dimension (for example in pixels per meters).
        Can be empty if no dimensions.
        MUST be defined for each dimension.

        Returns
        -------
            tuple(float,...) or ()
        """
        pass


    @abc.abstractmethod
    def computes_stddev(self):
        """
        Tells if the standard deviation is computed.
        (and returned by [] operator). This is for compatibility with
        nephelae.mapping.GprPredictor.

        /!\ Will probably be deleted in near future. (Compatibility with
        GprPredictor might be resolved with a cached stddev map).

        Returns
        -------
        boolean
            True if [] operator also returns the standard deviation.
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
        Returns min and max values inside the map (mostly for display, to
        avoid finding min-max each render for the colorscale normalization).
        Can be None if not computed.
        
        Returns
        -------
        Bounds or (Bounds,...)
            Can return a tuple of Bounds if sample dimension > 1.
        """
        return None


    def __getitem__(self, keys):
        """
        Returns a slice of map data ([] operator).

        Parameters
        ----------
        keys : (int,float,slice,...)
            keys like for reading a numpy.array.

        Returns
        -------
        numpy.array
            Section of space selected with keys.
            (to be changed with a nephelae.array.ScaledArray ?).
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

