import numpy as np
import bisect as bi
import copy

class TimedData:

    """
    TimedData

    Container aiming at shortening basic time series manipulations, from
    plotting to synchronization of data.
    """

    def from_database(database, tags, keys=(slice(None),), name=None,
                      dataFetchFunc=lambda e: e.data.data):
        entries = database[tags](sortCriteria=lambda x: x.position.t)[keys]
        if name is None:
            name = ''
            for tag in tags:
                name = name + ' ' + tag
            name = name[1:]
        return TimedData(np.array([entry.position.t     for entry in entries]),
                         np.array([dataFetchFunc(entry) for entry in entries]).squeeze(),
                         name,
                         np.array([[entry.position.x,entry.position.y,entry.position.z] for entry in entries]))


    def __init__(self, time, data, name='unnamed', position=None):
        self.name = name
        self.time = time
        self.data = data
        self.position = position


    def crop(self, key):
        if isinstance(key, slice):
            if key.start is None:
                key_start = 0
            else:
                key_start = key.start
            if key.stop is None:
                key_stop = len(self.time)
            else:
                key_stop = key.stop
            s = slice(bi.bisect_right(self.time, key_start),
                      bi.bisect_left(self.time, key_stop))
            # return self.data[s]
            self.time = self.time[s]
            self.data = self.data[s]
            if self.position is not None:
                self.position = self.position[(s, slice(None),)]
            return self
        elif isinstance(key, (list, tuple)):
            self.crop(slice(key[0], key[-1]))
        else:
            raise ValueError("Invalid key type for croping (must be a slice)")
        
    
    def position_at_time(self, t):
            return self.position[bi.bisect_left(self.time, t), :]

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.start is None:
                key_start = 0
            else:
                key_start = key.start
            if key.stop is None:
                key_stop = len(self.time)
            else:
                key_stop = key.stop
            s = slice(bi.bisect_right(self.time, key_start),
                      bi.bisect_left(self.time, key_stop))
            return self.data[s]
        elif isinstance(key, (float, int)):
            return self.data[bi.bisect_left(self.time, key)]
        else:
            raise ValueError("Invalid key type")



    def copy(self, newName=None):
        cpy = copy.deepcopy(self)
        if newName is not None:
            cpy.name = newName
        return cpy


    def plot(self, axes, label=None, style='-'):
        if label is None:
            label = self.name
        axes.plot(self.time, self.data, style, label=label)
        axes.grid()
        axes.set_xlabel("Time (s)")


    def plot_east(self, axes, label=None, style='-'):
        if label is None:
            label = self.name + '_east'
        axes.plot(self.time, self.position[:,0], style, label=label)
        axes.grid()
        axes.set_xlabel("Time (s)")


    def plot_north(self, axes, label=None, style='-'):
        if label is None:
            label = self.name + '_north'
        axes.plot(self.time, self.position[:,1], style, label=label)
        axes.grid()
        axes.set_xlabel("Time (s)")


    def plot_alt(self, axes, label=None, style='-'):
        if label is None:
            label = self.name + '_alt'
        axes.plot(self.time, self.position[:,2], style, label=label)
        axes.grid()
        axes.set_xlabel("Time (s)")


    def plot_position(self, axes, label=None, style='-'):
        if label is None:
            label = self.name + '_pos'
        axes.plot(self.position[:,0], self.position[:,1], style, label=label)
        axes.grid()
        axes.set_xlabel("East (m)")
        axes.set_ylabel("North (m)")
        


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
        axes.plot(t, d)


    def sync_on(self, other):
        s = slice(bi.bisect_right(self.time, other.time[0]),
                  bi.bisect_left(self.time, other.time[-1]))
        
        self.data = np.interp(other.time, self.time[s], self.data[s])
        self.time = other.time




