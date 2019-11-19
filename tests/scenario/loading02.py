#! /usr/bin/python3

import sys
sys.path.append('../../')
import signal

from nephelae_scenario import Scenario
from nephelae_paparazzi.common import IvyStop


scenario = Scenario('config_examples/full01.yaml')
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


