#! /usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import time
from PIL import Image

from nephelae.types    import Bounds
from nephelae.mapping  import GprPredictor, ValueMap, StdMap, WindKernel, WindMapConstant
from nephelae.database import NephelaeDataServer
from nephelae_mesonh   import MesonhDataset, MesonhMap

from nephelae.mapping  import MapComparator

mesonhPath = '/home/pnarvor/work/nephelae/data/MesoNH-2019-02/REFHR.1.ARMCu.4D.nc'
dataset = MesonhDataset(mesonhPath)

lwcMesonh = MesonhMap("RCT Map", dataset, 'RCT')

# Kernel
wind = np.array([8.5, 0.9])
processVariance    = 1.0e-8
noiseStddev = 0.1 * np.sqrt(processVariance)
lengthScales = [70.0, 80.0, 80.0, 60.0]
kernel0 = WindKernel(lengthScales, processVariance, noiseStddev**2, WindMapConstant('Wind',wind))

dtfile = 'database/database_virtual.neph'
dtbase = NephelaeDataServer.load(dtfile)

gpr = GprPredictor(dtbase, ['RCT'], kernel0)
map_gpr = ValueMap('RCT_gpr', gpr)
std_gpr = StdMap('RCT_gpr', gpr)

t0 = 300.0
x0 = 12.5
x1 = 6387.5
y0 = 1837.5
y1 = 2712.5
z0 = 1100.0

comp = MapComparator(lwcMesonh, map_gpr)
mesonhSlice, gprSlice, gprSliceResampled = comp[t0, x0:x1, y0:y1, z0]

mask = np.zeros(mesonhSlice.shape)
mask[gprSliceResampled > 1.0e-10] = 1.0
mesonhSlice = mesonhSlice * mask
gprSliceResampled = gprSliceResampled * mask

eqm       = np.sum(((mesonhSlice.T - gprSliceResampled.T)**2)[:]) / np.sum(mask[:])
mesonhVar = np.sum((mesonhSlice**2)[:]) / np.sum(mask[:])
eqmr = eqm / mesonhVar

fig, axes = plt.subplots(4,1, sharex=True, sharey=True)
axes[0].imshow(mesonhSlice.T, origin='lower', extent=comp.extent())
axes[1].imshow(gprSlice.T, origin='lower', extent=comp.extent())
axes[2].imshow(gprSliceResampled.T, origin='lower', extent=comp.extent())
axes[3].imshow(mesonhSlice.T - gprSliceResampled.T, origin='lower', extent=comp.extent())

plt.show(block=False)



