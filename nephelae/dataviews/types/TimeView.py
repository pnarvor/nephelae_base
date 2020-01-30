from .DataView import DataView

class TimeView(DataView):

    """
    TimeView
    
    Handle time keys the same way as numpy arrays. (negative time fetch at the
    end of the data structure). Also sort data with respect to time.
    """

    def __init__(self, parents=[]):
        super().__init__(parents)

        self.currentTime = None

    
    def __getitem__(self, keys):
        """
        Will fetch data from parent DataViews, concatenate and process them
        before returning them.
        """
        if isinstance(keys, (slice, float, int)):
            keys = (keys,)
        keys = list(keys)
        while len(keys) <= 4:
            keys.append(slice(None))
        newKeys = (self.process_time_key(keys[0]), keys[1], keys[2], keys[3])
        output = super().__getitem__(newKeys)
        output.sort(key=lambda x: x.position.t)
        return output


    def process_notified_sample(self, sample):
        self.currentTime = sample.position.t
        return sample


    def process_time_key(self, key):
        """Helper key format function of the time key"""
        if self.currentTime is None:
            return slice(None)
        if not isinstance(key, (slice, int, float)):
            raise ValueError("key must be a slice or a scalar (int or float)")
        if isinstance(key, slice):
            if key.start is None:
                key_start = None
            elif key.start < 0.0:
                key_start = self.currentTime + key.start
            else:
                key_start = key.start
            if key.stop is None:
                key_stop = None
            elif key.stop < 0.0:
                key_stop = self.currentTime + key.stop
            else:
                key_stop = key.stop
            return slice(key_start, key_stop)
        else:
            if key < 0:
                return self.currentTime + key.stop
            else:
                return key

