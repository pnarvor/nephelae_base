import numpy as np
from sklearn.gaussian_process import kernels as gpk

from nephelae.types import Bounds

from .MapInterface import MapInterface
from .GprPredictor import GprPredictor
from .GprKernel    import WindKernel

class WindMapConstant(MapInterface):

    """WindMapConstant
    Derived from nephelae.mapping.MapInterface

    Returns a identical fixed wind value at each location.

    """

    def __init__(self, name, wind=[0.0,0.0],
                 resolution=[50.0,50.0,50.0,50.0], threshold=0):
        super().__init__(name, threshold=threshold)
        self.wind  = np.array(wind)
        self.resol = resolution


    def at_locations(self, locations):
        return np.array([self.wind]*locations.shape[0])


    def shape(self):
        return (None,None,None,None)


    def span(self):
        return (None,None,None,None)


    def bounds(self):
        return (None,None,None,None)


    def resolution(self):
        return self.resol


    def sample_size(self):
        return len(self.wind)

    def get_wind(self):
        return self.wind

class WindObserverMap(WindMapConstant):

    """
    WindObserverMap

    Will ouput a single wind value for all location. This wind value
    is computed from received data from Observable objects such as PprzUav
    or a database.

    In the absence of data, default 

    Attritubes
    ----------
    wind : np.array (shape=(2,)), inherited from WindMapConstant
        Current wind value, average of fetched wind samples. (Default is [0,0])
    
    sampleName : str
        Name of the sample to be kept when add_sample is called. (add_sample
        will receive all kinds of sample types. This is to filter the samples)
        Default is str(['UT','VT'])

    windSamples : list(np.array,...)
        List of wind measurements. Will be averaged to give a single wind
        value for all space.

    maxSamples : int
        Maximum number of samples to be kept in self.windSamples. When reached,
        oldest samples will be deleted until len(self.windSamples) equals
        self.minSamples.

    minSamples : int
        Length at which windSample will be set when self.maxSamples is reached

    Methods
    -------
    add_sample(nephelae.types.SensorSample):
        Callback function to be registered in a publisher.
    """

    def __init__(self, name, sampleName=str(['UT','VT']),
                 defaultWindValue=np.array([0.0,0.0]),
                 maxSamples=30, minSamples=5,
                 resolution=[50.0,50.0,50.0,50.0], threshold=0):
        super().__init__(name, defaultWindValue, resolution, threshold=threshold)

        self.sampleName  = sampleName
        self.windSamples = []
        self.maxSamples  = maxSamples
        self.minSamples  = minSamples


    def add_sample(self, sample):
        """Callback function to be registered in a publisher."""
        if sample.variableName != self.sampleName:
            return

        if not self.windSamples:
            # If wind sample is empty, this is the first sample we receive.
            # Setting self.wind to this value is better than default.
            self.wind = sample.data[0]

        self.windSamples.append(sample.data[0])
        if len(self.windSamples) >= self.maxSamples:
            # Updating wind only when maxSamples is reached
            # To update at each sample, set maxSamples-minSamples=1
            self.wind = np.array(self.windSamples).mean(axis=0)
            # Removing old data
            self.windSamples[0:len(self.windSamples) - self.minSamples] = []


class WindMapUav(GprPredictor):

    """WindMapUav
    /!\ NOT FULLY IMPLEMENTED. DO NOT USE THIS.
    Derived from nephelae.mapping.MapInterface.

    Returns a predicted wind value based on measure fetch from a database and
    GPR prediction.

    /!\ NOT FULLY IMPLEMENTED. DO NOT USE THIS.
    """

    # def __init__(self, dataServer, lengthScales=[60.0, 300.0, 300.0, 30.0],
    def __init__(self, dataServer, lengthScales=[60.0, 300.0, 300.0, 30.0],
                 variance=5.0**2, noiseVariance=1.0):
        raise NotImplemented("I told you not to use this !!! (WindMapUav")
        super().__init__("H_Wind", dataServer, str(['UT','VT']),
            WindKernel(lengthScales, variance, noiseVariance, WindMapConstant('CH_Wind')),
            computesStddev=False, updateRange=False)


    def at_locations(self, locations):
        res = super().at_locations(locations).mean(axis=0)
        print("Horizontal wind :", res)
        return np.array([res]*len(locations))


    def __deepcopy__(self, memo):
        # find a better way ! This is to prevent scikit-lear to deepcppy the whole database
        # print("WindMapUav was deepcopied !\n\n\n\n\n\n")
        return self
        
