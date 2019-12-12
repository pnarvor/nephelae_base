"""DimensionHelper module

Contains a bunch of helper classes mostly used in the array.ScaledArray type.

The goal of the ScaledArray type is to be able to access a data array using
floating point indexes instead of integer indexes.

The idea behind this is that the data array represent a section of space.
For example a MesoNH data cube represent a cube of atmosphere. This cube has a size
in number of lines and columns, 
"""

import numpy as np
from scipy.interpolate import griddata
from scipy.interpolate import interp1d

from nephelae.types import Bounds

class AffineTransform:
    

    def __init__(self, alpha, beta):
        self.alpha = alpha
        self.beta  = beta


    def __call__(self, x):
        return self.alpha * x + self.beta


class UnitsIndexConverter:

    """UnitsIndexConverter

    Base class to transform a tuple of index based indexing to a 
    tuple of units based indexing and vice-versa.

    /!\ Is an abstract class. Concrete child classes must implement
        toUnits(key) and toIndex(key).
    """

    def __init__(self, dimSize):
        self.dimSize = dimSize


    def to_unit(self, key):
        
        if isinstance(key, (int, float)):
            return float(self.toUnit(key))
        elif type(key) == slice:
            if key.start is None:
                key_start = self.to_unit(0)
            else:
                key_start = self.to_unit(key.start)
            if key.stop is None:
                key_stop = self.to_unit(self.dimSize - 1)  # -1 because python slice...
            else:
                key_stop = self.to_unit(key.stop - 1) # -1 because python slice...
            return slice(key_start, key_stop, None)
        else:
            raise ValueError("key must be a slice or a numeric type.")


    def to_index(self, key):
        
        if isinstance(key, (int, float)):
            return int(self.toIndex(key) + 0.5) # rounding to closest integer
        elif type(key) == slice:
            if key.start is None:
                key_start = 0
            else:
                key_start = int(self.to_index(key.start))
            if key.stop is None:
                key_stop = self.dimSize
            else:
                key_stop = self.to_index(key.stop) + 1 # +1 because python slice...
            return slice(key_start, key_stop, None)
        else:
            raise ValueError("key must be a slice or a numeric type.")


    def linear_interpolation_indexes(self, key):
        
        """
        If key is a scalar, returns two pairs (key, weight) which are 
        to be used to compute a weighted sum of two elements in an array,
        effectively computing a linear interpolation.
        If key is a slice, returns a single pair (key, weight), with 
        the key being self.to_index(key) and the weight being 1.0
        (no interpolation if getting a non scalar subset of a dimension).

        /!\ returned key must be insides tuples to be able to concatenate keys
            cleanly.
        """
        if isinstance(key, slice):
            output = [{'key':(self.to_index(key),), 'weight':1.0}]
            return [{'key':(self.to_index(key),), 'weight':1.0}]
        elif isinstance(key, (int, float)):
            lowIndex  = int(self.toIndex(key))
            highIndex = lowIndex + 1
            try:
                lowUnit   = self.to_unit(lowIndex)
                highUnit  = self.to_unit(highIndex)
                lmbd = (key - lowUnit) / (highUnit - lowUnit)
                return [{'key':(lowIndex,),  'weight': 1.0-lmbd},
                        {'key':(highIndex,), 'weight':     lmbd}]
            except:
                return [{'key':(lowIndex,),  'weight': 1.0}]
        else:
            raise ValueError("key must be a slice or a numeric type.")
    

    def bounds(self):

        maxSlice = self.to_unit(slice(None,None,None))
        return Bounds(maxSlice.start, maxSlice.stop)


    def span(self):

        bounds = self.bounds()
        return bounds[-1] - bounds[0]


class AffineDimension(UnitsIndexConverter):

    """
    AffineDimension : maps input 1D indexes to output 1D scale through
                      affine transformation.
    """

    def __init__(self, dimSpan, dimSize):
        super().__init__(dimSize)

        self.toUnit  = AffineTransform((dimSpan[-1] - dimSpan[0]) / (self.dimSize - 1), dimSpan[0])
        self.toIndex = AffineTransform((self.dimSize - 1) / (dimSpan[-1] - dimSpan[0]),
                                       -dimSpan[0]*(self.dimSize - 1) / (dimSpan[-1] - dimSpan[0]))

    
    def subdimension(self, key):
        """Build a new AffineDimension which is a subset of self
            
            Return None if key is not a slice.
            Returns a new AffineDimension if key is a slice.
        """
        
        index = self.to_index(key)
        if isinstance(index, int):
            return None

        # here index is a slice
        if index.stop - index.start <= 1:
            # Here key represent a single element
            return None
        units = self.to_unit(index) # recompute units for clean borders
        return AffineDimension([units.start, units.stop], index.stop - index.start)

