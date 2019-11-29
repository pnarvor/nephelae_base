import numpy as np
from PIL import Image

from nephelae.types import Bounds

class MapComparator:

    """
    MapComparator

    This class is intended to compare the values between two maps. Its main
    goal is to ensure that the outputs of the two maps to be compare are
    effectively comparable regardless of resolution, and underlying encoding.

    The typical use case is to compare a MesoNH map (data from a mesonh
    dataset) and a ValueMap (data estimated with Gaussian Process Regression).
    """

    def __init__(self, map1, map2):

        """
        /!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\
        If you are comparing a MesonhMap and a ValueMap, make sure that map1 if
        the MesonhMap.
        /!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\
        """

        self.map1 = map1
        self.map2 = map2


    def __getitem__(self, keys):

        """
        This is the main function which will be called to compare maps. It
        outputs a dictionary with several fields useful for display and
        evaluation.

        /!\ Only compatible for 2D slices for now
        """
        # Getting a reference map slice
        self.slice1 = self.map1.__getitem__(keys)

        # In the case of a MesonhMap, the bounds of the output might slightly
        # differ from the requested ones because the underlying data sampling
        # might not match the requested keys. (keys value between voxels of the
        # MesonhMap). Slice1 contains the bounds closest to requested keys that
        # match the MesoNH sampling.
        # /!\ The bounds given match the position of the center of border
        # voxels. More on that below
        self.bounds = self.slice1.bounds

        # Here new keys are calculated to request data from self.map2. For the
        # data to be comparable, slice2 must be resampled to match the
        # resolution of slice1. However, given how the data are interpolated,
        # and how low is the resolution, the size of the voxels are not
        # negligible and the outer limits of the slices must be carefully
        # aligned : self.map1 and self.map2 scales are related to the center of
        # the voxels. So slice2 must be requested in a way that slice1 and
        # slice2 outer border fall on the same position.

        self.newKeys = []
        i = 0
        for key in keys:
            if isinstance(key, slice):
                self.newKeys.append(
                    slice(self.bounds[i].min, self.bounds[i].max))
                i = i + 1
            else:
                self.newKeys.append(key)

        self.externalBounds = []
        i = 0
        for key, res1 in zip(keys,self.map1.resolution()):
            if isinstance(key, slice):
                self.externalBounds.append(
                    Bounds(self.bounds[i].min - res1 / 2.0,
                           self.bounds[i].max + res1 / 2.0))
                i = i + 1

        self.slice2 = self.map2.__getitem__(self.newKeys)

        # This is the part that does not allow anything else than 2D slices
        self.data2resampled = np.array(
            Image.fromarray(self.slice2.data.T).resize(
            self.slice1.shape, Image.BICUBIC)).T

        return self.slice1.data, self.slice2.data, self.data2resampled

    
    def extent(self):
        res = []
        for bounds in self.externalBounds:
            res.append(bounds.min)
            res.append(bounds.max)
        return res

