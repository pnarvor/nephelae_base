from .Function import Function

class Scaling(Function):

    """
    Function

    Base class for data views applying a function on the SensorSamples.

    """

    parameterNames = ['gain', 'offset']

    def __init__(self, name, gain=1.0, offset=0.0, parents=[]):

        super().__init__(name, parents)
        self.gain   = gain
        self.offset = offset

    
    def process_sample(self, sample):
        sample.data = [self.gain*(value + self.offset) for value in sample.data]
        return sample

    



