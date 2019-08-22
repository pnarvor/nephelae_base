import numpy as np

class ScaledArray:

    """ScaledArray

    Helper class for accessing an array of which indexes are bound to
    a continous scale (for example a array a samples in space on which
    dimensions are in meters)

    Attributes:
    
    data                      (numpy-like array): Regular numpy-like array which holds the data
    dimHelper (mesonh_interface.DimensionHelper): Helper type which transform floating points
                                                  keys into index keys to read into the data.

    """

    def __init__(self, data, dimHelper, interpolation='nearest'):

        if interpolation not in ['nearest', 'linear']:
            raise ValueError("interpolation parameter should be either " +
                             "'nearest' or 'linear'")
        self.data      = data
        self.dimHelper = dimHelper
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
            return float(newData) # newData contains a singleValue
        else:
            return ScaledArray(newData, newDims)


