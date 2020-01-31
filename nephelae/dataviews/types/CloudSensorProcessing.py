import copy
import numpy as np
import bisect as bi
import threading
from scipy.signal import medfilt 
from statistics   import median

from nephelae.types import TimedData

from .DatabaseView import DatabaseView

class CloudSensorProcessing(DatabaseView):

    """
    CloudSensorProcessing
    
    Have to be a database view because must catch also the energy message.
    """

    parameterNames = ['lengthMedian', 'alpha', 'beta', 'scaling']

    def __init__(self, database, searchTagsCloud, searchTagsEnergy,
                 alpha=1.0, beta=0.0, scaling=1.0, lengthMedian=3):
        """
        searchTags : list(str, ...)
            tags to search data in the database.
        """
        super().__init__()

        self.alpha        = alpha
        self.beta         = beta
        self.scaling      = scaling
        self.lengthMedian = lengthMedian

        self.database         = database
        self.searchTagsCloud  = searchTagsCloud
        self.searchTagsEnergy = searchTagsEnergy
        self.lock             = threading.Lock()

        # subscribing to database
        self.database.add_sensor_observer(self)

        self.currentMedianCache = []
        self.lastVoltage        = None


    def __getitem__(self, keys):
        """
        Fetch and return data from the database.
        """
        # find_entries is expecting a tuple. If only one set of indices were
        # given between the brackets, keys is not a tuple.
        if isinstance(keys, (slice, float, int)):
            keys = (keys,)
        
        with self.lock:
            self.lengthMedian = int(self.lengthMedian)
            # cloud   = TimedData.from_database(self.database, self.searchTagsCloud, keys)
            cloudSamples = copy.deepcopy([e.data for e in
                self.database[self.searchTagsCloud](sortCriteria=lambda x: x.position.t)[keys]])
            cloud =  TimedData(np.array([s.position.t for s in cloudSamples]),
                               np.array([s.data[0]  for s in cloudSample]))
            voltage = np.deepcopy(TimedData.from_database(self.database, 
                                                          self.searchTagsEnergy, keys))
            voltage.data = voltage.data[:,1]
            voltage.sync_on(cloud)
            
            medianFiltered = medfilt(cloud.data, self.lengthMedian)
            if len(medianFiltered) < self.lengthMedian:
                self.currentMedianCache = medianFiltered.tolist()
            else:
                self.currentMedianCache = medianFiltered[-self.lengthMedian]

            output = (medianFiltered - self.alpha*voltage.data - self.beta) / self.scale
            for value, sample in zip(output, cloudSamples):
                sample.data[0] = value
            return cloudSamples


    
    def process_notified_sample(self, sample):
        sampleTags = [sample.producer, sample.variableName, 'SAMPLE']
        # if not all self.tag are in sample tags, ignore this sample
        if all([tag in sampleTags for tag in self.searchTagsCloud]):
            # got a cloud sensor sample
            with self.lock:
                if self.lastVoltage == None:
                    return None
                self.lengthMedian = int(self.lengthMedian)
                sample = copy.deepcopy(sample)
                self.currentMedianCache.append(sample.data[0])
                if len(self.currentMedianCache) > self.lengthMedian:
                    self.currentMedianCache = self.currentMedianCache[-self.lengthMedian:]
                sample.data[0] = (median(self.currentMedianCache) - self.alpha*self.lastVoltage - self.beta) / self.scale

        if all([tag in sampleTags for tag in self.searchTagsEnergy]):
            # Got an energy sample saving the value
            with self.lock:
                self.lastVoltage = sample.data[1]
        else:
            return None


        


