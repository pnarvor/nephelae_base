from .DataView import DataView

# from random import randn

class Function(DataView):

    """
    Function

    Base class for data views applying a function on the SensorSamples.

    """

    def __init__(self, parents=[]):
        super().__init__(parents)

    
    def process_notified_sample(self, sample):
        with self.parametersLock:
            return self.process_sample(sample)


    def process_fetched_samples(self, samples):
        with self.parametersLock:
            return [self.process_sample(sample) for sample in samples]


    def process_sample(self, sample):
        return sample

    



