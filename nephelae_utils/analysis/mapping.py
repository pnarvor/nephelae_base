import numpy as np

from nephelae.types           import DeepcopyGuard
from nephelae.mapping         import GprPredictor, ValueMap, StdMap, WindKernel, WindMapConstant
from nephelae.dataviews.types import CloudSensorProcessing


def setup_map_generator(database, lengthScales, variance, noiseVariance, wind, alpha, beta, scaling):
    
    # Object which is in charge of giving the wind to the gpr kernel.
    windServer = WindMapConstant('WindServer', wind)
    
    # Kernel to use in the gpr
    params = {}
    params['lengthScales']  = lengthScales
    params['variance']      = variance
    params['noiseVariance'] = noiseVariance

    shallowParams = {} # this is because of sklean clone function
    shallowParams['windMap'] = windServer
    params['shallowParameters'] = DeepcopyGuard(**shallowParams)
    kernel  = WindKernel(**params)

    print(type(kernel.windMap))

    # Object in charge of fetch cloud sensor data and voltage data from the
    # database and giving to the gpr calibrated sensor data.
    cloudView = CloudSensorProcessing("Cloud data", database,
                                      "cloud_channel_0", "energy",
                                      alpha, beta, scaling)

    # The object in charge of all gpr calculations.
    gpr = GprPredictor("Cloud Map estimator", cloudView, kernel)
    gpr.computeStd = True

    return gpr
    

