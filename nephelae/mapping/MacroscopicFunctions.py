import numpy as np

from nephelae.array import ScaledArray
from scipy import ndimage

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

def get_number_of_elements(scaledArr):
    """
    Computes the number of elements displayed on a image, using a threshold.

    Parameters
    ---------
    scaledArr : ScaledArray
        Contains the data of interest
    
    Returns
    ---------
    NdArray, Number :
        Returns the number of elements displayed on the image and the numpy
        array labeled associated to the data.
    """
    return ndimage.measurements.label(scaledArr.data)

def compute_list_of_coms(scaledArr):
    """
    Computes all the centers of elements displayed on a map. Returns None if
    there is no element.

    Parameters
    ---------
    scaledArr : ScaledArray
        Contains the data of interest
    
    Returns
    ---------
    List of tuple
        Returns all tuples of coordinates of all the elements displayed on the
        map
    """
    data_labeled, number_of_elements = get_number_of_elements(scaledArr)
    list_of_coms = []
    for i in range(1, number_of_elements+1):
        out = np.where(data_labeled == i)
        locations = np.array([X for X in out])
        indices = tuple(np.array(locations[i]) for i in
                range(locations.shape[0]))
        data = scaledArr.data[indices].ravel()
        center_of_mass = np.sum(locations*data, axis=1)/np.sum(data)
        res = scaledArr.dimHelper.to_unit(center_of_mass)
        list_of_coms.append(res)
    return list_of_coms

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

def compute_bounding_box(scaledArr_data, threshold=1e-5):
    """
    Computes the indices where values are superior to the threshold.
    Parameters
    --------
    scaledArr_data : ScaledArray
        Contains the data of interest
    threshold: number
        Gives the number where the values are nullified (0) or not (1)

    Returns
    ---------
    List
        The list of tuples of all indices containing a value superior to the
        threshold. The length of the list is equal to the value returned by
        compute_cloud_volume.
    """
    res = np.where(scaledArr_data.data > threshold)
    locations = np.array([X for X in res])
    indices = tuple(np.array(locations[i]) for i in
            range(locations.shape[0]))
    return [Bounds.from_array(x) from x in indices]

def compute_cloud_volume(scaledArr_data, threshold=1e-5):
    """
    Computes the number of pixels defining the cloud. The volume is
    determined via the MAP values.

    Parameters
    ---------
    scaledArr_data : ScaledArray
        Contains the data of interest
    threshold: number
        Gives the number where the values are nullified (0) or not (1)
    
    Returns
    ---------
    Number
        The number of points defining the area/volume of the cloud
    """
    res = scaledArr_data.data
    threshold_array(res, threshold)
    return np.sum(res)
