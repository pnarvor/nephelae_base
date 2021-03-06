import threading
import time
import pickle
import os

from nephelae.types import NavigationRef
from nephelae.types import Position
from nephelae.types import SensorSample
from nephelae.types import MultiObserverSubject

from .SpatializedDatabase import SpatializedDatabase
from .SpatializedDatabase import SpbEntry


class NephelaeDataServer(SpatializedDatabase):

    """NephelaeDatabase

    SpatializedDatabase specialization for Nephelae project

    /!\ Find better name ?

    """

    def load(path):
        # Have to do it this way because pickle does not seems to copy
        # everything (investigate this) Not a proper initialization
        loaded = pickle.load(open(path, "rb"))
        res = NephelaeDataServer()
        res.taggedData    = loaded.taggedData
        res.orderedTags   = loaded.orderedTags
        res.navFrame      = loaded.navFrame
        res.uavIds        = loaded.uavIds
        res.variableNames = loaded.variableNames
        return res


    def __init__(self):
        super().__init__() 

        self.navFrame      = NavigationRef()
        self.observerSet   = MultiObserverSubject(['add_gps', 'add_sample', 'add_status'])
        self.uavIds        = []
        self.variableNames = []
        self.dataLock      = threading.Lock()
       

    def set_navigation_frame(self, navFrame):
        self.navFrame = navFrame


    def add_gps(self, gps):
        self.observerSet.add_gps(gps) # mutex protected
        if self.navFrame is None:
            return
        uavId = str(gps.uavId)
        tags=[uavId, 'GPS']
        with self.dataLock:
            if uavId not in self.uavIds:
                self.uavIds.append(uavId)
            self.insert(SpbEntry(gps, gps - self.navFrame, tags))


    def add_status(self, status):
        self.observerSet.add_status(status) # mutex protected
        uavId = status.aircraftId
        tags=[uavId, 'STATUS']
        with self.dataLock:
            if uavId not in self.uavIds:
                self.uavIds.append(uavId)
            self.insert(SpbEntry(status, status.position, tags))
        

    def add_sample(self, sample):
        # sample assumed to comply with nephelae_base.types.sensor_sample
        self.observerSet.add_sample(sample) # mutex protected
        if self.navFrame is None:
            return
        tags=[str(sample.producer),
              str(sample.variableName),
              'SAMPLE']
        with self.dataLock:
            self.insert(SpbEntry(sample, sample.position, tags))
            if str(sample.variableName) not in self.variableNames:
                self.variableNames.append(str(sample.variableName))


    def add_gps_observer(self, observer):
        self.observerSet.attach_observer(observer, 'add_gps')
    def remove_gps_observer(self, observer):
        self.observerSet.detach_observer(observer, 'add_gps')


    def add_sensor_observer(self, observer):
        self.observerSet.attach_observer(observer, 'add_sample')
    def remove_sensor_observer(self, observer):
        self.observerSet.detach_observer(observer, 'add_sample')


    def add_status_observer(self, observer):
        self.observerSet.attach_observer(observer, 'add_status')
    def remove_status_observer(self, observer):
        self.observerSet.detach_observer(observer, 'add_status')


    def __getstate__(self):
        serializedItems = {}
        serializedItems['navFrame']      = self.navFrame
        serializedItems['uavIds']        = self.uavIds
        serializedItems['variableNames'] = self.variableNames
        serializedItems['data']          = super().__getstate__()
        return serializedItems
  

    def __setstate__(self, data):
        try:
            self.navFrame = data['navFrame']
            if 'uavIds' in data.keys():
                self.uavIds = data['uavIds']
            else:
                self.uavIds = []
            if 'variableNames' in data.keys():
                self.variableNames = data['variableNames']
            else:
                self.variableNames = []
            super().__setstate__(data['data'])
        except Exception as e:
            print("Exception happenned during database load."
                  "File is probably corrupted or is of an older version.")
            raise e


    def save_ascii(self, path, force=False):
        from progressbar import progressbar
        if not force and os.path.exists(path):
            raise ValueError("Path \"" + path + "\" already exists. "
                             "Please delete the file, pick another path "
                             "or force overwritting with force=True")
        print("Saving ascii data base to ", path, ' ...', flush=True)
        with open(path, 'w') as f:
            f.write(self.navFrame.one_line_str() + '\n')
            # data = [e.data for e in self['ALL'](sortCriteria=lambda x: x.position.t)[:]]
            data = [e.data.data for e in self.taggedData['ALL'].tSorted]
            for idx, datum in zip(progressbar(range(len(data))), data):
                f.write(datum.one_line_str() + '\n')



class DatabasePlayer(NephelaeDataServer):

    """DatabasePlayer
    
    Class to replay messages stored in a NephelaeDataServer save.
    
    As a subclass of NephelaeDataServer it can be used as a dataserver for
    mapping and inteface testing.

    """

    def __init__(self, databasePath, timeFactor=1.0, granularity=0.005):
        super().__init__()
        
        self.origin       = SpatializedDatabase.load(databasePath)
        self.timeFactor   = timeFactor
        self.granularity  = granularity
        self.running      = False
        self.currentTime  = 0.0
        self.replayData   = []
        self.replayThread = None
        self.replayLock   = threading.Lock()
        self.looped       = False

        self.set_navigation_frame(self.origin.navFrame)


    def play(self, looped=False):
        if not self.running:
            self.looped = looped
            self.restart()
        else:
            print("Replay already running.",
                  "Call 'restart' if you want to start it again")

    def stop(self):
        if self.running and self.replayThread is not None:
            print("Stopping replay... ", end='')
            self.looped  = False
            self.running = False
            self.replayThread.join()
            print("Done.")


    def restart(self):
        if self.running:
            self.init_replay()
        else:
            self.replayThread = threading.Thread(target=self.run)
            self.replayThread.start()


    def init_replay(self):
        with self.replayLock:
            self.currentTime = 0.0
            sourceList = self.origin.taggedData['ALL'].tSorted
            self.replayData = [entry for entry in sourceList]

    
    def run(self):
        self.init_replay()
        lastTime = time.time()
        self.running = True
        while self.running and self.replayData:
            with self.replayLock:
                ellapsed = time.time() - lastTime
                self.currentTime = self.currentTime + self.timeFactor*ellapsed
                while self.replayData[0].index <= self.currentTime:
                    self.process_replayed_entry(self.replayData[0].data)
                    self.replayData.pop(0)
                    if not self.replayData:
                        break

            lastTime = lastTime + ellapsed
            time.sleep(self.granularity)
        self.running = False
        if self.looped:
            self.init_data()
            self.restart()


    def process_replayed_entry(self, entry):
        if 'GPS' in entry.tags: 
            self.add_gps(entry.data)
        elif 'SAMPLE' in entry.tags:
            self.add_sample(entry.data)
        else:
            raise ValueError("No GPS or SAMPLE tag found in entry."+
                             "Are you using a valid database ?")



