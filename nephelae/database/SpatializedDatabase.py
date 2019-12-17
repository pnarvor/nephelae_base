# TODO TODO TODO TODO TODO TODO TODO
# Search for a dedicated library to do this
# Go search around pysqlite
# TODO TODO TODO TODO TODO TODO TODO

import numpy as np
import bisect as bi
import pickle
import os
import threading
from warnings import warn

from nephelae.types import Bounds

class SpbEntry:

    """
    SpbEntry

    Database entry. Contains a position (t,x,y,z) and tags to be searchable
    by the database.

    Attributes
    ----------

    data : any type
        Data to store in a database.

    position : nephelae.types.Position
        An (t,x,y,z) position to enable the database to search in a localised
        region of space-time.

    tags : [str,...]
        Tags to classify data. Used for retrieve data from the database.

    """

    def __init__(self, data, position, tags=['misc']):

        """
        data : any type
            Data to store in a database.

        position : nephelae.types.Position
            An (t,x,y,z) position to enable the database to search in a
            localised region of space-time.

        tags : [str,...]
            Tags to classify data. Used for retrieve data from the database.
        """

        self.data     = data
        self.position = position
        self.tags     = tags


    def __repr__(self):
        return "Entry at position : " + str(self.position) + \
               " tags : " + str(self.tags)


    def __str__(self):
        return "Entry at position : " + str(self.position) + \
               ", tags : " + str(self.tags) + ", data : " + str(self.data)


    def __eq__(self, other):
        """
        Checks equality with other entry.
        (Not sure why it is there... to be checked)
        """
        if self.position != other.position:
            return False
        elif self.tags != other.tags:
            return False
        elif str(self.data) != str(other.data):
            # Ugly. Re-check this.
            return False
        return True


class SpbSortableElement:

    """
    SpbSortableElement

    Intended to be used as a generic container, sortable with an arbitrary
    criterion. This class contains an attribute containing a single value
    used to compare two SpbSortableElement.
    
    The comparison operators where re-implemented in this class for this purpose.

    Example:

    One has a collection of samples measured at specific time stored in the
    data0 list and wants to store them in a time ascending order :
    
    timeSortedList = [SpbSortableElement(datum.t, datum) for datum in data]
    timeSortedList.sort()

    In this exemple, each SpbSortableElement.index was set to datum.t. The
    Comparison between each SpbSortableElement is between the 
    SpbSortableElements.index thanks to the re-implementation of the comparison
    operators. The list then sortable in time ascending order using standard
    python methods. If datum.x where used instead of datum.t, the list would be
    sorted in x ascending order.

    Note : python lists are perfectly capable of sorting themselves with an
    arbitrary criterion (given as a lambda function in the sort method). 
    However, the python bisect module used in this module, used to quickly
    insert and retrieve data from a sorted list is not capable of such
    behavior. Hence the necessity of using this type.
    
    TODO : take a look inside the bisect module to see if this is possible
    to implement. (would make the code clearer and computation faster).
    (Also you may have a commit with your name inside python sources. No this
    is not a bait).

    """

    def __init__(self, index, data):
        self.index = index
        self.data  = data

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{'+str(self.index)+' '+str(self.data)+'}'

    def __lt__(self, other):
        if isinstance(other, SpbSortableElement):
            return self.index < other.index
        else:
            return self.index < other

    def __le__(self, other):
        if isinstance(other, SpbSortableElement):
            return self.index <= other.index
        else:
            return self.index <= other

    def __eq__(self, other):
        if isinstance(other, SpbSortableElement):
            return self.index == other.index
        else:
            return self.index == other

    def __ne__(self, other):
        if isinstance(other, SpbSortableElement):
            return self.index != other.index
        else:
            return self.index != other

    def __ge__(self, other):
        if isinstance(other, SpbSortableElement):
            return self.index >= other.index
        else:
            return self.index >= other

    def __gt__(self, other):
        if isinstance(other, SpbSortableElement):
            return self.index > other.index
        else:
            return self.index > other


