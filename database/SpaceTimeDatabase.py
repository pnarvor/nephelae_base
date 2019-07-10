# TODO TODO TODO TODO TODO TODO TODO
# Search for a dedicated library to do this
# TODO TODO TODO TODO TODO TODO TODO

import numpy as np
import bisect as bi

from nephelae_base.types import Position
from nephelae_base.types import SensorSample


class StbEntry:

    """StbEntry

    Aim to unify the elements in the SpaceTimeDatabase.
    Contains a space-time location and at least one tag.

    """

    def __init__(self, data, position, tags=['misc']):

        self.data     = data
        self.position = position
        self.tags     = tags


class StbSortableElement:

    """StbSortableElement

    Intended to be used as a generic container in sorted lists.
    Contains a single index value to use for sorting and a data sample.
    All the numerical comparison operators are overloaded to compare  only
    the indexes of two instances.

    TODO : see if already exists

    """

    def __init__(self, index, data):
        self.index = index
        self.data  = data

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{'+str(self.index)+' '+str(self.data)+'}'

    def __lt__(self, other):
        if isinstance(other, StbSortableElement):
            return self.index < other.index
        else:
            return self.index < other

    def __le__(self, other):
        if isinstance(other, StbSortableElement):
            return self.index <= other.index
        else:
            return self.index <= other

    def __eq__(self, other):
        if isinstance(other, StbSortableElement):
            return self.index == other.index
        else:
            return self.index == other

    def __ne__(self, other):
        if isinstance(other, StbSortableElement):
            return self.index != other.index
        else:
            return self.index != other

    def __ge__(self, other):
        if isinstance(other, StbSortableElement):
            return self.index >= other.index
        else:
            return self.index >= other

    def __gt__(self, other):
        if isinstance(other, StbSortableElement):
            return self.index > other.index
        else:
            return self.index > other


class SpaceTimeList:

    """SpaceTimeList

    Class to efficiently insert and retrieve data based on their space-time
    location.

    Heavily based on python3 bisect module.

    All data element are assumed to have the same interface as StbEntry

    Base principle is to keep 4 list containing the same data but sorted along
    each dimension of space time (seems an awful waste of memory but only
    diplicate references to data are duplicated, not the data it self).
    When a query is made, smaller lists are made from subsets of the main
    list and the result is the common elements between the smaller lists.

    /!\ Changed to basic python implementation. To be continued

    """

    def __init__(self):

        self.tSorted = []
        self.xSorted = []
        self.ySorted = []
        self.zSorted = []


    def insert(self, data):

        # data assumed to be of a StbEntry compliant type
        bi.insort(self.tSorted, StbSortableElement(data.position.t, data))
        bi.insort(self.xSorted, StbSortableElement(data.position.x, data))
        bi.insort(self.ySorted, StbSortableElement(data.position.y, data))
        bi.insort(self.zSorted, StbSortableElement(data.position.z, data))


    def __getitem__(self, keys):

        """SpaceTimeList.__getitem__
        keys : a tuple of slices(float,float,None)
               slices values are bounds of a 4D cube in which are the
               requested data
               There must exactly be 4 slices in the tuple
        """
        
        # # Supposedly less efficient way
        # def isInSlice(value, key):
        #     if key.start is not None:
        #         if value < key.start:
        #             return False
        #     if key.stop is not None:
        #         if value > key.stop:
        #             return False
        #     return True
        # res = self.tSorted
        # res = [item for item in res if isInSlice(item.position.t, keys[0])]
        # res = [item for item in res if isInSlice(item.position.x, keys[1])]
        # res = [item for item in res if isInSlice(item.position.y, keys[2])]
        # res = [item.data for item in res if isInSlice(item.position.z, keys[3])]
    
        # Supposedly efficient way
        # Using a python dict to remove duplicates
        outputDict = {}
        def extract_entries(sortedList, key, outputDict):
            slc = slice(bi.bisect_left( sortedList, key.start),
                        bi.bisect_right(sortedList, key.stop ), None)
            for element in sortedList[slc]:
                outputDict[id(element.data)] = element.data

        extract_entries(self.tSorted, keys[0], outputDict)
        extract_entries(self.xSorted, keys[1], outputDict)
        extract_entries(self.ySorted, keys[2], outputDict)
        extract_entries(self.zSorted, keys[3], outputDict)

        return list(outputDict.values())


class SpaceTimeDatabase:

    """SpaceTimeDatabase

    This is a test class for Nephelae raw Uav data server.
    Must handle space-time related requests like all data in a region of 
    space-time. (Hence the very well though name TODO: find a real one). 
    Made to match the subscriber pattern used in nephelae_paparazzi.PprzUav.

    """

    def __init__(self):
        
        self.navFrame = None
        self.gps      = []
        self.samples  = []


    def set_navigation_frame(self, navFrame):
        self.navFrame = navFrame


    def add_gps(self, msg):
        if self.navFrame is None:
            return
        self.gps.append(msg)


    def add_sample(self, msg):
        if self.navFrame is None:
            return
        self.samples.append(msg)
        


