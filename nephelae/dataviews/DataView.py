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

    def __init__(self, parents=[]):

        """
        parameters:

        parents : list(Dataview, ...)
            List of dataviews this dataview is supposed to fetch SensorSample from.
        """
        # all Dataviews are add_sample observers AND observable (this is how
        # the processing pipeline is built).
        super().__init__('add_sample')

        self.parents = parents
        for parent in self.parents:
            parent.attach_observer(self)

    
    def add_sample(self, sample):
        """
        This is the method called by a parent notifying a sample. Will notify
        the observer in return with the sample after processing it with
        self.sample_notified You probably don't wan't to touch this.
        Reimplement self.sample_notified instead.
        """
        self.do_notify(self.process_notified_sample(sample))


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
        