class SpatializedList:

    """
    SpatializedList

    Class to (supposedly) efficiently insert and retrieve data based on their
    space-time location (based on python3 bisect module), and associated tags.

    All inserted data elements are assumed to have the same interface as
    SpbEntry (have a position (nephelae.types.Position) attribute, and a 
    tags (list(str,...)) attribute).

    This class manage 4 lists containing the same data but each sorted along
    a different dimension of space-time (seems an awful waste of memory but
    only references to data are duplicated, not the data itself). This allows
    for fast retrieval of data in a region of interest.

    Note : A huge memory space is used (seems too large). Memory usage is to
    be investigated.

    Methods
    -------
    find_entries(tags, keys, sortCriteria) -> list(SpbEntry,...):
        Method to search data, based on tags and space-time region.
        The space-time must be a tuple of slices (same format as keys in a
        __getitem__ method).

    find_bounds(tags, keys) -> list(nephelae.types.Bounds, ...):
        Similar to find_entries method but returns the bounding box for data
        with given tags and inside the space-time regien given by keys.

    """

    def __init__(self):

        self.tSorted = []
        self.xSorted = []
        self.ySorted = []
        self.zSorted = []


    def __len__(self):
        return len(self.tSorted)


    def insert(self, data):

        # data assumed to be of a SpbEntry compliant type
        bi.insort(self.tSorted, SpbSortableElement(data.position.t, data))
        bi.insort(self.xSorted, SpbSortableElement(data.position.x, data))
        bi.insort(self.ySorted, SpbSortableElement(data.position.y, data))
        bi.insort(self.zSorted, SpbSortableElement(data.position.z, data))


    def process_keys(self, keys, assumePositiveTime=False):
        """Ensure we have a tuple of 4 slices, and format the time key"""

        def process_time_key(key, sortedList):
            """Helper key format function of the time key"""
            if not isinstance(key, slice) and not isinstance(key, (int, float)):
                raise ValueError("key must be a slice or a scalar (int or float)")
            if sortedList is None:
                return slice(None)            
            if isinstance(key, slice):
                if key.start is None:
                    key_start = None
                elif key.start < 0.0:
                    key_start = sortedList[-1].index + key.start
                else:
                    key_start = key.start
                if key.stop is None:
                    key_stop = None
                elif key.stop < 0.0:
                    key_stop = sortedList[-1].index + key.stop
                else:
                    key_stop = key.stop
                return slice(key_start, key_stop)
            else:
                return key
        if keys is None:
            # in this case fetch all data.
            return (slice(None), slice(None), slice(None), slice(None))
        keys = list(keys)
        while len(keys) < 4:
            # Fetch all data on dimensions without key
            keys.append(slice(None))

        if assumePositiveTime:
            return (process_time_key(keys[0], self.tSorted),
                    keys[1],
                    keys[2],
                    keys[3])
        else:
            return keys


    def build_entry_dict(self, tags=[], keys=None, assumePositiveTime=False):

        """
        keys : a tuple of slices(float,float,None)
               slices values are bounds of a 4D cube in which are the
               requested data
               There must exactly be 4 slices in the tuple
        """
        
        keys = self.process_keys(keys, assumePositiveTime)

        # Using a python dict to be able to remove duplicates
        # Supposedly efficient way
        outputDict = {}
        def extract_entries(sortedList, key, outputDict):
            "Check if all tags are present"
            def check_tags(element, outputDict):
                if all([tag in element.data.tags for tag in tags]):
                    if id(element.data) not in outputDict.keys():
                        outputDict[id(element.data)] = []
                    # Will insert if tags is empty (all([]) returns True)
                    outputDict[id(element.data)].append(element.data)
                    return True
                return False

            if isinstance(key, slice):
                if key.start is None:
                    key_start = None
                else:
                    key_start = bi.bisect_left(sortedList, key.start)
                if key.stop is None:
                    key_stop = None
                else:
                    key_stop = bi.bisect_right(sortedList, key.stop)
                slc = slice(key_start, key_stop, None)
            else:
                if key is None:
                    slc = None
                else:
                    slc = bi.bisect_left(sortedList, key)
            if isinstance(slc, slice):
                for element in sortedList[slc]:
                    check_tags(element, outputDict)
            else:
                if slc == len(sortedList):
                    slc = len(sortedList)-1
                compteur = 0
                for elem1, elem2 in zip(reversed(sortedList[:slc]), sortedList[slc:]):
                    if check_tags(elem1, outputDict):
                        return
                    elif check_tags(elem2, outputDict):
                        return
                    compteur = compteur + 1
                for elem in sortedList[slc+compteur:]:
                    if check_tags(elem, outputDict):
                        return
                for elem in reversed(sortedList[:max(0, slc-compteur)]):
                    if check_tags(elem, outputDict):
                        return



        
        extract_entries(self.tSorted, keys[0], outputDict)
        extract_entries(self.xSorted, keys[1], outputDict)
        extract_entries(self.ySorted, keys[2], outputDict)
        extract_entries(self.zSorted, keys[3], outputDict)
        return outputDict

    def find_entries(self, tags=[], keys=None,
                           sortCriteria=None, assumePositiveTime=False):

        """
        keys : a tuple of slices(float,float,None)
               slices values are bounds of a 4D cube in which are the
               requested data
               There must exactly be 4 slices in the tuple
        """
        
        outputDict = self.build_entry_dict(tags, keys, assumePositiveTime)
        
        res = [l[0] for l in outputDict.values() if len(l) == 4]
        if sortCriteria is not None:
            res.sort(key=sortCriteria)
        return res


    def find_bounds(self, tags=[], keys=None, assumePositiveTime=False):

        """
        keys : a tuple of slices(float,float,None)
               slices values are bounds of a 4D cube in which are the
               requested data
               There must exactly be 4 slices in the tuple
        """
        
        outputDict = self.build_entry_dict(tags, keys, assumePositiveTime)
        bounds = [Bounds(), Bounds(), Bounds(), Bounds()]
        for l in outputDict.values():
            if len(l) != 4:
                continue
            bounds[0].update(l[0].data.position.t)
            bounds[1].update(l[0].data.position.x)
            bounds[2].update(l[0].data.position.y)
            bounds[3].update(l[0].data.position.z)
        return bounds


