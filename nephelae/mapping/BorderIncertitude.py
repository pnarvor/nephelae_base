from scipy import ndimage
import numpy as np

from nephelae.array import ScaledArray

from .FactoryBorder import FactoryBorder
from .MacroscopicFunctions import compute_cross_section_border

class BorderIncertitude(FactoryBorder):
    def __init__(self, name, valueMap, stdMap):
        super().__init__(name)
        self.valueMap = valueMap
        self.stdMap = stdMap

    def compute_borders(self, arrays):
        inner, outer = compute_cross_section_border(arrays[0],
                arrays[1], factor=1, threshold=2e-4)
        inner, outer = (inner.astype(np.int32), outer.astype(np.int32))
        eroded_inner = ndimage.binary_erosion(inner).astype(inner.dtype)
        eroded_outer = ndimage.binary_erosion(outer).astype(outer.dtype)
        border_inner = np.bitwise_xor(inner, eroded_inner)
        border_outer = np.bitwise_xor(outer, eroded_outer)
        inner_scarray = ScaledArray(border_inner, arrays[0].dimHelper,
                arrays[0].interpolation)
        outer_scarray = ScaledArray(border_outer, arrays[0].dimHelper,
                arrays[0].interpolation)
        return (inner_scarray, outer_scarray)

    def get_arrays(self, keys):
        return (self.valueMap.__getitem__(keys), self.stdMap.__getitem__(keys))
