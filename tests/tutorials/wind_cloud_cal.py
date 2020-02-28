#! /usr/bin/python3

# This is an example showing how to roughly compensate the battery voltage in
# the cloud sensor. More work is to be done to get this right. (Maybe an order
# 2 polynomial fit ?)
 
import numpy as np
import datetime
import matplotlib.pyplot as plt

from nephelae.database import NephelaeDataServer
from nephelae_utils.analysis import TimedData, voltage_fit_parameters_estimation, estimate_wind

# First loading a flight database.
databasePath = '/home/pnarvor/work/nephelae/data/barbados/post_processing/cams_logs/flight_01_28_01/database/flight_recorder_database.neph'
# databasePath = '/home/pnarvor/work/nephelae/data/barbados/post_processing/cams_logs/flight_01_29_01/database/database01.neph'
database = NephelaeDataServer.load(databasePath)
print("Aircrafts :", database.uavIds)
print("Time :", datetime.datetime.utcfromtimestamp(
    int(database.navFrame.position.t) - 4*3600).strftime('%Y-%m-%d %H:%M:%S'))

# We will work on aircraft 7 for this example
aircraft = '12'
keys = (slice(None),)
# keys = (slice(461,2755),)
cloud0  = TimedData.from_database(database, ['cloud_channel_0', aircraft], keys, name="Cloud 0", dataFetchFunc=lambda x: x.data.data[0])
voltage = TimedData.from_database(database,          ['energy', aircraft], keys, name="Voltage", dataFetchFunc=lambda x: x.data.data[1])

# Selecting a suitable section on which to estimate the fitting parameters
# (aircraft in level flight and no clouds). Plot the cloud data to select the
# section
cloudInterval = [1600.0, 2800.0]
windInterval  = [600, 750]
# Estimating the fitting parameters
alpha, beta  = voltage_fit_parameters_estimation(database, aircraft, 'cloud_channel_0', cloudInterval)
print("Alpha : ", alpha)
print("Beta  : ", beta)

# Calculating voltage fitted on cloud sensor
fittedVoltage = voltage.copy(newName="Fitted voltage")
fittedVoltage.data = alpha*voltage.data + beta
fittedVoltage.sync_on(cloud0)

# Compensating voltage in cloud sensor measurements
cloudCompensated      = cloud0.copy(newName="Compensated cloud")
cloudCompensated.data = cloudCompensated.data - fittedVoltage.data

fig, axes = plt.subplots(3,1, sharex=True)
cloud0.plot(axes[0])
fittedVoltage.plot(axes[0])
axes[0].legend(loc='upper right')
axes[0].grid()
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Cloud Sensor value (?)')

voltage.plot(axes[1])
axes[1].legend(loc='upper right')
axes[1].grid()
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Voltage (V)')

cloudCompensated.plot(axes[2])
axes[2].legend(loc='upper right')
axes[2].grid()
axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('Cloud Sensor value (?)')

# To plot the flight path of the aircraft, one has to fetch the aircraft
# position from the database.
status    = database[aircraft,'STATUS'](sortCriteria=lambda x: x.position.t)[:]
position  = np.array([[s.position.t, s.position.x, s.position.y, s.position.z] for s in status])

fig, axes = plt.subplots(2,1)
axes[0].plot( position[:,0],  position[:,1], label="East "+aircraft)
axes[0].plot( position[:,0],  position[:,2], label="North "+aircraft)
axes[0].legend(loc='upper right')
axes[0].grid()
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('(m)')

axes[1].plot( position[:,1],  position[:,2], label="Aircraft "+aircraft)
axes[1].legend(loc='upper right')
axes[1].grid()
axes[1].set_xlabel('East (m)')
axes[1].set_ylabel('North (m)')
axes[1].set_aspect('equal')

# set block to True if display window disappear as soon as they are displayed
plt.show(block=False)

wind, err = estimate_wind(database, aircraft, windInterval)
print("Aircraft wind estimation (m/s)    : [east,north : {:.2f}, {:.2f}]".format(wind[0], wind[1]))
print("Standard deviation of the error (m/s): {:.2f}".format(err))
