#! /usr/bin/python3

import sys
sys.path.append('../../')
import numpy as np

from nephelae_base.types import Bounds

a0 = np.array([[1,2,3],[4,5,6],[7,8,9]])
b0 = Bounds.from_array(a0)

print(b0)