class SpatializedDatabase:

    """
    SpatializedDatabase


    Methods
    -------
    find_entries(tags, keys, sortCriteria) -> list(SpbEntry,...):
        Method to search data, based on tags and space-time region.
        The space-time must be a tuple of slices (same format as keys in a
        __getitem__ method).

    find_bounds(tags, keys) -> list(nephelae.types.Bounds, ...):
        Similar to find_entries method but returns the bounding box for data
        with given tags and inside the space-time regien given by keys.
    """

    # class member functions #####################################

    def serialize(database):
        return pickle.dump(self)


    def unserialize(stream):
        return pickle.load(stream)

    
    def load(path):
        # Have to do it this way because pickle does not seems to copy
        # everything (investigate this)
        res = SpatializedDatabase()
        loaded = pickle.load(open(path, "rb"))
        res.taggedData  = loaded.taggedData
        res.orderedTags = loaded.orderedTags
        return res


    def save(database, path, force=False):
        if not force and os.path.exists(path):
            raise ValueError("Path \"" + path + "\" already exists. "
                             "Please delete the file, pick another path "
                             "or force overwritting with force=True")
        pickle.dump(database, open(path + '.part', "wb"))
        # this for not to erase the previously saved database in case of failure
        os.rename(path + '.part', path)


    # instance member functions #################################

    def __init__(self):
        self.saveTimer = None
        self.init_data()
   

    def init_data(self):
        self.taggedData = {'ALL': SpatializedList()}
        self.orderedTags       = ['ALL']
        self.lastTagOrdering   = -1
        self.tagOrderingPeriod = 1000


    def insert(self, entry):
        self.taggedData['ALL'].insert(entry)
        for tag in entry.tags:
            if tag not in self.taggedData.keys():
                self.taggedData[tag] = SpatializedList()
            self.taggedData[tag].insert(entry)
        self.check_tag_ordering()


    def best_search_list(self, tags=[]):
        if not tags:
            return self.taggedData['ALL']
        else:
            for tag in self.orderedTags:
                if tag in tags:
                    return self.taggedData[tag]
            return self.taggedData['ALL']
       

    def find_entries(self, tags=[], keys=None,
                           sortCriteria=None, assumePositiveTime=True):
        # Making sure we have a list of tags, event with one element
        if isinstance(tags, str):
            tags = [tags]
        return self.best_search_list(tags).find_entries(
                    tags, keys, sortCriteria, assumePositiveTime)
        


    def __getitem__(self, tags):
        """Syntactic sugar for self.find_entries"""
        class IndexHandler:
            def __init__(self, tags, database):
                self.tags               = tags
                self.database           = database
                self.sortCriteria       = None
                self.assumePositiveTime = True
            def __getitem__(self, keys):
                if isinstance(keys, slice) or isinstance(keys, (float, int)):
                    keys = (keys,)
                return self.database.find_entries(self.tags, keys,
                            self.sortCriteria, self.assumePositiveTime)
            def __call__(self, sortCriteria=None, assumePositiveTime=True):
                self.sortCriteria       = sortCriteria
                self.assumePositiveTime = assumePositiveTime
                return self
        return IndexHandler(tags, self)


    def find_bounds(self, tags=[], keys=None, assumePositiveTime=True):
        # Making sure we have a list of tags, event with one element
        if isinstance(tags, str):
            tags = [tags]
        return self.best_search_list(tags).find_bounds(tags, keys, assumePositiveTime)


    def last_entry(self, tag):
        """
        Takes a single tag as input and ouput the last entry for these tags.
        Is fast. (no search, direct read)
        """
        return self.taggedData[tag].tSorted[-1].data


    def __getstate__(self):
        return {'taggedData':self.taggedData}
  

    def __setstate__(self, deserializedData):
        self.init_data()
        self.taggedData = deserializedData['taggedData']
        self.check_tag_ordering()


    def enable_periodic_save(self, path, timerTick=60.0, force=False):
        if not force and os.path.exists(path):
            raise ValueError("Path \"" + path + "\" already exists. "
                             "Please delete the file, pick another path "
                             "or force overwritting with force=True")
        self.saveTimerTick = timerTick
        self.savePath      = path
        self.saveTimer = threading.Timer(self.saveTimerTick,
                                         self.periodic_save_do)
        self.saveTimer.start()


        
    def disable_periodic_save(self):
        if self.saveTimer is not None:
            self.periodic_save_do()
            self.saveTimer.cancel()
        self.saveTimer = None

    
    def periodic_save_do(self):
        SpatializedDatabase.save(self, self.savePath, force=True)
        if self.saveTimer is not None: # check if disable was called
            self.saveTimer = threading.Timer(self.saveTimerTick,
                                             self.periodic_save_do)
            self.saveTimer.start()

    
    def check_tag_ordering(self):
        if not 0 <= self.lastTagOrdering < self.tagOrderingPeriod:
            insertsSinceLinceLastTagOrdering = 0
            tags = []
            for tag in self.taggedData.keys():
                tags.append(SpbSortableElement(len(self.taggedData[tag]), tag))
            tags.sort()
            self.orderedTags = [tag.data for tag in tags]
        self.lastTagOrdering = self.lastTagOrdering + 1

