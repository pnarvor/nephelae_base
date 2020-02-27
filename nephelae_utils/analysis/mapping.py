import numpy as np

from nephelae.types           import DeepcopyGuard
from nephelae.mapping         import GprPredictor, ValueMap, StdMap, WindKernel, WindMapConstant
from nephelae.dataviews.types import CloudSensorProcessing, DataView


def setup_map_generator(database, aircrafts, lengthScales, variance, noiseVariance, wind):
    
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

    # Objects in charge of fetch cloud sensor data and voltage data from the
    # database and giving to the gpr calibrated sensor data.
    cloudViews = []
    for aircraft, params in aircrafts.items():
        cloudViews.append(CloudSensorProcessing("Cloud data " + aircraft, database,
                                                [aircraft, "cloud_channel_0"], 
                                                [aircraft, "energy"],
                                                params['alpha'], params['beta'], params['scaling']))
    # Aggregating the output of these view to a single one for the gpr
    cloudView = DataView("Cloud data", parents=cloudViews)

    # The object in charge of all gpr calculations.
    gpr = GprPredictor("Cloud Map estimator", cloudView, kernel)
    gpr.computeStd = True

    return gpr
    

