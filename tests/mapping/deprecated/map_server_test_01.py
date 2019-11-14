#! /usr/bin/python3

import sys
sys.path.append('../../')
import numpy as np
import matplotlib.pyplot as plt

from nephelae.types   import Bounds
from nephelae.mapping import MapServer
from nephelae_mesonh  import MesonhMap, MesonhDataset

mesonhFiles = "/home/pnarvor/work/nephelae/data/nephelae-remote/MesoNH02/bomex_hf.nc"

dataset = MesonhDataset(mesonhFiles)
maps = {'lwc'   : MesonhMap("Liquid Water Content", dataset, 'RCT'),
        'wt'    : MesonhMap("Vertical Wind"       , dataset, 'WT'),
        'hwind' : MesonhMap("Horizontal Wind"     , dataset, ['UT','VT'])}

mapServer0 = MapServer(mapSet=maps, mapBounds=(None,Bounds(300.0,800.0),None,None))
mapServer1 = MapServer(mapSet=maps, mapBounds=(None,Bounds(300.0,800.0),Bounds(0.0,500.0),None))

fig, axes = plt.subplots(2,1, sharex=True)
# axes[0].imshow(mapServer0['lwc'][0.0,:,0.0:12000.0,650.0].data.T, origin='lower')
# axes[1].imshow(mapServer1['lwc'][0.0,:,0.0:12000.0,650.0].data.T, origin='lower')
axes[0].imshow(mapServer0['wt'][0.0,:,:,650.0].data.T, origin='lower')
axes[1].imshow(mapServer1['wt'][0.0,:,:,650.0].data.T, origin='lower')

plt.show(block=False)




