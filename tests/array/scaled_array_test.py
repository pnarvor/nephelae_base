#! /usr/bin/python3

import sys
sys.path.append('../../')
import numpy as np
import matplotlib.pyplot as plt

try:
    from netCDF4 import MFDataset
except ImportError as e:
    print("netCDF4 package is probably not installed on this system.")
    print("The netCDF4 is mandadatory to run this test but not for using the nephelae package.")
    print("(To be fixed in the future.)")
    print("Exception output : \"" + str(e) + "\"")
    
from nephelae.array import DimensionHelper
from nephelae.array import ScaledArray

atm = MFDataset('/home/pnarvor/work/nephelae/data/MesoNH-2019-02/REFHR.1.ARMCu.4D.nc')
# atm = MFDataset('/home/pnarvor/work/nephelae/data/skyscanner-remote/mesoNH/ARM_OneHour3600files_No_Horizontal_Wind/*.nc')


time = atm.variables['time'][:]
time = time - time[0]
x    = 1000.0*atm.variables['W_E_direction'][:]
y    = 1000.0*atm.variables['S_N_direction'][:]
z    = 1000.0*np.squeeze(atm.variables['VLEV'][:,0,0])

dimHelper = DimensionHelper()
dimHelper.add_dimension(time, 'LUT')
dimHelper.add_dimension(z, 'LUT')
dimHelper.add_dimension(x, 'linear')
dimHelper.add_dimension(y, 'linear')

# scaledArray = ScaledArray(atm.variables['RCT'], dimHelper)
scaledArray = ScaledArray(atm.variables['RCT'], dimHelper, interpolation='linear')
print("bounds :", scaledArray.bounds)
print("span   :", scaledArray.span)
array0 = scaledArray[0.0, 1000.0, :, :]
array2 = array0[:3000.0, :3000.0]
array3 = array2[1500.0:, 1500.0:]

array1 = scaledArray[2.5, 1000.0, :, :]
array4 = scaledArray[5.0, 1000.0, :, :]

# fig, axes = plt.subplots(4,1,sharex=True)
# axes[0].plot(time, label='time')
# axes[0].grid()
# axes[0].legend(loc='lower right')
# axes[1].plot(x, label='x')
# axes[1].grid()
# axes[1].legend(loc='lower right')
# axes[2].plot(y, label='y')
# axes[2].grid()
# axes[2].legend(loc='lower right')
# axes[3].plot(z, label='z')
# axes[3].grid()
# axes[3].legend(loc='lower right')
# plt.show(block=False)

fig, axes = plt.subplots(1,3)
axes[0].imshow(array1.data, origin='lower')
axes[1].imshow(array2.data, origin='lower')
axes[2].imshow(array3.data, origin='lower')

fig, axes = plt.subplots(1,3, sharex=True, sharey=True)
axes[0].imshow(array0.data, origin='lower')
axes[1].imshow(array1.data, origin='lower')
axes[2].imshow(array4.data, origin='lower')

plt.show(block=False)




