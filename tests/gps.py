#! /usr/bin/python3

import sys
sys.path.append('../../')

from nephelae_base.types import Position
from nephelae_base.types import Gps
from nephelae_base.types import NavigationRef

gps0 = Gps(Position(0,0,0,0))
ref0 = NavigationRef(Position(1.0,1.0,1.0,1.0))

print(gps0 - ref0)




