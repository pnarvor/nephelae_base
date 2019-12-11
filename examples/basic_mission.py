#! /usr/bin/python3

import signal

from nephelae_scenario         import Scenario
from nephelae_paparazzi.common import IvyStop, messageInterface
from nephelae_paparazzi.utils  import send_lwc

configFilename = '/home/pnarvor/work/nephelae/files-config/mission_only_200.yaml'
scenario = Scenario(configFilename)
scenario.load()
scenario.start()

aircraft = scenario.aircrafts['200']
factory  = aircraft.missionFactories['Lace']
rules    = factory.parameterRules
print(rules['start'].summary())

def create():
    aircraft.create_mission('Lace', start=[747.24, 1078.94, 700.0])


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



