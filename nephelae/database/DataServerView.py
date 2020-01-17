from nephelae.types import MultiObserverSubject

from .NephelaeDataServer import NephelaeDataServer

class DataServerView:

    """
    DataServerView

    This class is a read-only access to a NephelaeDataServer object. Its role
    is to serve as an interface between the database and the data consumers.

    """

    def __init__(self, database):
        self.database = database
        self.observerSet   = MultiObserverSubject(
            ['add_gps', 'add_sample', 'add_status'])

        self.database.add_gps_observer(self)
        self.database.add_sensor_observer(self)
        self.database.add_status_observer(self)


    def __getitem__(self, tags):
        return self.database[tags]


    def add_gps(self, gps):
        self.observerSet.add_gps(gps)
    def add_gps_observer(self, observer):
        self.observerSet.attach_observer(observer, 'add_gps')
    def remove_gps_observer(self, observer):
        self.observerSet.detach_observer(observer, 'add_gps')


    def add_sample(self, sample):
        self.observerSet.add_sample(sample)
    def add_sensor_observer(self, observer):
        self.observerSet.attach_observer(observer, 'add_sample')
    def remove_sensor_observer(self, observer):
        self.observerSet.detach_observer(observer, 'add_sample')


    def add_status(self, status):
        self.observerSet.add_status(status)
    def add_status_observer(self, observer):
        self.observerSet.attach_observer(observer, 'add_status')
    def remove_status_observer(self, observer):
        self.observerSet.detach_observer(observer, 'add_status')


class DataServerTaggedView(DataServerView):
    
    """
    DataServerTaggedView

    A view only taking spacial keys to fetch data from the database. Search
    tags, are given as initialization parameters.
    """

    def __init__(self, database, tags, defaultSortCriteria=None,
                       assumePositiveTime=True):
        super().__init__(database)
        
        self.tags                = tags
        self.defaultSortCriteria = defaultSortCriteria
        self.assumePositiveTime  = assumePositiveTime


    def __call__(self, sortCriteria=None, assumePositiveTime=True):
        class OptionsHandler:
            def __init__(self, database, tags,
                               sortCriteria, assumePositiveTime):
                self.database           = database
                self.tags               = tags
                self.sortCriteria       = sortCriteria
                self.assumePositiveTime = assumePositiveTime
            def __getitem__(self, keys):
                if isinstance(keys, slice) or isinstance(keys, (float, int)):
                    keys = (keys,)
                return self.database.find_entries(self.tags, keys,
                            self.sortCriteria, self.assumePositiveTime)
        if sortCriteria is None:
            sortCriteria = self.defaultSortCriteria
        if assumePositiveTime is None:
            assumePositiveTime = self.assumePositiveTime
        return OptionsHandler(self.database, self.tags,
                              sortCriteria, assumePositiveTime)


    def __getitem__(self, keys):
        if isinstance(keys, slice) or isinstance(keys, (float, int)):
            keys = (keys,)
        return self.database.find_entries(self.tags, keys,
                    self.defaultSortCriteria, self.assumePositiveTime)



                
