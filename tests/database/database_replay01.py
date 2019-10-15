#! /usr/bin/python3

import sys
sys.path.append('../../')
import os
import signal
import time

from ivy.std_api import *
import logging

from nephelae.database import DatabasePlayer

class Logger:

    def __init__(self):
        pass

    def add_sample(self, sample):
        print(sample, end="\n\n")

    def add_gps(self, gps):
        print(gps, end="\n\n")


# dtbase = DatabasePlayer('output/database01.neph')
dtbase = DatabasePlayer('/home/pnarvor/work/nephelae/data/temp/dt5_01_1.neph')

logger = Logger()
dtbase.add_gps_observer(logger)
dtbase.add_sensor_observer(logger)

dtbase.play(looped=True)

signal.signal(signal.SIGINT, lambda sig, frame: dtbase.stop())

