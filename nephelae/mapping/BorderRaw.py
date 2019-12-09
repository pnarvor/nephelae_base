from scipy import ndimage
import numpy as np

from nephelae.array import ScaledArray

from .FactoryBorder import FactoryBorder
from .MacroscopicFunctions import threshold_array

class BorderRaw(FactoryBorder):
    def __init__(self, name, mapInterface):
        super().__init__(name)
        self.mapInterface = mapInterface

    def compute_borders(self, arrays):
        raw_data = arrays.data
        border = threshold_array(raw_data).astype(np.int32)
        eroded = ndimage.binary_erosion(border).astype(border.dtype)
        border_raw = np.bitwise_xor(border, eroded)
        raw_scarray = ScaledArray(border_raw, arrays.dimHelper,
                arrays.interpolation)
        return raw_scarray

    def get_arrays(self, keys):
        return self.mapInterface.__getitem__(keys)
