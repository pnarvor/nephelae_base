#! /usr/bin/python3

from nephelae.database import NephelaeDataServer
import numpy as np
import matplotlib.pyplot as plt

database = NephelaeDataServer.load('/home/pnarvor/work/nephelae/data/barbados/logs/flight_01_26_03_simu/database/database01.neph')
# database = NephelaeDataServer.load('/home/pnarvor/work/nephelae/data/barbados/logs/flight_01_26_03_simu/database/database01.neph'


channel0 = [entry.data for entry in database['cloud_channel_0'](sortCriteria=lambda x: x.position.t)[:]]
channel1 = [entry.data for entry in database['cloud_channel_1'](sortCriteria=lambda x: x.position.t)[:]]

t = [sample.position.t for sample in channel0]
z = [sample.position.z for sample in channel0]
data_channel_0 = [sample.data[0] for sample in channel0]
data_channel_1 = [sample.data[0] for sample in channel1]


fig, axes = plt.subplots(2,1, sharex=True)
axes[0].plot(t, data_channel_0, label='cloud_channel_0')
axes[0].plot(t, data_channel_1, label='cloud_channel_1')
axes[0].legend(loc="upper right")
axes[0].grid()
axes[0].set_xlabel('Time (s)')

axes[1].plot(t, z, label='elevation')
axes[1].legend(loc="upper right")
axes[1].grid()
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Elevation  (m)')

plt.show(block=False)


