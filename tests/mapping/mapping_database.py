#! /usr/bin/python3

import signal

from nephelae_scenario         import Scenario
from nephelae_paparazzi.common import IvyStop, messageInterface
from nephelae_paparazzi.utils  import send_lwc

scenario = Scenario('../config-files/mapping_200.yaml')
scenario.load()
scenario.start()

flightAreaKeys = [slice(scenario.flightArea[0][0], scenario.flightArea[1][0]),
                  slice(scenario.flightArea[0][1], scenario.flightArea[1][1]),
                  slice(scenario.flightArea[0][2], scenario.flightArea[1][2])]

def compute_map():
    t0   = scenario.database.last_entry('RCT').position.t
    print("Current time :", t0)
    keys = [t0 - 150] + flightAreaKeys
    return scenario.maps['LWC'][keys]





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



