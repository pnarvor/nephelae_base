import numpy as np

from nephelae.array import ScaledArray
from scipy import ndimage

from nephelae.types import Bounds

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

def threshold_array(arr, threshold=2e-4):
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
    return (arr > threshold)

def get_number_of_elements(scaledArr, threshold=2e-4):
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
    arr = (scaledArr.data > threshold) * scaledArr.data
    return ndimage.measurements.label(arr)

def compute_selected_element_com(coords, scaledArr, threshold):
    """
    Computes the center of mass of a selected element, using a tuple of
    coordinates. Return None if there is no center of mass.

    Parameters
    ---------
    coords : Tuple
        Tuple of coordinates

    Returns
    ---------
    Tuple :
        Coordinates of the center of mass. None if there is no element
        associated with the map.
    """
    res = None
    data_labeled, number_of_elements = get_number_of_elements(scaledArr,
            threshold)
    if is_in_element(coords, data_labeled):
        out = np.where(data_labeled == data_labeled[coords])
        locations = np.array([X for X in out])
        indices = tuple(np.array(locations[i]) for i in
                range(locations.shape[0]))
        data = scaledArr.data[indices].ravel()
        center_of_mass = np.sum(locations*data, axis=1)/np.sum(data)
        res = scaledArr.dimHelper.to_unit(center_of_mass)
    return res

def compute_selected_element_volume(coords, scaledArr, threshold=2e-4):
    """
    Computes the number of pixels defining the cloud, depending of the
    coordinates.

    Parameters
    ---------
    coords : Tuple
        Tuple of coordinates
    
    scaledArr : ScaledArray
        Contains the data of interest

    Returns
    ---------
    Number :
        The number of pixels of the cloud displayed. Returns None if there is no
        element associated with the coordinates.
    """
    res = None
    data_labeled, number_of_elements = get_number_of_elements(scaledArr,
            threshold)
    if is_in_element(coords, data_labeled):
        out = np.where(data_labeled == data_labeled[coords])
        res = len(out[0])
    return res

def compute_list_of_coms(scaledArr, threshold):
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
    data_labeled, number_of_elements = get_number_of_elements(scaledArr,
            threshold)
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
        threshold=2e-4):
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
    return inner_border, outer_border

def compute_bounding_box(scaledArr, threshold):
    """
    Computes the bounds where an element is spotted. Returns the list of bounds
    of all elements.
    
    Parameters
    --------
    scaledArr_data : ScaledArray
        Contains the data of interest

    Returns
    ---------
    List
        The list of bounds of elements in the ScaledArray.
        The length of the list is equal to number_of_elements.
    """
    data_labeled, number_of_elements = get_number_of_elements(scaledArr,
            threshold)
    list_of_boxes = []
    for i in range(1, number_of_elements+1):
        out = np.where(data_labeled == i)
        locations = np.array([X for X in out])
        mins = scaledArr.dimHelper.to_unit(np.amin(locations, axis=1).tolist())
        maxs = scaledArr.dimHelper.to_unit(np.amax(locations, axis=1).tolist())
        list_of_boxes.append([Bounds(mins[i], maxs[i]) for i in
            range(len(mins))])
    return list_of_boxes
    

def is_in_element(coords, data_labeled):
    """
    Evaluate if the given coords are in a element.

    Parameters
    ---------
    coords: Tuple
        Contains the indices to check
    data_labeled : NdArray
        Data with elements labeled

    Returns
    ---------
    Boolean
        True if coords point to an element of the data, False otherwise.
    """
    return data_labeled[coords] != 0

def compute_cloud_volume(scaledArr_data, threshold=1e-5):
    """
    Computes the number of pixels defining the cloud. The volume is
    determined via the MAP values.

    Parameters
    ---------
    scaledArr_data : ScaledArray
        Contains the data of interest
    threshold : number
        Gives the number where the values are nullified (0) or not (1)
    
    Returns
    ---------
    Number
        The number of points defining the area/volume of the cloud
    """
    arr = threshold_array(scaledArr_data.data, threshold)
    return np.sum(arr)
