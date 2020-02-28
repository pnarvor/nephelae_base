#! /usr/bin/python3

# This is a tutorial showing how to write to and read from a NephelaeDataServer

import numpy as np
from numpy.random import randn
import matplotlib.pyplot as plt

from nephelae.types          import Position, SensorSample
from nephelae.database       import SpatializedDatabase, SpbEntry
from nephelae_utils.analysis import TimedData


# First we have to get data. Lets generate some. Lets say we have two aircrafts
# named aircraft0 and aircraft1 flying in 200m radius circles at 20m/s, 300.0m
# and 400.0m above sea level. Its position is logged at 2 Hz. It has a pressure
# and a temperature sensor. The pressure sensor is logged at 4Hz and the
# temperature sensor is logged at 1Hz.

# This function is returning a 4D position given a time to generate our
# aircraft path. Here a circle, has stated above.
def get_aircraft0_position(t):
    return Position(t=t,
                    x = 200.0*np.cos(20.0/200.0*t),
                    y = 200.0*np.sin(20.0/200.0*t),
                    z = 300.0)
def get_aircraft1_position(t):
    return Position(t=t,
                    x = 200.0*np.cos(20.0/200.0*t) + 300,
                    y = 200.0*np.sin(20.0/200.0*t) + 100,
                    z = 300.0)

# let generate 2min of data
duration = 120

# Setting a fixed random seed for repeatability
np.random.seed(42)

# Generating random pressure samples at 4Hz
# (Gaussian distribution with 10.0 standard deviation)
pressureTimestamps = np.linspace(0, duration, int(duration*4.0))
pressureValues0    = 10.0*randn(len(pressureTimestamps))
# Making it smoother because reasons
pressureValues0    = 1013.0 + np.convolve(pressureValues0, np.ones(7) / 7, 'same')

# Generating random temperature samples at 4Hz
# (Gaussian distribution with 10.0 standard deviation)
temperatureTimestamps = np.linspace(0, duration, int(duration*4.0))
temperatureValues0    = 5.0*randn(len(temperatureTimestamps))
# Making it smoother because reasons
temperatureValues0    = 15.0 + np.convolve(temperatureValues0, np.ones(31) / 31, 'same')

# Samples for the second aircraft (we use the same timestamps for convenience)
pressureValues1    = 10.0*randn(len(pressureTimestamps))
pressureValues1    = 1013.0 + np.convolve(pressureValues1, np.ones(7) / 7, 'same')
temperatureValues1 = 5.0*randn(len(temperatureTimestamps))
temperatureValues1 = 15.0 + np.convolve(temperatureValues1, np.ones(31) / 31, 'same')

# Plotting generated data
fig, axes = plt.subplots(2,1, sharex=True)
axes[0].set_title('Generated pressure samples')
axes[0].plot(pressureTimestamps, pressureValues0, label='Aircraft 0')
axes[0].plot(pressureTimestamps, pressureValues1, label='Aircraft 1')
axes[0].legend(loc='upper right')
axes[0].grid()
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Pressure (hPa)')
axes[0].set_title('Generated temperature samples')
axes[1].plot(temperatureTimestamps, temperatureValues0, label='Aircraft 0')
axes[1].plot(temperatureTimestamps, temperatureValues1, label='Aircraft 1')
axes[1].legend(loc='upper right')
axes[1].grid()
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Temperature (C)')
plt.show(block=False)

# From there we have all we need to start making a database
# Here we use a SpacializeDatabase for the tutorial but the ones used in the
# CAMS softwares are all NephelaeDataServer which is actually a specialization
# (child type) of SpacializedDatabase. But the two handle the same for what
# will be done in the following, except that the NephelaeDataServer is creating
# SpbEntries automatically from other types.
database = SpatializedDatabase()

# Samples cannot be inserted in batch (the database is meant to work in real
# time, so there shouldn't be any batch anyway in a non-simulated case). But
# the entry can be entered in any order. The end result will be the same as the
# database is sorting data as they arrive.

