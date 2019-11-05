#! /usr/bin/python3

import sys
sys.path.append('../../')
import os
import signal
import time

from ivy.std_api import *
import logging

from nephelae_paparazzi import PprzMesonhUav, PprzSimulation
from nephelae.database import NephelaeDataServer

# mesonhFiles = '/home/pnarvor/work/nephelae/data/MesoNH-2019-02/REFHR.1.ARMCu.4D.nc'
mesonhFiles = '/local/fseguin/nephelae_data/MesoNH02/bomex_hf.nc'



dtbase = NephelaeDataServer()
# dtbase.enable_periodic_save('output/database01.neph', timerTick=10.0)

def build_uav(uavId, navRef):
    uav = PprzMesonhUav(uavId, navRef, mesonhFiles, ['RCT', 'WT'])
    uav.add_sensor_observer(dtbase)
    uav.add_gps_observer(dtbase)
    return uav
interface = PprzSimulation(mesonhFiles,
                           ['RCT', 'WT'],
                           build_uav_callback=build_uav)
interface.start()
# Has to be called after interface.start()
dtbase.set_navigation_frame(interface.navFrame)



def stop():
    if interface.running:
        print("Shutting down... ", end='')
        sys.stdout.flush()
        interface.stop()
        dtbase.disable_periodic_save()
        print("Complete.")
signal.signal(signal.SIGINT, lambda sig,fr: stop())

