#! /usr/bin/python3

# This is a simple example on how to read data directly from a MesoNH dataset.

import numpy as np

from nephelae_mesonh import MesonhDataset, MesonhVariable
from nephelae_utils.analysis import display_scaled_array

# Change this path to fir your system
mesonhPath = '/home/pnarvor/work/nephelae/data/MesoNH-2019-02/REFHR.1.ARMCu.4D.nc'

# This is the main object managing a MesoNH file. It will open a MesoNH file
# and makes its data available for MesoNH variables You can give one file path
# or a list of file path. The opening of a MesoNH dataset can take some time.
# Note : the python package used to read the MesoNH file prints a few lines
# when opening a file. This is expected (but probably to be fixed at one
# point...)
dataset = MesonhDataset(mesonhPath)

# Once the dataset is open you can create the MesonhVariable accessors. These
# objects will read data into the MesonhDataset to make them available to you.
rct = MesonhVariable(dataset, 'RCT', interpolation='linear')
wt  = MesonhVariable(dataset, 'WT',  interpolation='linear')

# Now reading a RCT sample in the mesonh is done by using indexes with units,
# instead of plain integer indexes. The MesonhVariable type actually parse the
# dimension informations from the MesoNH dataset and allows you to read inside
# it by directly using seconds and meters.

# /!\/!\ To allow compatibility with the rest of the project the dimensions
# /!\/!\ order was changed from (t,z,y,x) to (t,x,y,z)

# Example : reading the rct value at t = 60.0s, x=500.0m, y=700.0, z=1100.0m
value = rct[60.0,500.0,700.0,1100.0]
print("RCT value :", value)

# You can also fetch some slices. The next line will read a horizontal plane of
# wt data, at time t=60, at altitude z=1100.0, and between xmin=400.0,
# xmax=500.0, ymin=600.0, ymax=800.0
windArray = wt[60,400.0:500.0, 600.0:800.0, 1100.0]

# You can access the bounds (upper and lower limit of each dimension) of the
# variable this way:
bounds = wt.bounds
print(bounds)

# To access the bounds of a single dimension
tminmax = wt.bounds[0]
print("Time bounds :", tminmax.min, tminmax.max)
xminmax = wt.bounds[1]
print("x    bounds :", xminmax.min, xminmax.max)
yminmax = wt.bounds[2]
print("y    bounds :", yminmax.min, yminmax.max)
zminmax = wt.bounds[3]
print("z    bounds :", zminmax.min, zminmax.max)

# You can access the array size (number of samples in each dimension) this way:
print("Shape : ", wt.shape)

# Note : MesoNH datasets are assumed to be periodic in the (x,y) plane. So even
# if a bound is defined for x and y, you can read data further than the "bound"
# of the dimension. For example this will work:
xbounds = wt.bounds[1]
windArray = wt[60, 0:2*xbounds.max, 600:800.0, 1100]

# Once you read data from the MesonhVariable you get an array of data (or a
# single sample). The type of this array is nephelae.array.ScaledArray
windArray = wt[60,400.0:500.0, 600.0:800.0, 1100.0] # windArray is a scaledArray

# ScaledArrays are accessed in the same manner as MesonhVariables, but are not
# periodic. The bounds on the scaled arrays reflect the keys you used to fetch
# data in the first place, but might vary a little depending on the underlying
# data.
print("windArray bounds :", windArray.bounds)

# In the ScaledArray, data are stored as regular numpy.array. To access it:
numpyArray = windArray.data
# The type of numpy array is numpy.array

# You can display 2D ScaledArrays using the display_scaled_array function. Take
# a look at its implementation to learn more about scaled arrays
display_scaled_array(windArray)

# You can fetch a full size slice of data this way
fullWind = wt[60.0, :,:, 1100]
display_scaled_array(fullWind)
