# So its time to feed the database
# inserting pressure samples
for t, pressureValue0, pressureValue1 in zip(pressureTimestamps, pressureValues0, pressureValues1):
    # The SpacializedDatabase accepts only one type : a SbpEntry
    # The SbpEntry object contains a position (t,x,y,z) and a set of string
    # tags which are used for data sorting and retrieval. A SpbEntry must be
    # created for each unique sample.

    # Getting the aircraft position at time t:
    position = get_aircraft0_position(t)

    # Creating the list of tags. You can put as many as you want. The goal is
    # to make it easy to find the data you want inside the database.
    tags = ['aircraft0', 'pressure', 'sensor_sample']

    # Creating a new SpbEntry for a pressure sample of aircraft0.
    newEntry = SpbEntry(data=pressureValue0,
                        position=position,
                        tags=tags)

    # Inserting in the database
    database.insert(newEntry)

    # Doing the same thing for aircraft1, but with less talk
    database.insert(SpbEntry(data=pressureValue1,
                             position=get_aircraft1_position(t),
                             tags=['aircraft1', 'pressure', 'sensor_sample']))

# inserting temperature samples
for t, temperatureValue0, temperatureValue1 in zip(temperatureTimestamps, temperatureValues0, temperatureValues1):
    database.insert(SpbEntry(data=temperatureValue0,
                             position=get_aircraft0_position(t),
                             tags=['aircraft0', 'temperature', 'sensor_sample']))
    database.insert(SpbEntry(data=temperatureValue1,
                             position=get_aircraft1_position(t),
                             tags=['aircraft1', 'temperature', 'sensor_sample']))

# Now the database is filled with data. It can be saved for latter use like
# this:
# SpatializedDatabase.save(database, 'database.neph')
# Note : remember to remove or rename 'database.neph' if you want to write this
# file again. Alternatively you can force write:
SpatializedDatabase.save(database, 'database.neph', force=True)

# And loaded like this :
database = SpatializedDatabase.load('database.neph')

# This section will explain how to get data from the database. Lets suppose you
# want the pressure sample measured by aircraft1 between 30.0s and 60.0s:
searchTags = ['aircraft1', 'pressure']
# The search keys are a tuple of float or slices to represent a section of
# spacetime in (t,x,y,z) order. Here t is between 30.0s and 60.0s. The other
# dimension are set to slice(None) to indicate not search bounds is apply to
# the dimension
searchKeys = (slice(30.0, 60.0), slice(None), slice(None), slice(None))

# Output entry will not be necessarily sorted in time ascending order. You can
# request to sort the data with a given criterion by giving a lambda function.
# The following one output the timestamp of an entry, so the output will be
# sorted in a time ascending order.
timeAscending=lambda x: x.position.t

# Finally ! We can search some entries now
pressure1 = database.find_entries(tags=searchTags, keys=searchKeys, sortCriteria=timeAscending)

# The same query but with syntactic sugar: (way faster to write)
pressure1 = database['aircraft1', 'pressure'](sortCriteria=lambda x: x.position.t)[30.0:60.0]

# pressure1 is a list containing all SpbEntry with t between 30.0s and 60.0 and
# contains all the search tags

# Let get all data in this time span and plot them
pressure0 = database['aircraft0', 'pressure'](sortCriteria=lambda x: x.position.t)[30.0:60.0]
temperature0 = database['aircraft0', 'temperature'](sortCriteria=lambda x: x.position.t)[30.0:60.0]
temperature1 = database['aircraft1', 'temperature'](sortCriteria=lambda x: x.position.t)[30.0:60.0]

fig, axes = plt.subplots(2,2,sharex=True)
axes[0][0].set_title('Pressure Aircraft 0')
axes[0][0].plot(pressureTimestamps, pressureValues0, label='Original data')
axes[0][0].scatter([e.position.t for e in pressure0], [e.data for e in pressure0], label='Fetched database data')
axes[0][0].legend(loc='upper right')
axes[0][0].grid()
axes[0][0].set_xlabel('Time (s)')
axes[0][0].set_ylabel('Pressure (hPa)')
axes[0][1].set_title('Pressure Aircraft 1')
axes[0][1].plot(pressureTimestamps, pressureValues1, label='Original data')
axes[0][1].scatter([e.position.t for e in pressure1], [e.data for e in pressure1], label='Fetched database data')
axes[0][1].legend(loc='upper right')
axes[0][1].grid()
axes[0][1].set_xlabel('Time (s)')
axes[0][1].set_ylabel('Pressure (hPa)')
axes[1][0].set_title('temperature Aircraft 0')
axes[1][0].plot(temperatureTimestamps, temperatureValues0, label='Original data')
axes[1][0].scatter([e.position.t for e in temperature0], [e.data for e in temperature0], label='Fetched database data')
axes[1][0].legend(loc='upper right')
axes[1][0].grid()
axes[1][0].set_xlabel('Time (s)')
axes[1][0].set_ylabel('Temperature (C)')
axes[1][1].set_title('temperature Aircraft 1')
axes[1][1].plot(temperatureTimestamps, temperatureValues1, label='Original data')
axes[1][1].scatter([e.position.t for e in temperature1], [e.data for e in temperature1], label='Fetched database data')
axes[1][1].legend(loc='upper right')
axes[1][1].grid()
axes[1][1].set_xlabel('Time (s)')
axes[1][1].set_ylabel('Temperature (C)')


