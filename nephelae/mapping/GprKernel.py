import os
import numpy as np
import numpy.fft as npfft
import pickle
import sklearn.gaussian_process.kernels as gpk
from   scipy.spatial.distance import cdist
from   copy import deepcopy

class NephKernel(gpk.Kernel):

    """
    NephKernel

    Base class for Gaussian Process kernel used in the nephelae_project

    Kernel derived from sklearn.gaussian_process.Kernel
    to be used in sklearn.gaussian_process.GaussianProcessRegressor.

    This kernel equivalent to a scikit-learn RBF (Radial Basis Funcion) kernel,
    with white noise and some additional methods. The exact definition of the
    kernel is :
        variance*exp(-0.5*|(x-y)/lengthScales|^2) + diag(noiseVariance)

    /!\ Hyper parameters optimization HAS NOT BEEN TESTED
    When using with GaussianProcessRegressor, set optimizer=None
    
    Attributes
    ----------
    lengthScales : numpy.array
        Length scale of considered process on each dimension of the input space.
        See a GPR tutorial for more info.

    variance : float or numpy.array
        Variance of the considered process. Is a numpy.array if the output
        space is multidimensional. See a GPR tutorial for more info.

    noiseVariance : float or numpy.array
        Variance of the measure noise (usually sensor noise, or used as a
        smoothing parameter). See a GPR tutorial for more info.

    """

    def __init__(self, lengthScale, variance, noiseVariance):

        """
        Parameters
        ----------

        lengthScales : numpy.array
            Length scale of considered process on each dimension of the input
            space. See a GPR tutorial for more info.

        variance : float or numpy.array
            Variance of the considered process. Is a numpy.array if the output
            space is multidimensional. See a GPR tutorial for more info.

        noiseVariance : float or numpy.array
            Variance of the measure noise (usually sensor noise, or used as a
            smoothing parameter). See a GPR tutorial for more info.
        """

        self.lengthScales  = lengthScale
        self.variance      = variance
        self.noiseVariance = noiseVariance


    def __call__(self, X, Y=None):
        """See sklearn.gaussian_process.kernels for details
        https://scikit-learn.org/stable/modules/classes.html#module-sklearn.gaussian_process
            TODO : a doc...
        """

        if Y is None:
            Y = X

        distMat = cdist(X / self.lengthScales,
                        Y / self.lengthScales,
                        metric='sqeuclidian')
        if Y is X:
            return self.variance*np.exp(-0.5*distMat)\
                   + np.diag([self.noiseVariance]*X.shape[0])
        else:
            return self.variance*np.exp(-0.5*distMat)


    def diag(self, X):
        """See sklearn.gaussian_process.kernels for details
        https://scikit-learn.org/stable/modules/classes.html#module-sklearn.gaussian_process
            TODO : a doc...
        """
        return np.array([self.variance + self.noiseVariance]*X.shape[0])


    def is_stationary(self):
        """See sklearn.gaussian_process.kernels for details
        https://scikit-learn.org/stable/modules/classes.html#module-sklearn.gaussian_process
            TODO : a doc...
        """
        return True


    def resolution(self):
        """Returns the optimal resolution to which compute a dense map.

        Value computed by estimating the cutting frequency of the RBF kernel.
        The kernel is the autocorrelation of the process and thus its Fourier
        transform is the power spectrum of the process.

        This resolution was computed as the inverse of twice the cut-off
        frequency where the spectrum falls below -60dB (Nyquist-Shannon
        sampling theorem).

        The resolution returned by this method is the minimal resolution
        without loos of information.
        """
        # return 0.84 * np.array(self.lengthScales)
        # return 0.42 * np.array(self.lengthScales)
        # After a bit of experiement, this seems better => investigate why
        return 0.3 * np.array(self.lengthScales) # 0.84 / (2 * sqrt(2)) ???


    def span(self):
        """Distance from which a sample contribution is deemed negligible
        in front of another one.

        This is used to discard negligible data before the costly computation
        of a GPR prediction.

        Is set at 3 sigmas (kernel being a Gaussian-based kernel).

        This parameter is a trade-off performance versus-precision.
        TODO : (make this criterion configurable ?)
        """
        return 3.0 * np.array(self.lengthScales)



