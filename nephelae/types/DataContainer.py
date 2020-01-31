import numpy as np
import bisect as bi
import copy

class TimedData:

    """
    TimedData

    Container aiming at shortening basic time series manipulations, from
    plotting to synchronization of data.
    """

    def from_database(database, tags, keys, name=None):
        entries = database[tags](sortCriteria=lambda x: x.position.t)[keys]
        if name is None:
            name = ''
            for tag in tags:
                name = name + ' ' + tag
            name = name[1:]
        return TimedData(np.array([entry.position.t for entry in entries]),
                         np.array([entry.data.data  for entry in entries]).squeeze(),
                         name)


    def __init__(self, time, data, name=''):
        self.name = name
        self.time = time
        self.data = data


    def copy(self, newName=None):
        cpy = copy.deepcopy(self)
        if newName is not None:
            cpy.name = newName
        return cpy


    def plot(self, axes, label=None, style='-'):
        if label is None:
            label = self.name
        axes.plot(self.time, self.data, style, label=label)


    def plot_instant(self, axes, flipTimes):
        amin = np.min(self.data)
        amax = np.max(self.data)
        
        t = [self.time[0]]
        d = [-1]
        for flip in flipTimes:
            t = t + [flip, flip]
            d = d + [d[-1], -1.0*d[-1]]
        t.append(self.time[-1])
        d.append(d[-1])
        d = 0.5*(amax - amin)*(1.0 + np.array(d)) + amin
        print("t :", t)
        print("d :", d)
        axes.plot(t, d)


    def sync_on(self, other):
        s = slice(bi.bisect_right(self.time, other.time[0]),
                  bi.bisect_left(self.time, other.time[-1]))
        
        self.data = np.interp(other.time, self.time[s], self.data[s])
        self.time = other.time




