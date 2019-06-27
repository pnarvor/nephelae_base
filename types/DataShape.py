import numpy as np

class DimensionShape:

    """DimensionShape

    Helper type holding regular sampling information over a 1D linear space

    Attributes:

        size    (int): Number of samples
        begin (float): First value of the sampling locations
        end   (float): First value of the \"next\" sampling locations (see location() method details below)

    Methods:
        
        locations()  : Produce linearly sampled values between self.begin and self.size.
                       Returns a 1D numpy.ndarray.

                       /!\ The begin and end attributes are managed in such a way that two contigous DimensionShape
                           (dimShape1.end == dimShape2.begin) produce regularly spaced locations.
                           (The concatenation of dimShape1.locations() and dimShape2.locations() is a regularly sampled 1D space
                           from dimShape1.begin to dimShape2.end)

        span()       : Length of the dimension. Returns a float
    """

    def __init__(self, size=0, begin=0.0, end=0.0):

        self.size  = 0
        self.begin = begin
        self.end   = end

    def locations(self);
        return self.span()*np.linspace(0, self.size-1)/self.size + self.begin

    def span(self):
        return self.end() - self.begin()



