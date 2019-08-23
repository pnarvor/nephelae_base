#! /usr/bin/python3

import sys
sys.path.append('../../')

import nephelae.types as ntype

shape = ntype.Shape4D(
    ntype.DimensionShape(2, 0.0, 1.0),
    ntype.DimensionShape(2, 0.0, 2.0),
    ntype.DimensionShape(2, 0.0, 3.0),
    ntype.DimensionShape(2, 0.0, 4.0))

print("Spans:")
print(shape.t.span())
print(shape.x.span())
print(shape.y.span())
print(shape.z.span())

print("Locations:")
print(shape.t.locations())
print(shape.x.locations())
print(shape.y.locations())
print(shape.z.locations())

print("Points:")
# print(shape.locations())
points = shape.locations()
for i in range(points.shape[0]):
    print(points[i,:])

print("Distances :\n", shape.distances())

