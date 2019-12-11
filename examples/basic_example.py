#! /usr/bin/python3

import signal

from nephelae_scenario         import Scenario
from nephelae_paparazzi.common import IvyStop, messageInterface
from nephelae_paparazzi.utils  import send_lwc

configFilename = '/home/pnarvor/work/nephelae/files-config/mission_only_200.yaml'
scenario = Scenario(configFilename)
scenario.load()
scenario.start()

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



