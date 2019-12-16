#! /usr/bin/python3

import signal

from nephelae_scenario         import Scenario
from nephelae_paparazzi.common import IvyStop, messageInterface
from nephelae_paparazzi.utils  import send_lwc

configFilename = 'config/demo_missions_fixed.yaml'
scenario = Scenario(configFilename)
scenario.load()
scenario.start()

# aircraft = scenario.aircrafts['200']
# factory  = aircraft.missionFactories['Lace']
# rules    = factory.parameterRules
# print(rules['start'].summary())
# 
# def create():
#     aircraft.create_mission('Rosette', start=[800.97, 821.76, 700.0])

aircraft200 = scenario.aircrafts['200']
aircraft201 = scenario.aircrafts['201']

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



