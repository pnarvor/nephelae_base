#! /usr/bin/python3

import sys
sys.path.append('../../')
import os
import signal
import time

from nephelae.database import NephelaeDataServer

database = NephelaeDataServer.load('/home/pnarvor/work/nephelae/data/temp/default.neph')



