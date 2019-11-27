import numpy as np

from nephelae.array import ScaledArray

def compute_com(scaledArr):
    """
    Computes the C.O.M. (center of mass) of a scaled array.

    Parameters
    ---------
    scaledArr : ScaledArray
        Used to compute the C.O.M. Contains data, positions of the data and
        translations function from array indices to map postions.

    Returns
    ---------
    Tuple (1xN)
        Returns the C.O.M. in the coordinates of the map
    """
    res = None
    data = scaledArr.data.ravel()
    indices = np.indices(scaledArr.data.shape)
    locations = np.array([x.ravel() for x in indices])
    x = np.sum(data)
    if x != 0:
        center_of_mass = np.sum(data*locations, axis=1)/x
        res = scaledArr.dimHelper.to_unit(center_of_mass)
    return res
