#! /usr/bin/python3

# This is an example showing how to roughly compensate the battery voltage in
# the cloud sensor. More work is to be done to get this right. (Maybe an order
# 2 polynomial fit ?)
 
import numpy as np
import matplotlib.pyplot as plt

from nephelae.database import NephelaeDataServer
from nephelae_utils.analysis import TimedData, voltage_fit_parameters_estimation

# First loading a flight database.
databasePath = '/home/pnarvor/work/nephelae/data/barbados/post_processing/cams_logs/flight_02_08_03/database/database01.neph'
database = NephelaeDataServer.load(databasePath)

# We will work on aircraft 7 for this example
aircraft = '7'
keys = (slice(209,2755),)
cloud0  = TimedData.from_database(database, ['cloud_channel_0', aircraft], keys, name="Cloud 0", dataFetchFunc=lambda x: x.data.data[0])
voltage = TimedData.from_database(database,          ['energy', aircraft], keys, name="Voltage", dataFetchFunc=lambda x: x.data.data[1])

# Selecting a suitable section on which to estimate the fitting parameters
# (aircraft in level flight and no clouds). Plot the cloud data to select the
# section
timeInterval = [1100.0, 1900.0]
# Estimating the fitting parameters
alpha, beta  = voltage_fit_parameters_estimation(database, aircraft, 'cloud_channel_0', timeInterval)

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

# set block to True if display window disappear as soon as they are displayed
plt.show(block=False)

