#! /usr/bin/python3

import sys
sys.path.append('../../')
import signal
import time

from nephelae_scenario         import Scenario
from nephelae_paparazzi.common import IvyStop, messageInterface
from nephelae_paparazzi.utils  import send_lwc

from nephelae.dataviews import DataView, DatabaseView

def stop():
    if scenario.running:
        print("Shutting down... ", end='', flush=True)
        scenario.stop()
        print("Complete.", flush=True)
    IvyStop()
    try:
        get_ipython().ask_exit()
    except NameError:
        sys.exit()
signal.signal(signal.SIGINT, lambda sig,fr: stop())

configFilename = '../../examples/config/demo_database_only.yaml'
scenario = Scenario(configFilename)
scenario.load()
scenario.start()

gpr = scenario.maps['LWC']










