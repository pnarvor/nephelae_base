#! /usr/bin/python3

# changing process priority (linux only)
import os
# os.nice(-19) # probably a bit harsh (requires sudo)

import sys
sys.path.append('../../')
import numpy as np
import numpy.fft as npfft
import matplotlib.pyplot as plt
from   matplotlib import animation
import time
from PIL import Image

from nephelae_mesonh import MesonhDataset, MesonhMap
from nephelae.types  import Bounds

from nephelae.mapping  import GprPredictor
from nephelae.mapping  import StdMap
from nephelae.mapping  import ValueMap
from nephelae.mapping  import WindKernel
from nephelae.mapping  import WindMapConstant
from nephelae.database import NephelaeDataServer

# from nephelae.mapping  import compute_com

# mesonhPath = '/local/fseguin/nephelae_data/REFHR.1.ARMCu.4D.nc'
mesonhPath = '/home/pnarvor/work/nephelae/data/MesoNH-2019-02/REFHR.1.ARMCu.4D.nc'
dataset = MesonhDataset(mesonhPath)

rct = MesonhMap("RCT Map", dataset, 'RCT')
# ut  = MesonhMap("UT Map",  dataset, 'UT')
# vt  = MesonhMap("VT Map",  dataset, 'VT')

# Kernel
v0 = np.array([8.5, 0.9])
processVariance    = 1.0e-8
noiseStddev = 0.1 * np.sqrt(processVariance)
# kernel0 = WindKernel(lengthScales, processVariance, noiseStddev**2, v0)
# lengthScales = [70.0, 60.0, 60.0, 60.0]
lengthScales = [70.0, 80.0, 80.0, 60.0]
kernel0 = WindKernel(lengthScales, processVariance, noiseStddev**2, WindMapConstant('Wind',v0))

dtfile = 'output/wind_data04.neph'
dtbase = NephelaeDataServer.load(dtfile)

gpr = GprPredictor(dtbase, ['RCT'], kernel0)
map_gpr = ValueMap('RCT_gpr', gpr)
std_gpr = StdMap('RCT_gpr', gpr)

t0 = 200.0
z0 = 1100.0
b = [Bounds(0.0, 715), Bounds(12.5, 6387.5), Bounds(1837.5, 2712.5), Bounds(12.5, 3987)]

mesonhSlice = rct[t0, b[1].min:b[1].max, b[2].min:b[2].max, z0]
r2 = map_gpr.resolution()[1] / 2.0
gprSlice    = map_gpr[t0, b[1].min+r2:b[1].max-r2, b[2].min+r2:b[2].max-r2, z0]

# gprCenter0 = compute_com(gprSlice)
# gprSlice.data[gprSlice.data < 0] = 0.0
# gprCenter1 = compute_com(gprSlice)

gprSliceResampled = np.array(Image.fromarray(gprSlice.data.T).resize(mesonhSlice.shape, Image.BICUBIC)).T

mask = np.zeros(mesonhSlice.data.shape)
mask[gprSliceResampled > 1.0e-10] = 1.0
mesonhSlice.data = mesonhSlice.data * mask
gprSliceResampled = gprSliceResampled * mask


eqm       = np.sum(((mesonhSlice.data.T - gprSliceResampled.T)**2)[:]) / np.sum(mask[:])
mesonhVar = np.sum((mesonhSlice.data**2)[:]) / np.sum(mask[:])
eqmr = eqm / mesonhVar


fig, axes = plt.subplots(4,1, sharex=True, sharey=True)
b = mesonhSlice.bounds
print(b)

axes[0].imshow(mesonhSlice.data.T, origin='lower', extent=[b[0].min, b[0].max, b[1].min, b[1].max])
axes[1].imshow(gprSlice.data.T, origin='lower', extent=[b[0].min, b[0].max, b[1].min, b[1].max])

# axes[1].plot(gprCenter0[0], gprCenter0[1], '.r')
# axes[1].plot(gprCenter1[0], gprCenter1[1], '.b')

axes[2].imshow(gprSliceResampled.T, origin='lower', extent=[b[0].min, b[0].max, b[1].min, b[1].max])
axes[3].imshow((mesonhSlice.data.T - gprSliceResampled.T)**2 / np.max(mesonhSlice.data.ravel())**2, origin='lower', extent=[b[0].min, b[0].max, b[1].min, b[1].max])

plt.show(block=False)



