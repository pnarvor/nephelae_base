import numpy as np
import threading
from sklearn.gaussian_process import GaussianProcessRegressor

from nephelae.types import Bounds

from .MapInterface import MapInterface

class GprPredictor(MapInterface):

    """GprPredictor

    Class dedicated to prediction using Gaussian Process Regression.

    No kernel parameters is optimised, kernel is given as a fixed parameter.

    """

    def __init__(self, name, database, databaseTags, kernel,
                 computesStddev=True, updateRange=True):

        """
        variableName (str):
            name of the variable (no inside class purpose, only an identifier)

        database (nephelae_mapping.database):
            database from which fetching the measured data

        databaseTags (list of strings):
            tags for searching data in the database
       
        kernel (GprKernel): kernel to use for the prediction
                            (is compatiable with scikit-learn kernels)
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


    def at_locations(self, locations):

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
            # print("Train locations :", trainLocations.shape)
            # print("Train values    :", trainValues.shape)
            # print("Predic locations:", locations.shape)
            if len(trainValues.shape) < 2:
                trainValues = trainValues.reshape(-1,1)
            try:
                # self.gprProc.fit(trainLocations, trainValues)
                gprProc = GaussianProcessRegressor(self.kernel,
                                                   alpha=0.0,
                                                   optimizer=None,
                                                   copy_X_train=False)
                gprProc.fit(trainLocations, trainValues)
            except Exception as e:
                print("Got exception in", self.name)
                raise e

            
            if "Liquid" in self.name:
                print("Doing prediction :", self.name)
                print("Train locations   :", trainLocations.shape)
                print("Train values      :", trainValues.shape)
                print("Train values mean :", trainValues.mean(axis=0))
                print("Predic locations  :", locations.shape)
            if self.updateRange:
                # res = self.gprProc.predict(locations, return_std=self.computes_stddev())
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
                if "Liquid" in self.name:
                    print("Updating range :", self.dataRange, "\n\n")
                return res
            else:
                if "Liquid" in self.name:
                    print("Not updating range :", self.dataRange, "\n\n")
                # return self.gprProc.predict(locations, return_std=self.computes_stddev())
                return gprProc.predict(locations, return_std=self.computes_stddev())
        finally:
            self.lock.release()
        # except Exception as e:
        #     print("Got exception :", e)
        #     raise e

    def shape(self):
        return (None, None, None, None)


    def span(self):
        return (None, None, None, None)


    def bounds(self):
        return (None, None, None, None)


    def resolution(self):
        return self.kernel.resolution()
   

    def range(self):
        return self.dataRange


    def computes_stddev(self):
        return self.computesStddev