class WindKernel(NephKernel):

    """
    WindKernel
    Derived from NephKernel.

    Kernel design to take wind into account when computing the distance
    between two samples.

    More generally : each measurement point is considered to be able to
    drift over time, like clouds goes with the wind. The net result is that
    two data points taken at the same location in space but at different
    times should be considered different (=low kernel value). Two data points
    taken at different locations but related by the relation
    p1 = p0 + v*dt where v is the wind speed should be considered similar
    (high kernel value).

    A few of the benefits of using this kernel to predict the dense map of a
    cloud are :
        - Even when no new data is taken, successive predicted map with old
          data will still predict the true cloud location if the wind speed
          is accurate.
        - Data points can have a longer lifetime than if they are considered
          fixed, so have a longer time lengthScale. Predicted maps should
          be more precise with less data.

    /!\ Only implemented for dimension (t,x,y,z). (only (t,x,y) won't work)

    Attributes
    ----------
    wind : nephelae.mapping.WindMap
        A class able to return a wind estimation at a given location.


    """

    def __init__(self, lengthScales, variance, noiseVariance, windMap, mean=0):

        """
        Parameters
        ----------
        wind : nephelae.mapping.WindMap
            A class able to return a wind estimation at a given location.
        """

        super().__init__(lengthScales, variance, noiseVariance)
        self.windMap = windMap
        self.mean = mean

    
    def __call__(self, X, Y=None):

        """See sklearn.gaussian_process.kernels for details
        https://scikit-learn.org/stable/modules/classes.html#module-sklearn.gaussian_process
            TODO : a doc...
        """

        if Y is None:
            Y = X

        # print("X shape: ", X.shape)
        # print("Y shape: ", X.shape, end="\n\n")
        
        wind = self.windMap.at_locations(Y)

        # print("Horizontal wind :", wind)
        # print(Y)
        # if self.windMap.name == 'H_Wind':
        #     print("X shape:\n", X)
        #     print("Y shape:\n", Y) 
        #     print("Mean horizontal wind :", wind.mean(axis=0))
        # print("self.variance :", self.variance)

        # Far from most efficient but efficiency requires C++ implementation 
        # (Or is it ? Yes. Yes it is. 40ns self time, cdist : 2ns, can be 6 times as fast)
        t0,t1 = np.meshgrid(X[:,0], Y[:,0], indexing='ij', copy=False)
        dt = t1 - t0
        distMat = (dt / self.lengthScales[0])**2

        # if self.windMap.name == 'H_Wind':
        #     print("distMat0 :\n", [np.min(distMat.ravel()), np.max(distMat.ravel())])

        x0,x1 = np.meshgrid(X[:,1],    Y[:,1], indexing='ij', copy=False)
        x0,w1 = np.meshgrid(X[:,1], wind[:,0], indexing='ij', copy=False)
        dx = x1 - (x0 + w1 * dt)
        distMat = distMat + (dx / self.lengthScales[1])**2

        # if self.windMap.name == 'H_Wind':
        #     print("distMat1 :\n", [np.min(distMat.ravel()), np.max(distMat.ravel())])

        x0,x1 = np.meshgrid(X[:,2],    Y[:,2], indexing='ij', copy=False)
        x0,w1 = np.meshgrid(X[:,2], wind[:,1], indexing='ij', copy=False)
        dx = x1 - (x0 + w1 * dt)
        distMat = distMat + (dx / self.lengthScales[2])**2

        # if self.windMap.name == 'H_Wind':
        #     print("distMat2 :\n", [np.min(distMat.ravel()), np.max(distMat.ravel())])
        
        distMat = distMat + cdist((X[:,3] / self.lengthScales[3]).reshape(-1,1),
                                  (Y[:,3] / self.lengthScales[3]).reshape(-1,1),
                                  metric='sqeuclidean')

        # if self.windMap.name == 'H_Wind':
        #     print("distMat3 :\n", [np.min(distMat.ravel()), np.max(distMat.ravel())])

        if Y is X:
            return self.variance*np.exp(-0.5*distMat)\
                   + np.diag([self.noiseVariance]*X.shape[0])
        else:
            return self.variance*np.exp(-0.5*distMat)

        # print("Wind map :", self.windMap.name)
        # if Y is X:
        #     res = self.variance*np.exp(-0.5*distMat)\
        #            + np.diag([self.noiseVariance]*X.shape[0])
        #     # print("Y is X:\n", res)
        # else:
        #     res = self.variance*np.exp(-0.5*distMat)
        #     # print("Y is no X:\n", res)

        # if self.windMap.name == 'H_Wind':
        #     print("res :\n", [np.min(res.ravel()), np.max(res.ravel())])

        # if self.windMap.name == 'H_Wind':
        #     print("Y is no X:\n", res)
        # return res


    def __deepcopy__(self, memo):

        """For compatibility with sklearn

        sklearn does a deepcopy of the kernel, which in sklearn implementation
        is not costly. However in this specific implementation, the kernel
        contains a reference a of full database. This method overrides the
        deepcopy of the WindMap attribute to avoid the full deepcopy of
        the database.

        /!\ This method may not behave as intended. Check it.
        """
        print("Deepcopy was called ################################################################################") 
        # Forbidding deepcopy of self.windMap
        # scikit-learn will deepcopy the kernel and if the windMap is a 
        # GprPredictor it contains a reference to a databasei, which will
        # be deep-copied alongside the kernel. We don't want that.
        other = WindKernel(deepcopy(self.lengthScales, memo),
                           deepcopy(self.variance, memo),
                           deepcopy(self.noiseVariance, memo),
                           self.windMap)



# class NephKernel(GprKernel):
# 
#     """NephKernel
# 
#     Specialization of GprKernel for Nephelae project use.
#     (for convenience, no heavy code here)
#     """
# 
#     def load(path):
#         return pickle.load(open(path, "rb"))
# 
# 
#     def save(kernel, path, force=False):
#         if not force and os.path.exists(path):
#             raise ValueError("Path \"" + path + "\" already exists. "
#                              "Please delete the file, pick another path "
#                              "or force overwritting with force=True")
#         pickle.dump(kernel, open(path, "wb"))
# 
# 
#     def __init__(self, lengthScales, variance, noiseVariance):
#         self.lengthScales  = lengthScales
#         self.noiseVariance = noiseVariance
#         self.variance      = variance
#         super().__init__(variance*gpk.RBF(lengthScales) + gpk.WhiteKernel(noiseVariance),
#                          lengthScales)
# 
# 
#     def __getstate__(self):
#         serializedItems = {}
#         serializedItems['lengthScales']  = self.lengthScales
#         serializedItems['noiseVariance'] = self.noiseVariance
#         return serializedItems
# 
# 
#     def __setstate__(self, data):
#         self.__init__(data['lengthScales'],
#                       data['noiseVariance'])




