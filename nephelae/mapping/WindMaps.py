import numpy as np
from sklearn.gaussian_process import kernels as gpk

from nephelae.types import Bounds

from .MapInterface import MapInterface
from .GprPredictor import GprPredictor
from .GprKernel    import WindKernel

class WindMapConstant(MapInterface):

    """WindConstant
    
    Constant wind predictor.
    
    Will output the same value at every point in space.
    """

    def __init__(self, variableName, wind=[0.0,0.0],
                 resolution=[50.0,50.0,50.0,50.0]):
        super().__init__(variableName)
        self.wind = wind
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


    def computes_stddev(self):
        return False


class WindMapUav(GprPredictor):

    """WindMapUav
    
    Wind maps base on measurements from 
    """

    # def __init__(self, dataServer, lengthScales=[60.0, 300.0, 300.0, 30.0],
    def __init__(self, dataServer, lengthScales=[60.0, 300.0, 300.0, 30.0],
                 variance=5.0**2, noiseVariance=1.0):
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
        
