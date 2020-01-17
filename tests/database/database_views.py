#! /usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt

from nephelae.database import NephelaeDataServer, DataServerView, DataServerTaggedView

database = NephelaeDataServer.load("/home/pnarvor/work/nephelae/data/temp/default.neph")
view0    = DataServerView(database)
view1    = DataServerTaggedView(database, ['200'])




