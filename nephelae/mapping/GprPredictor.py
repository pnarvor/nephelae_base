import numpy as np
import threading
from sklearn.gaussian_process import GaussianProcessRegressor

from nephelae.types import Bounds

from .MapInterface import MapInterface

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

    computesStddev : bool
        On prediction, GaussianProcessRegressor can either return only the
        Maximum A Posteriori (MAP) or both the MAP and its associated
        covariance map. (TODO : remove this and transform it in a cached
        covariance map).

    updateRange : bool
        Mainly for drawing purposes. If true min-max value of the last predicted
        map are re-computed each time.

    dataRange : list(Bounds,...)
        Contains range of value inside last predicted map. See
        nephelae.mapping.MapInterface for more details.

    lock : threading.Lock
        Simple mutex to allow only one map computation at a time in
        self.at_location method. self.at_location will return Non if busy.

    Methods
    -------

    at_locations(locations) ->  numpy.array:
        Computes predicted value at each given location using GPR.
        This method is used in the map interface when requesting a dense map.
        When requesting a dense map, each location must be the position of
        on pixel of the requested map.

    See nephelae.mapping.MapInterface for other methods.
    """

    def __init__(self, name, database, databaseTags, kernel,
                 sampleSize=1, computesStddev=True, updateRange=True):

        """
        name : str
            Name of the computed map. Must be unique.

        database (nephelae_mapping.database):
            database from which fetch the relevant data for map computation.

        databaseTags : list(str, ...)
            tags for searching data in the database.
       
        kernel : sklearn.gaussian_process.kernel.Kernel derived type
            Kernel used in GPR.

        computesStddev : bool
            On prediction, GaussianProcessRegressor can either return only the
            Maximum A Posteriori (MAP) or both the MAP and its associated
            covariance map. (TODO : remove this and transform it in a cached
            covariance map).

        updateRange : bool
            Mainly for drawing purposes. If true min-max value of the last predicted
            map are re-computed each time.
        """
        super().__init__(name)

        self.database     = database
        self.databaseTags = databaseTags
        self.kernel       = kernel
        self.gprProc = GaussianProcessRegressor(self.kernel,
                                                alpha=0.0,
                                                optimizer=None,
                                                copy_X_train=False)
        self.computesStddev = computesStddev
        self.updateRange    = updateRange
        self.dataRange      = []
        self.lock           = threading.Lock()
        self.sampleSize     = sampleSize # Find a way to make this automatic


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

        # try:
        # with self.lock:
        if not self.lock.acquire(blocking=True, timeout=1.0):
            print("###### Cloud not lock", self.name, "! ####################################")
            return
        try:

            # ############## WRRRROOOOOOOOOOOOOOOOOOOOOOONNG #####################
            # # Must take all data otherwise prediction not possible because outside 
            # # locations
            # searchKeys = [slice(b.min,b.max) for b in Bounds.from_array(locations.T)]
            # samples = [entry.data for entry in \
            #            self.database.find_entries(self.databaseTags, tuple(searchKeys)]

            # Finding bounds of data we currently have then compute
            # proper bounds of data to request. This ensure we have some data
            # to make predictions on.
            # Here only time limts are considered
            # locations are assumed to be sorted in increasing time order
            # (same time location will probably be asked more often anyway)
            dataBounds = self.database.find_bounds(self.databaseTags)[0]
            kernelSpan = self.kernel.span()[0]
            locBounds = Bounds(locations[0,0], locations[-1,0])

            locBounds.min = max([locBounds.min, dataBounds.min])
            locBounds.max = min([locBounds.max, dataBounds.max])
            locBounds.min = locBounds.min - kernelSpan
            locBounds.max = locBounds.max + kernelSpan

            samples = [entry.data for entry in \
                self.database.find_entries(self.databaseTags,
                                           (slice(locBounds.min, locBounds.max),))]
            
            trainLocations =\
                np.array([[s.position.t,\
                           s.position.x,\
                           s.position.y,\
                           s.position.z]\
                           for s in samples])
            trainValues = np.array([s.data for s in samples]).squeeze()
            if len(trainValues.shape) < 2:
                trainValues = trainValues.reshape(-1,1)
            try:
                gprProc = GaussianProcessRegressor(self.kernel,
                                                   alpha=0.0,
                                                   optimizer=None,
                                                   copy_X_train=False)
                gprProc.fit(trainLocations, trainValues)
            except Exception as e:
                print("Got exception in", self.name)
                raise e

            
            if self.updateRange:
                res = gprProc.predict(locations, return_std=self.computes_stddev())
                if self.computes_stddev():
                    tmp = res[0]
                else:
                    tmp = res
                Min = tmp.min(axis=0)
                Max = tmp.max(axis=0)
                if np.isscalar(Min):
                    Min = [Min]
                    Max = [Max]
                if len(Min) != len(self.dataRange):
                    self.dataRange = [Bounds(m, M) for m,M in zip(Min,Max)]
                else:
                    for b,m,M in zip(self.dataRange, Min, Max):
                        b.update(m)
                        b.update(M)
                return res
            else:
                return gprProc.predict(locations, return_std=self.computes_stddev())
        finally:
            self.lock.release()

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


    def computes_stddev(self):
        return self.computesStddev

