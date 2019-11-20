import numpy as np
import threading
from sklearn.gaussian_process import GaussianProcessRegressor

from nephelae.types import Bounds

class GprPredictor():

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

    compute_maps(locations):
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

    def computeMaps(self, locations):

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
        kernelSpan = self.kernel.span()[0]
        locBounds = Bounds(locations[0,0], locations[-1,0])

        locBounds.min = locBounds.min - kernelSpan
        locBounds.max = locBounds.max + kernelSpan
        samples = [entry.data for entry in \
                self.database[self.databaseTags]\
                (assumePositiveTime=False)\
                [locBounds.min:locBounds.max]]

        if len(samples) < 1:
            self.cache = (np.ones(locations.shape)*self.kernel.mean,
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

            self.gprProc.fit(trainLocations, trainValues)
            self.cache = self.gprProc.predict(locations, return_std=True)

    def checkCache(self, keys):
        return (self.cache is not None) and keys == self.keys

    def setKeys(self, keys):
        self.keys = keys
