import threading
from warnings import warn

from nephelae.types import ObserverSubject

class DataView(ObserverSubject):

    """
    DataView

    Base class of all DataView objects. Their purpose is to abstract the link
    between database and data consumers, allowing some simple data processing
    and being configurable online. They can be chained to allow for complex
    behaviors.


    TODOs : mission-like updatable parameters ?
    """

    parameterNames = []

    def __init__(self, parents=[]):

        """
        parameters:

        parents : list(Dataview, ...)
            List of dataviews this dataview is supposed to fetch SensorSample from.
        """
        # all Dataviews are add_sample observers AND observable (this is how
        # the processing pipeline is built).
        super().__init__('add_sample')
        
        self.parents = []
        for parent in parents:
            self.add_parent(parent)
        self.parametersLock = threading.Lock()


    def add_parent(self, parent):
        if not self.has_parent(parent):
            self.parents.append(parent)
            parent.attach_observer(self)

    
    def remove_parent(self, parent):
        if self.has_parent(parent):
            self.parents.remove(parent)
        try:
            parent.detach_observer(self)
        except KeyError as e:
            warn("DataView self was not attached to this parent")
    

    def has_parent(self, parent):
        return parent in self.parents
    

    def add_sample(self, sample):
        """
        This is the method called by a parent notifying a sample. Will notify
        the observer in return with the sample after processing it with
        self.sample_notified You probably don't wan't to touch this.
        Reimplement self.sample_notified instead.
        """
        processedSample = self.process_notified_sample(sample)
        if processedSample is not None:
            self.do_notify(processedSample)


    def __getitem__(self, keys):
        """
        Will fetch data from parent DataViews, concatenate and process them
        before returning them.
        """
        output = []
        for parent in self.parents:
            output = output + parent[keys]
        return self.process_fetched_samples(output)


    def process_notified_sample(self, sample):
        """
        Process a single sample before notifying the observers (childs). Is
        called by self.add_sample. To be reimplemented by subclasses.
        """
        return sample


    def process_fetched_samples(self, samples):
        """
        Process a list of samples before returning to the childs __getitem__
        function. Is called by self.__getitem__. To be reimplemented by
        subclasses.

        /!\ Samples are allowed to be processed "in place" (make a deepcopy of
        samples for the DatabaseView).
        """
        return samples
        

    def get_parameters(self):
        """Return a dictionary with parameter names and their values"""
        
        with self.parametersLock:
            params = {}
            for name in self.parameterNames:
                params[name] = getattr(self, name)
            return params


    def set_parameters(self, **params):
        """Set a parameter value (with check)"""
        with self.parametersLock:
            for param in params:
                setattr(self, param, params[param])


