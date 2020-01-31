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

    def __init__(self, name, database, searchTagsCloud, searchTagsEnergy,
                 alpha=1.0, beta=0.0, scaling=1.0, lengthMedian=3):
        """
        searchTags : list(str, ...)
            tags to search data in the database.
        """
        super().__init__(name, database, searchTagsCloud)

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

        self.medianCache = []
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


            cloudSamples = copy.deepcopy([e.data for e in
                self.database[self.searchTagsCloud](sortCriteria=lambda x: x.position.t)[keys]])
            if len(cloudSamples) < 1:
                return []
            cloud =  TimedData(np.array([s.position.t for s in cloudSamples]),
                               np.array([s.data[0]  for s in cloudSamples]))

            # Getting battery voltage samples
            energySamples = copy.deepcopy([e.data for e in
                self.database[self.searchTagsEnergy](sortCriteria=lambda x: x.position.t)[keys]])
            if len(energySamples) < 1:
                return []
            voltage =  TimedData(np.array([s.position.t for s in energySamples]),
                                 np.array([s.data[1]    for s in energySamples]))
            voltage.sync_on(cloud)
            
            medianFiltered = medfilt(cloud.data, self.lengthMedian)
            if len(medianFiltered) < self.lengthMedian:
                self.medianCache = medianFiltered.tolist()
            else:
                self.medianCache = medianFiltered[-self.lengthMedian:].tolist()

            output = (medianFiltered - self.alpha*voltage.data - self.beta) / self.scaling
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
                self.medianCache.append(sample.data[0])
                if len(self.medianCache) > self.lengthMedian:
                    self.medianCache = self.medianCache[-self.lengthMedian:]
                sample.data[0] = (median(self.medianCache) - self.alpha*self.lastVoltage - self.beta) / self.scaling
            return sample

        if all([tag in sampleTags for tag in self.searchTagsEnergy]):
            # Got an energy sample saving the value
            with self.lock:
                self.lastVoltage = sample.data[1]
        else:
            return None

        


