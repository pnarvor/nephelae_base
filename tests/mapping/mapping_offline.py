#! /usr/bin/python3

import os
import sys
sys.path.append('../../')
import numpy as np
import matplotlib.pyplot as plt
import time

from PIL import Image


from nephelae_mesonh import MesonhDataset, MesonhMap
from nephelae.types  import Position
from nephelae.types  import Bounds
from nephelae.types  import Gps
from nephelae.types  import SensorSample

from nephelae.mapping  import GprPredictor
from nephelae.mapping  import WindKernel
from nephelae.mapping  import WindMapConstant
from nephelae.database import NephelaeDataServer

mesonhPath   = '/home/pnarvor/work/nephelae/data/MesoNH-2019-02/REFHR.1.ARMCu.4D.nc'
# databasePath = '/home/pnarvor/work/nephelae/data/temp/dt5_01.neph'
databasePath = 'output/wind_data04.neph'

database = NephelaeDataServer.load(databasePath)

mesonhDataset = MesonhDataset(mesonhPath)
rct = MesonhMap('Liquid water', mesonhDataset, 'RCT', interpolation='linear')

# Have to define wind by hand for now.
wind = np.array([8.5, 0.9])
windMap = WindMapConstant('Wind', wind)

# Kernel for liquid water content
processVariance = 1.0e-8
noiseStddev     = 0.1 * np.sqrt(processVariance)
lengthScales    = [70.0, 80.0, 80.0, 60.0]

rctKernel0 = WindKernel(lengthScales, processVariance, noiseStddev**2, windMap)
rctGpr     = GprPredictor('RCT', database, ['RCT'], rctKernel0)

# coordinates of the map you want to generate/extract 
t = 160.0
x = [12.5, 6387.5]
y = [1837.5, 2712.5]
z = 1100.0

# getting some mesonh data
mesonhSlice = rct[t, x[0]:x[1], y[0]:y[1], z].data
# predicting with gpr
gprSlice    = rctGpr[t, x[0]:x[1], y[0]:y[1], z][0].data[:,:,0]


# the GPR prediction resolution depends on the kernel length scale so it is not
# necessarily the same as the mesonh. Although they represent the same region
# of space, the array sizes might differ. If you want to compare mesonh data
# and gpr data, you want to resize the gpr output.
gprSliceResampled = np.array(Image.fromarray(gprSlice.T).resize(mesonhSlice.shape, Image.BICUBIC)).T

# Calculating the difference between ground truth and prediction
diff = mesonhSlice - gprSliceResampled

fig, axes = plt.subplots(4, 1, sharex=True, sharey=True)
axes[0].imshow(mesonhSlice.T, origin='lower', extent=x+y)
axes[0].grid()
axes[0].set_xlabel("W_E_direction (m)")
axes[0].set_ylabel("S_N_direction (m)")

axes[1].imshow(gprSlice.T, origin='lower', extent=x+y)
axes[1].grid()
axes[1].set_xlabel("W_E_direction (m)")
axes[1].set_ylabel("S_N_direction (m)")

axes[2].imshow(gprSliceResampled.T, origin='lower', extent=x+y)
axes[2].grid()
axes[2].set_xlabel("W_E_direction (m)")
axes[2].set_ylabel("S_N_direction (m)")

axes[3].imshow(diff.T, origin='lower', extent=x+y)
axes[3].grid()
axes[3].set_xlabel("W_E_direction (m)")
axes[3].set_ylabel("S_N_direction (m)")

plt.show(block=False)


# rct = MesonhVariable(dataset, ['RCT','WT'])
# ut  = MesonhVariable(dataset, 'UT')
# vt  = MesonhVariable(dataset, 'VT')
# 
# t,p0,p,b,xyLocations,v0,mapShape,tStart,tEnd = parameters(rct)
# 
# # Kernel
# processVariance    = 1.0e-8
# noiseStddev = 0.1 * np.sqrt(processVariance)
# # kernel0 = WindKernel(lengthScales, processVariance, noiseStddev**2, v0)
# # lengthScales = [70.0, 60.0, 60.0, 60.0]
# lengthScales = [70.0, 80.0, 80.0, 60.0]
# kernel0 = WindKernel(lengthScales, processVariance, noiseStddev**2, WindMapConstant('Wind',v0))
# 
# noise = noiseStddev*np.random.randn(p.shape[0])
# dtfile = 'output/wind_data04.neph'
# print("Getting mesonh values... ", end='', flush=True)
# dtbase = NephelaeDataServer.load(dtfile)
# print("Done !", flush=True)
# 
# 
# gprMap = GprPredictor('RCT', dtbase, ['RCT'], kernel0)
# 
# 
# profiling = False
# # profiling = True
# if not profiling:
#     fig, axes = plt.subplots(3,1,sharex=True,sharey=True)
# simTime = p0.t
# lastTime = time.time()
# simSpeed = 50.0
# 
# # interp='nearest'
# interp='bicubic'
# def do_update(t):
# 
#     print("Sim time :", t)
#     # prediction
# 
#     # print(gprMap.range())
#     map0, std0 = gprMap[t,b[1].min:b[1].max,b[2].min:b[2].max,p0.z]
# 
#     # uncomment this to remove negative values  
#     # map0.data[map0.data < 0.0] = 0.0
#    
#     # display
#     if not profiling:
#         global axes
#         axes[0].cla()
#         axes[0].imshow(rct[t,b[1].min:b[1].max,b[2].min:b[2].max,p0.z].data[:,:,0].T, origin='lower',
#                        interpolation=interp,
#                        extent=[b[1].min, b[1].max, b[2].min, b[2].max])
#         axes[0].grid()
#         axes[0].set_title("Ground truth")
# 
#         try:
#             axes[0].plot(p[:int(t-tStart + 0.5),1], p[:int(t-tStart + 0.5),2], '.')
#         finally:
#             pass
# 
#         axes[1].cla()
#         axes[1].imshow(map0.data[:,:,0].T, origin='lower', interpolation=interp,
#                        extent=[b[1].min, b[1].max, b[2].min, b[2].max])
#         axes[1].grid()
#         axes[1].set_title("MAP")
# 
#         axes[2].cla()
#         axes[2].imshow(std0.data.T**2, origin='lower', interpolation=interp,
#                        extent=[b[1].min, b[1].max, b[2].min, b[2].max])
#         axes[2].grid()
#         axes[2].set_title("Variance AP")
# 
#     time.sleep(1.0)
# 
# def init():
#     pass
# def update(i):
# 
#     global simTime
#     if profiling:
#         simTime = simTime + 1.0
#     else:
#         simTime = simTime + 3.0
# 
#     do_update(simTime)
# 
# if not profiling:
#     anim = animation.FuncAnimation(
#         fig,
#         update,
#         init_func=init,
#         interval = 1)
#     
#     plt.show(block=False)
# else:
#     t0 = time.time()
#     while simTime < 600:
#         update(0)
#     print("Ellapsed :", time.time() - t0, "s")

