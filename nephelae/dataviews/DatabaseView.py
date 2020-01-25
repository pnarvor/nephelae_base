from .DataView import DataView

class DatabaseView(DataView):

    """
    DatabaseView

    Dataview without parents made to access a NephelaeDataServer (The
    NephelaeDataServer play the role of a parent (but is not in the self.parent
    list).

    /!\ This can only be used to manage SensorSample, only the add_sample
    observation is done on the database.

    TODO Consider changing database output interface.

    Output interface is a regular DataView.
    """

    def __init__(self, database, searchTags):
        """
        Parameters:

        database : NephelaeDataServer
            database to which subscribing and from which data will be fetched
            on a __getitem__.

        searchTags : list(str, ...)
            tags to search data in the database.
        """
        super().__init__()

        self.database   = database
        self.searchTags = searchTags

        # subscribing to database
        self.database.add_sensor_observer(self)


    def __getitem__(self, keys):
        """
        Fetch and return data from the database.
        """
        # find_entries is expecting a tuple. If only one set of indices were
        # given between the brackets, keys is not a tuple.
        if isinstance(keys, (slice, float, int)):
            keys = (keys,)
        return [entry.data for entry in
                self.database.find_entries(tags=self.searchTags, keys=keys)]

    
    def process_notified_sample(self, sample):
        """
        Filter samples based in self.searchTags

        This is copied from NephelaeDataServer.add_sample consider changing the
        database output interface (must output DatabaseEntry via its observable
        methods.
        """
        sampleTags = [sample.producer, sample.variableName, 'SAMPLE']
        # if not all self.tag are in sample tags, ignore this sample
        if not all([tag in sampleTags for tag in self.searchTags]):
            return None
        else:
            return sample


