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

    cache : couple
        Contains computed Values and Stds maps of given keys.

    Methods
    -------

    at_locations(locations):
        Computes predicted value at each given location using GPR.
        This method is used in the map interface when requesting a dense map.
        When requesting a dense map, each location must be the position of
        on pixel of the requested map.

    See nephelae.mapping.MapInterface for other methods.
    """

    def __init__(self, name, database, databaseTags, kernel,
            dataRange=(Bounds(0, 0),), updateRange=True, threshold=0):

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
        super().__init__(name, threshold=threshold)
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
        self.updateRange    = updateRange
        self.dataRange      = dataRange

    
    def at_locations(self, locations, locBounds=None):

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
            if locBounds is None:
                kernelSpan = self.kernel.span()
                locBounds = Bounds.from_array(locations.T)
                
                locBounds[0].min = locBounds[0].min - kernelSpan[0]
                locBounds[0].max = locBounds[0].max + kernelSpan[0]
                
                locBounds[1].min = locBounds[1].min - kernelSpan[1]
                locBounds[1].max = locBounds[1].max + kernelSpan[1]
                
                locBounds[2].min = locBounds[2].min - kernelSpan[2]
                locBounds[2].max = locBounds[2].max + kernelSpan[2]
                
                locBounds[3].min = locBounds[3].min - kernelSpan[3]
                locBounds[3].max = locBounds[3].max + kernelSpan[3]
            
            samples = [entry.data for entry in \
                    self.database[self.databaseTags]\
                    (assumePositiveTime=False)\
                    [locBounds[0].min:locBounds[0].max,
                    locBounds[1].min:locBounds[1].max,
                    locBounds[2].min:locBounds[2].max,
                    locBounds[3].min:locBounds[3].max]]
            
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
                
                boundingBox = (np.min(trainLocations, axis=0), 
                    np.max(trainLocations, axis=0))

                dt = boundingBox[1][0] - boundingBox[0][0]
                
                wind = self.kernel.windMap.get_wind()

                dx, dy = dt*wind

                boundingBox[0][1] = min(boundingBox[0][1], boundingBox[0][1] +
                        dx)
                boundingBox[1][1] = max(boundingBox[1][1], boundingBox[1][1] +
                        dx)

                boundingBox[0][2] = min(boundingBox[0][2], boundingBox[0][2] +
                        dy)
                boundingBox[1][2] = max(boundingBox[1][2], boundingBox[1][2] +
                        dy)

                same_locations = np.where(np.logical_and(
                    np.logical_and(
                        np.logical_and(
                            locations[:,0] >= boundingBox[0][0] - kernelSpan[0],
                            locations[:,0] <= boundingBox[1][0] + kernelSpan[0]),
                        np.logical_and(
                            locations[:,1] >= boundingBox[0][1] - kernelSpan[1],
                            locations[:,1] <= boundingBox[1][1] + kernelSpan[1])),
                    np.logical_and(
                        np.logical_and(
                            locations[:,2] >= boundingBox[0][2] - kernelSpan[2],
                            locations[:,2] <= boundingBox[1][2] + kernelSpan[2]),
                        np.logical_and(
                            locations[:,3] >= boundingBox[0][3] - kernelSpan[3],
                            locations[:,3] <= boundingBox[1][3] + kernelSpan[3])
                    )))[0]
                
                selected_locations = locations[same_locations]
                
                self.gprProc.fit(trainLocations, trainValues)
                computed_locations = self.gprProc.predict(
                        selected_locations, return_std=self.computeStd)
                
                if self.computeStd:
                    val_res = np.ones((locations.shape[0], 1))*self.kernel.mean
                    std_res = \
                    np.ones(locations.shape[0])*np.sqrt(self.kernel.variance + 
                            self.kernel.noiseVariance)
                    np.put(val_res, same_locations, computed_locations[0])
                    np.put(std_res, same_locations, computed_locations[1])
                    val_return = (val_res, std_res)
                else:
                    res = np.ones((locations.shape[0], 1))*self.kernel.mean
                    np.put(res, same_locations, computed_locations)
                    val_return = (res, None)
                
                if self.updateRange:
                    tmp = val_return[0]
                
                    Min = tmp.min(axis=0)
                    Max = tmp.max(axis=0)
                
                    if np.isscalar(Min):
                        Min = [Min]
                        Max = [Max]
                
                    if len(Min) != len(self.dataRange):
                        self.dataRange = tuple(Bounds(m, M) for m,M in
                                zip(Min,Max))
                    else:
                        for b,m,M in zip(self.dataRange, Min, Max):
                            b.update(m)
                            b.update(M)
                
                return val_return

    def check_cache(self, keys):
        return (self.cache is not None) and keys == self.keys

    def set_keys(self, keys):
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

    def get_std(self, keys):
        self.update_cache(keys)
        return self.cache[1]

    def get_value(self, keys):
        self.update_cache(keys)
        return self.cache[0]

    def update_cache(self, keys):
        with self.getItemLock:
            if not self.check_cache(keys):
                self.set_keys(keys)
                locations, dims, shape = self.compute_locations(keys)
                pred = self.at_locations(locations)
                if self.computeStd:
                    outputShape = list(shape)
                    stdComputed = ScaledArray(pred[1].reshape(outputShape)
                            .squeeze(), dims)
                    if len(pred[0].shape) == 2:
                        outputShape.append(pred[0].shape[1])
                        valComputed = ScaledArray(pred[0].reshape(outputShape)
                                .squeeze(), dims)
                        self.cache = (valComputed, stdComputed)
                else:
                    self.cache = (self.compute_scaled_array(shape, pred[0],
                        dims), None)

    def set_compute_std(self, state):
        self.computeStd = state

    def __getitem__(self, keys):
        return self.get_value(keys)
