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
    data = scaledArr.data
    indices = np.indices(data.shape)
    locations = np.array([x.ravel() for x in indices])
    return np.sum(data+locations)/np.sum(data)
