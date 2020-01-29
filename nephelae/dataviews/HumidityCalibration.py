from .Function import Function

class HumidityCalibration(Function):

    """
    Function

    Base class for data views applying a function on the SensorSamples.

    """

    parameterNames = ['gain_1', 'offset_1', 'gain_2', 'offset_2', 'lt']

    def __init__(self, lt=0.0, gain_1=1.0, offset_1=0.0, gain_2=1.0, offset_2=0.0, parents=[]):

        super().__init__(parents)
        self.lt = lt
        self.gain_1   = gain_1
        self.offset_1 = offset_1
        self.gain_2   = gain_2
        self.offset_2 = offset_2

    
    def process_sample(self, sample):
        sample.data = [self.gain_1*value + self.offset_1 if value < self.lt else 
        self.gain_2*value + self.offset_2 for value in sample.data]
        return sample

    



