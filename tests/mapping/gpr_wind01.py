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


from nephelae_mesonh import MesonhVariable, MesonhDataset
from nephelae.types  import Position
from nephelae.types  import Bounds
from nephelae.types  import Gps
from nephelae.types  import SensorSample

from nephelae.mapping  import GprPredictor
from nephelae.mapping  import StdMap
from nephelae.mapping  import ValueMap
from nephelae.mapping  import WindKernel
from nephelae.mapping  import WindMapConstant
from nephelae.database import NephelaeDataServer

from sklearn.gaussian_process import GaussianProcessRegressor

def parameters(rct):

    # Trajectory ####################################
    # a0 = 400.0
    a0 = 250.0
    f0 = - 1 / 120.0
    # f0 = 1 / 150.0
    
    a1 = 0.0
    # f1 = 1.5*f0
    f1 = 2.5*f0
    # f1 = -1.3*f0
    # f1 = -2.5*f0
    # f1 = -4.5*f0
    v0 = np.array([8.5, 0.9])
    
    tStart = 50.0
    tEnd   = 700.0
    t = np.linspace(tStart, tEnd, int(tEnd - tStart))
    # p0 = Position(240.0, 1700.0, 2000.0, 1100.0)
    # p0 = Position(50.0, 0.0, 2000.0, 1100.0)
    p0 = Position(50.0, 100.0, 1950.0, 1100.0)
    p  = np.array([[p0.t, p0.x, p0.y, p0.z]]*len(t))
    
    p[:,0] = t
    p[:,1] = p[:,1] + a0*(a1 + np.cos(2*np.pi*f1*(t-t[0])))*np.cos(2*np.pi*f0*(t-t[0]))
    p[:,2] = p[:,2] + a0*(a1 + np.cos(2*np.pi*f1*(t-t[0])))*np.sin(2*np.pi*f0*(t-t[0]))
    print("Max velocity relative to wind :",
        max(np.sqrt(np.sum((p[1:,1:3] - p[:-1,1:3])**2, axis=1)) / (p[1:,0] - p[:-1,0])))
    print("Min velocity relative to wind :",
        min(np.sqrt(np.sum((p[1:,1:3] - p[:-1,1:3])**2, axis=1)) / (p[1:,0] - p[:-1,0])))
    p[:,1:3] = p[:,1:3] + (t - tStart).reshape([len(t), 1]) @ v0.reshape([1,2]) 
    
    # prediction ####################################
    b = rct.bounds
    # yBounds = [min(p[:,2]), max(p[:,2])]
    # b[2].min = yBounds[0]
    # b[2].max = yBounds[1]
    # tmp = rct[p0.t,p0.z,yBounds[0]:yBounds[1],:]
    b[2].min = min(p[:,2])
    b[2].max = max(p[:,2])
    tmp = rct[p0.t,:,b[2].min:b[2].max,p0.z]
    b[1].min = tmp.bounds[0][0]
    b[1].max = tmp.bounds[0][-1]
    b[2].min = tmp.bounds[1][0]
    b[2].max = tmp.bounds[1][-1]
    print("Bounds : ", b)
    X0,Y0 = np.meshgrid(
        np.linspace(tmp.bounds[0][0], tmp.bounds[0][-1], tmp.shape[0]),
        np.linspace(tmp.bounds[1][0], tmp.bounds[1][-1], tmp.shape[1]),
        indexing='xy', copy=False)
    # xyLocations = np.array([[0]*X0.shape[0]*X0.shape[1], X0.ravel(), Y0.ravel()]).T
    print(X0.ravel())
    xyLocations = np.array([[0]*X0.shape[0]*X0.shape[1],
                           X0.ravel(), Y0.ravel(),
                           [p0.z]*X0.shape[0]*X0.shape[1]]).T

    return t,p0,p,b,xyLocations,v0,tmp.shape,tStart,tEnd

#########################################################################

mesonhPath = '/local/fseguin/nephelae_data/REFHR.1.ARMCu.4D.nc'
dataset = MesonhDataset(mesonhPath)

