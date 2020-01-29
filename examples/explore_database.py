#! /usr/bin/python3

import time

from nephelae.database import NephelaeDataServer
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt

t0 = time.time()
database = NephelaeDataServer.load('/home/pnarvor/work/nephelae/data/barbados/logs/flight_01_28_01/database/database01.neph')
print("Loading time : ", time.time() - t0)

t0 = time.time()
channel0_10 = [entry.data for entry in database['10', 'cloud_channel_0'](sortCriteria=lambda x: x.position.t)[:]]
channel1_10 = [entry.data for entry in database['10', 'cloud_channel_1'](sortCriteria=lambda x: x.position.t)[:]]
channel0_12 = [entry.data for entry in database['12', 'cloud_channel_0'](sortCriteria=lambda x: x.position.t)[:]]
channel1_12 = [entry.data for entry in database['12', 'cloud_channel_1'](sortCriteria=lambda x: x.position.t)[:]]
print("Query time : ", (time.time() - t0) / 4)

temperature_10 = [entry.data for entry in database['10', 'temperature'](sortCriteria=lambda x: x.position.t)[:]]
t_t10 = [sample.position.t for sample in temperature_10]
data_temperature_10 = [sample.data[0] for sample in temperature_10]
pressure_10 = [entry.data for entry in database['10', 'pressure'](sortCriteria=lambda x: x.position.t)[:]]
t_t10 = [sample.position.t for sample in pressure_10]
data_pressure_10 = [sample.data[0] for sample in pressure_10]

temperature_12 = [entry.data for entry in database['12', 'temperature'](sortCriteria=lambda x: x.position.t)[:]]
t_t12 = [sample.position.t for sample in temperature_12]
data_temperature_12 = [sample.data[0] for sample in temperature_12]
pressure_12 = [entry.data for entry in database['12', 'pressure'](sortCriteria=lambda x: x.position.t)[:]]
t_t12 = [sample.position.t for sample in pressure_12]
data_pressure_12 = [sample.data[0] for sample in pressure_12]

status_10 = [entry.data for entry in database['10', 'STATUS'](sortCriteria=lambda x: x.position.t)[:]]
t_status_10 = [status.position.t for status in status_10]
status_12 = [entry.data for entry in database['12', 'STATUS'](sortCriteria=lambda x: x.position.t)[:]]
t_status_12 = [status.position.t for status in status_12]

t_10 = [sample.position.t for sample in channel0_10]
z_10 = [sample.position.z for sample in channel0_10]
data_channel_0_10 = [sample.data[0] for sample in channel0_10]
data_channel_1_10 = [sample.data[0] for sample in channel1_10]

t_12 = [sample.position.t for sample in channel0_12]
z_12 = [sample.position.z for sample in channel0_12]
data_channel_0_12 = [sample.data[0] for sample in channel0_12]
data_channel_1_12 = [sample.data[0] for sample in channel1_12]


fig, axes = plt.subplots(4,1, sharex=True)
axes[0].plot(t_12, data_channel_0_12, label='cloud_channel_0_12')
axes[0].plot(t_12, data_channel_1_12, label='cloud_channel_1_12')
axes[0].plot(t_12, medfilt(data_channel_1_12, 5), label='cloud_channel_1_12_median_5')
axes[0].plot(t_12, medfilt(data_channel_1_12, 3), label='cloud_channel_1_12_median_3')
axes[0].legend(loc="upper right")
axes[0].grid()
axes[0].set_xlabel('Time (s)')

axes[1].plot(t_status_12, [status.pitch   for status in status_12], label='pitch_12')
# axes[1].plot(t_status_12, [status.roll    for status in status_12], label='roll_12')
# axes[1].plot(t_status_12, [status.heading for status in status_12], label='heading_12')
axes[1].legend(loc="upper right")
axes[1].grid()
axes[1].set_xlabel('Time (s)')

axes[2].plot(t_t12, data_temperature_12, label='temperature_12')
axes[2].legend(loc="upper right")
axes[2].grid()
axes[2].set_xlabel('Time (s)')

# axes[3].plot(t_12, z_12, label='elevation_12')
axes[3].plot(t_t12, data_pressure_12, label='pressure_12')
axes[3].legend(loc="upper right")
axes[3].grid()
axes[3].set_xlabel('Time (s)')
axes[3].set_ylabel('Elevation  (m)')

fig, axes = plt.subplots(4,1, sharex=True)
# axes[0].plot(t_10, medfilt(data_channel_1_10, 5), label='cloud_channel_1_10_median_5')
# axes[0].plot(t_10, medfilt(data_channel_1_10, 3), label='cloud_channel_1_10_median_3')
axes[0].plot(t_10, data_channel_0_10, label='cloud_channel_0_10')
axes[0].plot(t_10, data_channel_1_10, label='cloud_channel_1_10')
axes[0].legend(loc="upper right")
axes[0].grid()
axes[0].set_xlabel('Time (s)')

axes[1].plot(t_status_10, [status.pitch   for status in status_10], label='pitch_10')
# axes[1].plot(t_status_10, [status.roll    for status in status_10], label='roll_10')
# axes[1].plot(t_status_10, [status.heading for status in status_10], label='heading_10')
axes[1].legend(loc="upper right")
axes[1].grid()
axes[1].set_xlabel('Time (s)')

axes[2].plot(t_t10, data_temperature_10, label='temperature_10')
axes[2].legend(loc="upper right")
axes[2].grid()
axes[2].set_xlabel('Time (s)')

# axes[3].plot(t_10, z_10, label='elevation_10')
axes[3].plot(t_t10, data_pressure_10, label='pressure_10')
axes[3].legend(loc="upper right")
axes[3].grid()
axes[3].set_xlabel('Time (s)')
axes[3].set_ylabel('Elevation  (m)')

plt.show(block=False)