class LookupTableDimension(UnitsIndexConverter):

    """
    LookupTableDimension : maps input 1D indexes to output 1D scale through an array
                           defining a stricly monotonous function.
    """

    def __init__(self, inputToOutput):
        super().__init__(len(inputToOutput))

        x_in = np.linspace(0, self.dimSize-1, self.dimSize)

        self.toUnit  = interp1d(x_in, np.array(inputToOutput))
        self.toIndex = interp1d(np.array(inputToOutput), x_in)


    def subdimension(self, key):
        """Build a new LookupTableDimension which is a subset of self
            
            Return None if key is not a slice. Returns a new AffineDimension instead.
        """
        
        index = self.to_index(key)
        if isinstance(index, int):
            return None
        # here index is a slice
        if index.stop - index.start <= 1:
            # Here key reresent a single element
            return None
        return LookupTableDimension(self.toUnit.y[index])


class DimensionHelper:

    """DimensionHelper
    Helper class to convert a tuple of indexes or units to
    their units or indexes counterpart. To be used in ScaledArray
    """

    def __init__(self):
       self.dims = []


    def add_dimension(self, params, typ='linear', dimLen=None):

        if typ == 'linear':
            if dimLen is None:
                dimLen = len(params)
            self.dims.append(AffineDimension([params[0], params[-1]], dimLen))
        elif typ == 'LUT':
            self.dims.append(LookupTableDimension(params))
        elif typ == 'empty':
            return
        else:
            raise ValueError("Invalid dimension type '" + typ + "'")


    def to_unit(self, keys):
        
        if len(keys) != len(self.dims):
            raise ValueError("Number or keys must be equal to number of " +
                             "Dimension (" + str(len(keys)) + "/" + 
                             str(len(self.dims)) + ")")
        res = []
        for key, dim in zip(keys, self.dims):
            res.append(dim.to_unit(key))
        return tuple(res)


    def to_index(self, keys):
        
        if len(keys) != len(self.dims):
            raise ValueError("Number or keys must be equal to number of " +
                             "Dimension (" + str(len(keys)) + "/" + 
                             str(len(self.dims)) + ")")
        res = []
        for key, dim in zip(keys, self.dims):
            res.append(dim.to_index(key))
        return tuple(res)

    
    def subarray_dimensions(self, keys):

        """Compute the new DimensionHelper object associated to the subarray
        corresponding to the keys.
        """
       
        if len(keys) != len(self.dims):
            raise ValueError("Number of keys must be equal to the number of" +
                             " dimensions. (Got " +  str(len(keys)) + "/"
                             + str(len(self.dims)) + ")")

        newDims = DimensionHelper()
        for key, dim in zip(keys, self.dims):
            newDim = dim.subdimension(key)
            if newDim is not None:
                newDims.dims.append(newDim)
        return newDims


    def linear_interpolation_keys(self, keys):
        
        """ Returns a list of pairs of keys and weights to compute a linear
        interpolation. The interpolation computation should read in the 
        main array using generated keys and compute a weighted sum of the
        resulting subrrays using the associated weights.
        """
        if len(keys) != len(self.dims):
            raise ValueError("Number of keys must be equal to the number of" +
                             " dimensions. (Got " +  str(len(keys)) + "/"
                             + str(len(self.dims)) + ")")
        
        weightedKeys = []
        for key, dim in zip(keys, self.dims):
            weightedKeys.append(dim.linear_interpolation_indexes(key))
        
        while len(weightedKeys) > 1:
            newKeys = []
            for key1 in weightedKeys[-2]:
                for key2 in weightedKeys[-1]:
                    newKeys.append({'key':key1['key'] + key2['key'],
                                    'weight':key1['weight']*key2['weight']})
            weightedKeys.pop(-1)
            weightedKeys[-1] = newKeys

        return weightedKeys[0]


    def bounds(self):
        return [dim.bounds() for dim in self.dims]
        

    def span(self):
        return [dim.span() for dim in self.dims]

