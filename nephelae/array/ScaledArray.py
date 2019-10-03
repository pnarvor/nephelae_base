import numpy as np

class ScaledArray:

    """
    ScaledArray
    
    Helper class wrapping an array to be able to access data using
    real numbers (float) instead of integer indexes.

    This class wraps a data array (a numpy.array-like object) and overrides its
    __getitem__ method (the [] operator) to accept floating point values.
    These floating point values are mapped onto the corresponding integer
    indexes to retrieve data from the wrapped array.

    Example:

    array1 is a 3D array containing data from a region of space.
    This region is a cube of 10.0 x 20.0 x 30.0 meters. The resolution
    is 10 samples/m on each dimension so the data size is 100 x 200 x 300
    elements.
    Then with array2 = ScaledArray(array1, ...), the sample value at:
                        x=1.4m, y=3.1m, z=4.2
    is obtained as following:
                        value = array2[1.4,3.1,4.2].
    which is equivalent to:
                        value = array1[14,31,42]
    One 

    The ScaledArray type also handles interpolation (nearest neighbor and linear)
    and non-linear mappings.

    Attributes
    ----------
    
    data : numpy-like array
        Regular numpy-like array holding the data. Must define
        array.__getitem__() and array.span.

    dimHelper : array.DimensionHelper
        Main class performing the mapping between real numbers
        and integer indexes. Dimensions can be either a affine mapping
        (index = a*x + b), or a look up table. See array.DimensionHelper
        for more details.

    interpolation : str
        Interpolation method. Only 'nearest' and 'linear' are supported.
        When getting an interval the method 'nearest' is always used
        regardless of self.interpolation value.

    Methods
    -------

    __getattr__(name): (To be deprecated ?)
        name == 'shape' -> tuple(int):
            Returns self.data.shape
        name == 'bounds' -> tuple(types.Bounds):
            Returns bounds of each dimension of the array.
        name == 'span' -> tuple(float):
            Returns span of each dimension of the array.
            For a single dimension, the span is bound.ax - bound.min.

    __getitem__(keys) -> numpy.array:
        [] operator. Keys are real values.

    """

    def __init__(self, data, dimHelper, interpolation='nearest'):

        """
        Parameters
        ----------
        data : numpy-like array
            Array around which wrap ScaledArray.

        dimHelper : array.DimensionHelper
            Main class performing the mapping between real numbers
            and integer indexes. Dimensions can be either a affine mapping
            (index = a*x + b), or a look up table. See array.DimensionHelper
            for more details.

        interpolation : str
            Interpolation method (either 'nearest' or 'linear').
            When getting an interval the method 'nearest' is always used
            regardless of self.interpolation value.
        """

        if interpolation not in ['nearest', 'linear']:
            raise ValueError("interpolation parameter should be either " +
                             "'nearest' or 'linear'")
        self.data          = data
        self.dimHelper     = dimHelper
        self.interpolation = interpolation


    def __getattr__(self, name):

        if name == 'shape':
            return self.data.shape
        elif name == 'bounds':
            return self.dimHelper.bounds()
        elif name == 'span':
            return self.dimHelper.span()
        else:
            raise ValueError("ScaledArray has no attribute '"+name+"'")


    def __getitem__(self, keys):

        """Returns value(s) at specific location(s).

        __getitem__ is the method called when using the [] operator.
        Calling array[1, 2:4, :5:2, 1:] is equivalent to call
        array.__getitem__((1, slice(2,4,None), slice(None,5,2), slice(1,None,None)))
        the "start:stop:step" syntax is syntactic sugar for "slice(start,stop,step)".

        In this implementation the step argument is not used. 

        Parameters
        ----------

        keys : tuple(float,slice(float),...)
            Real number indexes to be mapped to integer indexes used
            to get data from self.data.
        """

        if self.interpolation == 'nearest':
            newData = np.squeeze(self.data[self.dimHelper.to_index(keys)])
        elif self.interpolation == 'linear':
            interpKeys = self.dimHelper.linear_interpolation_keys(keys)
            newData = interpKeys[0]['weight']*np.squeeze(self.data[interpKeys[0]['key']])
            for interpKey in interpKeys[1:]:
                newData = newData + interpKey['weight']*np.squeeze(self.data[interpKey['key']])
        else:
            raise ValueError("self.interpolation parameter should be either "+
                             "'nearest' or 'linear'")

        newDims = self.dimHelper.subarray_dimensions(keys)
        if not newDims.dims:
            # return float(newData) # newData contains a singleValue
            return newData # check if no problems
        else:
            return ScaledArray(newData, newDims)