rct = MesonhVariable(dataset, 'RCT')
ut  = MesonhVariable(dataset, 'UT')
vt  = MesonhVariable(dataset, 'VT')

t,p0,p,b,xyLocations,v0,mapShape,tStart,tEnd = parameters(rct)

# Kernel
processVariance    = 1.0e-8
noiseStddev = 0.1 * np.sqrt(processVariance)
# kernel0 = WindKernel(lengthScales, processVariance, noiseStddev**2, v0)
# lengthScales = [70.0, 60.0, 60.0, 60.0]
lengthScales = [70.0, 80.0, 80.0, 60.0]
kernel0 = WindKernel(lengthScales, processVariance, noiseStddev**2, WindMapConstant('Wind',v0))

noise = noiseStddev*np.random.randn(p.shape[0])
dtfile = 'output/wind_data04.neph'
print("Getting mesonh values... ", end='', flush=True)
dtbase = NephelaeDataServer()
# for pos,n in zip(p,noise):
#    dtbase.add_gps(Gps("100", Position(pos[0],pos[1],pos[2],pos[3])))
#    dtbase.add_sample(SensorSample('RCT', '100', pos[0],
#        Position(pos[0],pos[1],pos[2],pos[3]),
#        [rct[pos[0],pos[1],pos[2],pos[3] + n]]))
#    dtbase.add_sample(SensorSample('Wind', '100', pos[0],
#        Position(pos[0],pos[1],pos[2],pos[3]),
#        [ut[pos[0],pos[1],pos[2],pos[3]], vt[pos[0],pos[1],pos[2],pos[3]]]))
# dtbase.save(dtfile, force=True)
dtbase = NephelaeDataServer.load(dtfile)
print("Done !", flush=True)


gpr = GprPredictor(dtbase, ['RCT'], kernel0)
map_gpr = ValueMap('RCT_val', gpr)
std_gpr = StdMap('RCT_val', gpr)

profiling = False
# profiling = True
if not profiling:
    fig, axes = plt.subplots(3,1,sharex=True,sharey=True)
simTime = p0.t
lastTime = time.time()
simSpeed = 50.0

# interp='nearest'
interp='bicubic'
def do_update(t):

    print("Sim time :", t)
    # prediction

    # print(gprMap.range())
    map0 = map_gpr[t,b[1].min:b[1].max,b[2].min:b[2].max,p0.z]
    std0 = std_gpr[t,b[1].min:b[1].max,b[2].min:b[2].max,p0.z]
    # uncomment this to remove negative values  
    map0.data[map0.data < 0.0] = 0.0
   
    # display
    if not profiling:
        global axes
        axes[0].cla()
        axes[0].imshow(rct[t,b[1].min:b[1].max,b[2].min:b[2].max,p0.z].data.T, origin='lower',
                      interpolation=interp,
                      extent=[b[1].min, b[1].max, b[2].min, b[2].max])
        axes[0].grid()
        axes[0].set_title("Ground truth")

        try:
           axes[0].plot(p[:int(t-tStart + 0.5),1], p[:int(t-tStart + 0.5),2], '.')
        finally:
           pass

        axes[1].cla()
        axes[1].imshow(map0.data.T, origin='lower', interpolation=interp,
                      extent=[b[1].min, b[1].max, b[2].min, b[2].max])
        axes[1].grid()
        axes[1].set_title("MAP")

        axes[2].cla()
        axes[2].imshow(std0.data.T**2, origin='lower', interpolation=interp,
                      extent=[b[1].min, b[1].max, b[2].min, b[2].max])
        axes[2].grid()
        axes[2].set_title("Variance AP")
def init():
    pass
def update(i):

    global simTime
    if profiling:
        simTime = simTime + 1.0
    else:
        simTime = simTime + 3.0

    do_update(simTime)

if not profiling:
    anim = animation.FuncAnimation(
        fig,
        update,
        init_func=init,
        interval = 1)
    
    plt.show(block=False)
else:
    t0 = time.time()
    while simTime < 600:
        update(0)
    print("Ellapsed :", time.time() - t0, "s")

