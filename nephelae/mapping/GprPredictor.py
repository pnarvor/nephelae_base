import numpy as np
import threading
from sklearn.gaussian_process import GaussianProcessRegressor

from nephelae.array import ScaledArray
from nephelae.types import Bounds
from nephelae.mapping import MapInterface

class GprPredictor(MapInterface):

    """
    GprPredictor

    Computes dense maps using sparse samples, using Gaussian Process Regression.
    Base on scikit-learn GPR library.

    /!\ Kernel parameters optimisation is not currently supported !

    Attributes
    ----------
    database : nephelae.database.NephelaeDataServer
        Data server from which fetch data to build the map.

    databaseTags : list(str,...)
        Tags used to retrieve from the database relevant data to build the map.

    kernel : sklearn.gaussian_process.kernel.Kernel derived type
        Kernel used in GPR. See here for more details :
        https://scikit-learn.org/stable/modules/classes.html#module-sklearn.gaussian_process

    gprProc : sklearn.gaussian_process.GaussianProcessRegressor
        Class doing the GPR computation. (Not used here. Trouble updating
        data inside this class. Is re-build each time. TODO : debug this)

    lock : threading.Lock
        Simple mutex to allow only one map computation at a time in
        self.compute_maps method. self.compute_maps will return None if busy.

    cache : 3-tuple
        Contains locations, computed Values and Stds maps of given locations.

    Methods
    -------

    at_locations(locations):
        Computes predicted value at each given location using GPR.
        This method is used in the map interface when requesting a dense map.
        When requesting a dense map, each location must be the position of
        on pixel of the requested map.

    See nephelae.mapping.MapInterface for other methods.
    """

    def __init__(self, database, databaseTags, kernel):

        """
        name : str
            Name of the computed map. Must be unique.

        database (nephelae_mapping.database):
            database from which fetch the relevant data for map computation.

        databaseTags : list(str, ...)
            tags for searching data in the database.

        kernel : sklearn.gaussian_process.kernel.Kernel derived type
            Kernel used in GPR.
        """
        self.database       = database
        self.databaseTags   = databaseTags
        self.kernel         = kernel
        self.gprProc = GaussianProcessRegressor(self.kernel,
                alpha=0.0,
                optimizer=None,
                copy_X_train=False)
        self.cache          = None
        self.keys           = None
        self.locationsLock  = threading.Lock()
        self.getItemLock    = threading.Lock()
        self.computeStd     = False
    def at_locations(self, locations):

        """Computes predicted value at each given location using GPR.

        This method is used in the map interface when requesting a dense map.
        When requesting a dense map, each location must be the position of
        on pixel of the requested map.

        This method automatically fetch relevant data from self.database
        to compute the predicted values.

        Parameters
        ----------
        locations : numpy.array (N x 4)
            Locations N x (t,x,y,z) for each of the N points where to compute
            a predicted value using GPR. 
            Note : this implementation of GprPredictor does not enforce the
            use of a 4D space (t,x,y,z) for location. However, the
            self.database attribute is most likely a
            nephelae.database.NephelaeDataServer type, which enforce the
            use of a 4D (t,x,y,z) space.

        Returns : numpy.array (N x M)
            Predicted values at locations. Can be more than 1 dimensional
            depending on the data fetched from the database.
            Example : If the database contains samples of 2D wind vector.
            The samples are 2D. The predicted map is then a 2D field vector
            defined on a 4D space-time.

        Note : This method probably needs more refining.
        (TODO : investigate this)
        """
        with self.locationsLock:
            kernelSpan = self.kernel.span()[0]
            locBounds = Bounds(locations[0,0], locations[-1,0])

            locBounds.min = locBounds.min - kernelSpan
            locBounds.max = locBounds.max + kernelSpan
            samples = [entry.data for entry in \
                    self.database[self.databaseTags]\
                    (assumePositiveTime=False)\
                    [locBounds.min:locBounds.max]]
            
            if len(samples) < 1:
                 return (np.ones((locations.shape[0], 1))*self.kernel.mean,
                        np.ones(locations.shape[0])*self.kernel.variance)

            else:
                trainLocations =\
                    np.array([[s.position.t,\
                    s.position.x,\
                    s.position.y,\
                    s.position.z]\
                    for s in samples])
                trainValues = np.array([s.data for s in samples]).squeeze()
                if len(trainValues.shape) < 2:
                    trainValues = trainValues.reshape(-1,1)
                
                
                # Code optimisation, still in beta
                
                boundingBox = ((np.min(trainLocations[:,1]),
                    np.min(trainLocations[:,2])), (np.max(trainLocations[:,1]),
                        np.max(trainLocations[:,2])))
                
                selected_locations = np.array([locations[i]
                    for i in range(locations.shape[0])
                    if locations[i][1] >= boundingBox[0][0] - kernelSpan
                    and locations[i][1] <= boundingBox[1][0] + kernelSpan
                    and locations[i][2] >= boundingBox[0][1] - kernelSpan
                    and locations[i][2] <= boundingBox[1][1] + kernelSpan])

                # ################################

                self.gprProc.fit(trainLocations, trainValues)
                computed_locations = self.gprProc.predict(
                        selected_locations, return_std=self.computeStd)
                
                same_locations = np.array([i
                    for i in range(locations.shape[0])
                    if locations[i][1] >= boundingBox[0][0] - kernelSpan
                    and locations[i][1] <= boundingBox[1][0] + kernelSpan
                    and locations[i][2] >= boundingBox[0][1] - kernelSpan
                    and locations[i][2] <= boundingBox[1][1] + kernelSpan],
                    dtype=np.int16)
                print(same_locations.shape[0])
                
                if self.computeStd:
                    val_res = np.ones((locations.shape[0], 1))*self.kernel.mean
                    std_res = np.ones(locations.shape[0])*self.kernel.variance
                    np.put(val_res, same_locations, computed_locations[0])
                    np.put(std_res, same_locations, computed_locations[1])
                    return (val_res, std_res)
                else:
                    res = np.ones(locations.shape[0], 1)*self.kernel.mean
                    np.put(res, same_locations, computed_locations)
                    return (res, None)

    def checkCache(self, keys):
        return (self.cache is not None) and keys == self.keys

    def setKeys(self, keys):
        self.keys = keys
    
    def shape(self):
        return (None, None, None, None)

    def span(self):
        return (None, None, None, None)

    def bounds(self):
        return (None, None, None, None)

    def resolution(self):
        return self.kernel.resolution()

    def sample_size(self):
        return self.sampleSize

    def range(self):
        return self.dataRange

    def getStd(self, keys):
        self.updateCache(keys)
        return self.cache[1]

    def getValue(self, keys):
        self.updateCache(keys)
        return self.cache[0]

    def updateCache(self, keys):
        with self.getItemLock:
            if not self.checkCache(keys):
                self.setKeys(keys)
                locations, dims, shape = self.computeLocations(keys)
                pred = self.at_locations(locations)
                if self.computeStd:
                    outputShape = list(shape)
                    std_computed = ScaledArray(pred[1].reshape(outputShape)
                            .squeeze(), dims)
                    if len(pred[0].shape) == 2:
                        outputShape.append(pred[0].shape[1])
                        val_computed = ScaledArray(pred[0].reshape(outputShape)
                                .squeeze(), dims)
                        self.cache = (val_computed, std_computed)
                else:
                    self.cache = (self.computeScaledArray(shape, pred[0], dims),
                            None)

    def setComputeStd(self, state):
        self.computeStd = state

    def __getitem__(self, keys):
        return self.getValue
