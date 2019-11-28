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
        Returns the C.O.M. in the coordinates of the map.
        /!\ Returns None if the sum of the scaledArr.data is 0 /!\
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

def threshold_array(arr, threshold=1e-5):
    """
    Thresholds an array, returning a binary array

    Parameters
    ---------
    arr : NumpyArray
        Contains the data to threshold
    Returns
    ---------
    NumpyArray
        Returns arr with binary values, depending of the threshold
    """
    arr[arr < threshold] = 0.0
    arr[arr >= threshold] = 1.0
    return arr

def compute_cross_section_border(scaledArr_data, scaledArr_std, factor=1,
        threshold=1e-5):
    """
    Computes the border of the scaledArr, using a threshold, and returns inner
    and outer borders, using std values with a certain confidence (given by the
    factor parameter)

    Parameters
    ---------
    scaledArr_data : ScaledArray
        Contains the data of interest
    scaledArr_std : ScaledArray
        Contains std associated with the data
    factor : number
        Gives the confidence of the std. See Gaussian properties with the std.
    threshold : number
        Gives the number where values are nullified (0) or not (1)

    Returns
    --------
    NumpyArray, NumpyArray
        Returns inner and outer borders of the data.
    """
    inner_border, outer_border = (scaledArr_data.data - factor *
            scaledArr_std.data, scaledArr_data.data + factor *
            scaledArr_std.data)
    threshold_array(inner_border, threshold)
    threshold_array(outer_border, threshold)
    return inner_border, outer_border
