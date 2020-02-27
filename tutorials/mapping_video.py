#! /usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt

from nephelae.database import NephelaeDataServer
from nephelae_utils.analysis import TimedData, setup_map_generator
from nephelae_utils.analysis import aircraft_position_at_time, keys_from_position, display_scaled_array

# This is an example showing how to generate a cloud map from a prevously saved
# database.

# First loading a flight database.
databasePath = '/home/pnarvor/work/nephelae/data/barbados/post_processing/cams_logs/flight_02_08_03/database/database01.neph'
database = NephelaeDataServer.load(databasePath)

# We will work on aircraft 7 in this dataset.
aircraft = '7'
keys = (slice(209,2755),)

# Create a map generator. You can find out how to estimate the hyper-parameters
# such wind and cloud sensor calibration from other tutorials.
wind    = [-8.91, -0.71]
# wind    = [0.0, 0.0]
aircrafts = {
    '7'  : {'alpha' : 245.5, 'beta' : 8853.0, 'scaling' : 5.0e6},
    # '10' : {'alpha' : 338.1, 'beta' : 8450.6, 'scaling' : 5.0e6}
}

# These were always set by hand. Play with it !
lengthScales  = [240.0, 90.0, 90.0, 60.0]
variance      = 1.0e-8
noiseVariance = 1.0e-9
mapGenerator  = setup_map_generator(database, aircrafts, lengthScales, variance, noiseVariance, wind)

# Then find a good position to generate the map. An easy way to do this is to
# look at the cloud sensor data, find when it detected cloud and select a
# suitable time. Then you can find the aircraft position at that particular time
# with the function aircraft_position_at_time.
cloud0 = TimedData.from_database(database, [aircraft, 'cloud_channel_0'], keys)


# Define a mapWdith (in meters)
mapWidth = 2000.0

fig, axes = plt.subplots(1,2, sharex=True, sharey=True)
axes[0].grid()
axes[1].grid()

t0 = 2000
duration = 300.0
T = np.linspace(t0, t0 + duration, int(duration / 10))

p0 = aircraft_position_at_time(database, aircraft, T[0] + (T[-1] - T[0]) / 2)

for t in T:
    # p = np.array([p for p in p0])
    p = np.copy(p0)
    p[0] = t
    p[1] += wind[0]*(t - p0[0])
    p[2] += wind[1]*(t - p0[0])
    
    # This contains coordinates of the map to generate. It is a python tuple.
    # (float(t), slice(xmin, xmax), slice(ymin,ymax), float(z))
    # This particular one represents a 2D horizontal map. But you can generate full
    # 4D maps by using a tuple as following.
    # (slice(tmin, tmax), slice(xmin, xmax), slice(ymin,ymax), slice(zmin,zmax))
    keys = keys_from_position(p, mapWidth)
    
    # Finally ! You can generate some maps now
    mapValue0       = mapGenerator.get_value(keys)
    mapUncertainty0 = mapGenerator.get_std(keys)
    
    axes[0].set_title("t={:.2f}s".format(t - T[0]))
    display_scaled_array(mapValue0, axes[0], resample=4)
    display_scaled_array(mapUncertainty0, axes[1], resample=4)
    
    # set block to True if display window disappear as soon as they are displayed
    plt.show(block=False)
    plt.pause(0.1) # for crude video making

