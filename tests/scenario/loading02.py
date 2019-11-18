#! /usr/bin/python3

import sys
sys.path.append('../../')
import signal

from nephelae_scenario import Scenario


scenario = Scenario('config_examples/full01.yaml')
scenario.load()

def stop():
    if interface.running:
        print("Shutting down... ", end='')
        sys.stdout.flush()
        interface.stop()
        print("Complete.")
        exit()
signal.signal(signal.SIGINT, lambda sig,fr: stop())

# print(scenario.parser.yamlStream)
# print(scenario.config)
