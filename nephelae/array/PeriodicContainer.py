import numpy as np

class PeriodicContainer:

    """ 
    PeriodicContainer
    
    Helper class to ease access to an array with data known periodic on 
    some dimensions.

    Example:

    Let array0 be a numpy.array of size 10x20 with periodic data on the first
    dimension. Then with array1 = PeriodicContainer(array0, periodicDimensions=[0]),
    one can access array0 data in the same way as using directly the  array0
    variable, but with the first dimension seemingly infinite. For example :

        data = array0[5:15,:]

    would raise an exception because array0.shape[0] = 10, but :

        array1 = PeriodicContainer(array0, periodicDimensions=[0])
        data   = array1[5:15,:]

    becomes a valid expression. The PeriodicContainer class automatically
    traduce

        data = array0[5:15,:]

    into

        data0 = array0[5:,:]
        data1 = array0[:(15 % array0.shape[0]),:]
        data = [data0, data1]

    As a result, any indexes used to access a periodic dimension is valid.

    This classes can handle an array with arbitrary number of dimensions.

    Attributes
    ----------

    data : numpy.array (or equivalent)
        The original data array in which some dimensions are periodic.

    shape : tuple(int), (to be removed ?)
        Original shape of the array.

    periodicShape : tuple(int)
        Same as self.shape, but with -1 on periodicDimensions.

    isPeriodic : tuple(bool)
        Element is true if dimension is periodic.
    """

    def __init__(self, data, periodicDimension=[]):

        """
        PeriodicContainer constructor:
            - data               : numpy like array (must implement __getitem__ and shape)
            - periodicDimensions : list of dimension index to be handled as periodic
        """

        self.data = data
        self.shape = self.data.shape # not used in this class, inly for convenience
        self.periodicShape = list(self.data.shape)
        self.isPeriodic = np.array([False]*len(self.data.shape))
        # Will set -1 on periodic dimensions
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
            # print("res shape :",  res[writeIndex].shape)
            # print("data shape :", self.data[list(readIndex)].shape)
            # print("read index  :", readIndex)
            # print("write index :", writeIndex)
            res[writeIndex] = self.data[readIndex]
        return res

    # private functions (for internal use only) #############################
    def __format_keys(self, keys):

        # output of this function is a tuple of slices (no single index)

        keys = list(keys)
        while len(keys) < len(self.data.shape):
            keys.append(slice(None))

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
        
        self.readTuples  = PeriodicContainer.__remove_unit_slices(PeriodicContainer.__expandTuples(readTuples))
        self.writeTuples = PeriodicContainer.__remove_unit_slices(PeriodicContainer.__expandTuples(writeTuples))
        
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


    def __remove_unit_slices(tuples):
        out = []
        for keys in tuples:
            newKeys = []
            for key in keys:
                if key.stop - key.start == 1:
                    newKeys.append(key.start)
                else:
                    newKeys.append(key)
            out.append(tuple(newKeys))
        return out
