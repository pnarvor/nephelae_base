#! /usr/bin/python3

import sys
sys.path.append('../../')

import nephelae.types as ntype

pos0 = ntype.Position(0,1,2,3)
print(pos0)
pos1 = pos0 * 10
print(pos1)
print(pos1 + pos0)
print(pos1 - pos0)
print(pos1 * pos0)


