import numpy as np

class PeriodicContainer:

    """ 
    PeriodicContainer : This class is a helper to access data in a numpy-like array where some dimensions are known to be periodic
    """

    def __init__(self, data, periodicDimension=[]):

        """
        PeriodicContainer constructor:
            - data               : numpy like array (must implement __getitem__ and shape)
            - periodicDimensions : list of dimension index to be handled as periodic
        """

        self.data = data
        self.shape = self.data.shape # not used in this class, inly for convenience
        self.periodicShape = list(self.data.shape) # -1 on periodic dimensions
        self.isPeriodic = np.array([False]*len(self.data.shape))
        for i in periodicDimension:
            self.isPeriodic[i] = True
            self.periodicShape[i] = -1
        self.periodicShape = tuple(self.periodicShape)
        self.outputShape = ()
        self.readTuples = []
        self.writeTuples = []

    def __getitem__(self, keys):
        """
        Implementation of operator []
        """
        self.__compute_read_write_tuples(self.__format_keys(keys))
        return self.get(self.outputShape, self.readTuples, self.writeTuples)


    def get(self, outputShape, readTuples, writeTuples):
        """
        get : data getter separated from __getitem__ to be able to read data using tuples from another PeriodicContainer for efficiency
        """
        # print("outputShape : ", outputShape)
        # print("readTuples  : ", readTuples)
        # print("writeTuples : ", writeTuples)

        res = np.empty(outputShape)
        for readIndex, writeIndex in zip(readTuples, writeTuples):
            res[writeIndex] = self.data[list(readIndex)]
        return res

    # private functions (for internal use only) #############################
    def __format_keys(self, keys):
        checkedKeys = []
        for i, key in enumerate(keys):

            if isinstance(key, slice):
                if key.start == None:
                    key_start = 0
                else:
                    key_start = key.start
                if key.stop == None:
                    key_stop = self.data.shape[i]
                else:
                    key_stop = key.stop
                key = slice(key_start, key_stop, key.step)

                if key.start > key.stop:
                    raise Exception("Error : slice must have positive length")

                if self.isPeriodic[i]: # if dim is periodic set key.start into shape bounds
                    t = self.data.shape[i] * (key.start // self.data.shape[i])
                    checkedKeys.append(slice(key.start - t, key.stop - t, key.step))
                else:
                    if key.start < 0 or key.start > self.data.shape[i]:
                        raise Exception("Error : index not inside shape")
                    if key.stop < 0 or key.stop > self.data.shape[i]:
                        raise Exception("Error : index not inside shape")
                    checkedKeys.append(key)
            else:
                if self.isPeriodic[i]:
                    key = key - self.data.shape[i] * (key // self.data.shape[i])
                else:
                    if key < 0 or key > self.data.shape[i]:
                        raise Exception("Error : index not inside shape")
                checkedKeys.append(slice(key, key + 1, None))

        return tuple(checkedKeys)

    def __compute_read_write_tuples(self, keys):
        shape = []
        for key in keys:
            shape.append(key.stop - key.start)
        self.outputShape = tuple(shape)

        readTuples  = []
        writeTuples = []
        for key, readDimLen, writeDimLen in zip(keys, self.data.shape, self.outputShape):

            Ntuples = 1 + (key.stop - 1) // readDimLen

            rtuples = []
            if Ntuples <= 1:
                rtuples = [key]
            else:
                rtuples = [slice(0, readDimLen)] * (Ntuples - 2)
                rtuples.insert(0, slice(key.start, readDimLen))
                rtuples.append(slice(0, (key.stop - 1) % readDimLen + 1))
            index0 = 0
            wtuples = []
            for tu in rtuples:
                wtuples.append(slice(index0, index0 + tu.stop - tu.start))
                index0 += tu.stop - tu.start

            readTuples.append(rtuples)
            writeTuples.append(wtuples)
        
        self.readTuples  = PeriodicContainer.__expandTuples(readTuples)
        self.writeTuples = PeriodicContainer.__expandTuples(writeTuples)
        
    def __expandTuples(tuples):
        out = []
        if len(tuples) <=  1:
            for tu in tuples[0]:
                out.append((tu,))
        else:
            others = PeriodicContainer.__expandTuples(tuples[1:])
            for tu0 in tuples[0]:
                for tu1 in others:
                    out.append((tu0,) + tu1)
        return out



