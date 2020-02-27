#! /usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt

from nephelae.database import NephelaeDataServer
from nephelae_utils.analysis import TimedData, estimate_wind

# This is an example showing how to estimate the advective wind (average (x,y)
# wind) from the data of an aircraft flight.

# First loading a flight database.
databasePath = '/home/pnarvor/work/nephelae/data/barbados/post_processing/cams_logs/flight_02_08_03/database/database01.neph'
database = NephelaeDataServer.load(databasePath)

# Then we have to find a suitable section of the flight from which estimating
# the wind. A typical good flight section is when an aircraft is performing a
# circle (which it always does at some points in the flight, either to change
# altitude or the half circles at the end of hippodromes). To find such a
# section, plotting the flight trajectory does really help.

# To find the circles, one can look at two plots (t,x) and (t,y) and find
# section where the two curves both have a kind of "zigzag", sinusoidal-ish
# shape.

# To plot the flight path of the aircraft, one has to fetch the aircraft
# position from the database.
status7    = database['7','STATUS'](sortCriteria=lambda x: x.position.t)[:]
position7  = np.array([[s.position.t, s.position.x, s.position.y, s.position.z] for s in status7])
status10   = database['10','STATUS'](sortCriteria=lambda x: x.position.t)[:]
position10 = np.array([[s.position.t, s.position.x, s.position.y, s.position.z] for s in status10])

fig, axes = plt.subplots(2,1)
axes[0].plot( position7[:,0],  position7[:,1], label="East 7")
axes[0].plot( position7[:,0],  position7[:,2], label="North 7")
axes[0].plot(position10[:,0], position10[:,1], label="East 10")
axes[0].plot(position10[:,0], position10[:,2], label="North 10")
axes[0].legend(loc='upper right')
axes[0].grid()
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('(m)')

axes[1].plot( position7[:,1],  position7[:,2], label="Aircraft 7")
axes[1].plot(position10[:,1], position10[:,2], label="Aircraft 10")
axes[1].legend(loc='upper right')
axes[1].grid()
axes[1].set_xlabel('East (m)')
axes[1].set_ylabel('North (m)')
axes[1].set_aspect('equal')

# After looking at the plots, on this particular dataset, a good interval for
# aircraft 7 is between 630 seconds and 930 seconds
wind7, err = estimate_wind(database, '7', [630, 930])
print("Aircraft  7 wind estimation (m/s)    : [east : {:.2f}, north : {:.2f}]".format(wind7[0], wind7[1]))
print("Standard deviation of the error (m/s): {:.2f}".format(err))

# After looking at the plots, on this particular dataset, a good interval for
# aircraft 10 is between 875 seconds and 1040 seconds
wind10, err = estimate_wind(database, '10', [875, 1040])
print("Aircraft 10 wind estimation (m/s)    : [east : {:.2f}, north : {:.2f}]".format(wind10[0], wind10[1]))
print("Standard deviation of the error (m/s): {:.2f}".format(err))

# set block to True if display window disappear as soon as they are displayed
plt.show(block=False)

