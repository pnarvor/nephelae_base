# Dataviews are type meant to handle the interface between the database and
# data consumers. Their purpose includes abstracting database access (several
# ways of accessing data depending on the consumer), do simple data
# pre-processing (sensor calibration...), while being able to change their
# behavior online.

from .DataView import DataView