# Another example but giving bounds in y dimension. This will fetch data for
# which -50.0 <= position.y <= 50.0
pressure0 = database['aircraft0', 'pressure'](sortCriteria=lambda x: x.position.t)[:,:,-50:50]
pressure1 = database['aircraft1', 'pressure'](sortCriteria=lambda x: x.position.t)[:,:,-50:50]
temperature0 = database['aircraft0', 'temperature'](sortCriteria=lambda x: x.position.t)[:,:,-50:50]
temperature1 = database['aircraft1', 'temperature'](sortCriteria=lambda x: x.position.t)[:,:,-50:50]

fig, axes = plt.subplots(2,2,sharex=True)
axes[0][0].set_title('Pressure Aircraft 0 (where -50<=position.y<=50)')
axes[0][0].plot(pressureTimestamps, pressureValues0, label='Original data')
axes[0][0].scatter([e.position.t for e in pressure0], [e.data for e in pressure0], label='Fetched database data')
axes[0][0].legend(loc='upper right')
axes[0][0].grid()
axes[0][0].set_xlabel('Time (s)')
axes[0][0].set_ylabel('Pressure (hPa)')
axes[0][1].set_title('Pressure Aircraft 1 (where -50<=position.y<=50)')
axes[0][1].plot(pressureTimestamps, pressureValues1, label='Original data')
axes[0][1].scatter([e.position.t for e in pressure1], [e.data for e in pressure1], label='Fetched database data')
axes[0][1].legend(loc='upper right')
axes[0][1].grid()
axes[0][1].set_xlabel('Time (s)')
axes[0][1].set_ylabel('Pressure (hPa)')
axes[1][0].set_title('temperature Aircraft 0 (where -50<=position.y<=50)')
axes[1][0].plot(temperatureTimestamps, temperatureValues0, label='Original data')
axes[1][0].scatter([e.position.t for e in temperature0], [e.data for e in temperature0], label='Fetched database data')
axes[1][0].legend(loc='upper right')
axes[1][0].grid()
axes[1][0].set_xlabel('Time (s)')
axes[1][0].set_ylabel('Temperature (C)')
axes[1][1].set_title('temperature Aircraft 1 (where -50<=position.y<=50)')
axes[1][1].plot(temperatureTimestamps, temperatureValues1, label='Original data')
axes[1][1].scatter([e.position.t for e in temperature1], [e.data for e in temperature1], label='Fetched database data')
axes[1][1].legend(loc='upper right')
axes[1][1].grid()
axes[1][1].set_xlabel('Time (s)')
axes[1][1].set_ylabel('Temperature (C)')


# Regenerating aircrafts path for plot
trajAircraft0 = []
trajAircraft1 = []
for t in pressureTimestamps:
    pos = get_aircraft0_position(t)
    trajAircraft0.append([pos.x, pos.y])
    pos = get_aircraft1_position(t)
    trajAircraft1.append([pos.x, pos.y])
trajAircraft0 = np.array(trajAircraft0)
trajAircraft1 = np.array(trajAircraft1)

# Plotting where pressure data was fetched
fig, axes = plt.subplots(1,1)
axes.plot(trajAircraft0[:,0], trajAircraft0[:,1], label='Trajectory Aircraft 0')
axes.plot(trajAircraft1[:,0], trajAircraft1[:,1], label='Trajectory Aircraft 1')
axes.scatter([e.position.x for e in pressure0], [e.position.y for e in pressure0], label='Fetched pressure data locations aircraft 0')
axes.scatter([e.position.x for e in pressure1], [e.position.y for e in pressure1], label='Fetched pressure data locations aircraft 1')
axes.legend(loc='lower right')
axes.grid()
axes.set_xlabel('x (m)')
axes.set_ylabel('y (m)')
axes.set_aspect('equal')


plt.show(block=False)






