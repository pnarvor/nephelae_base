from nephelae.types   import Bounds
from nephelae.mapping import MapInterface


class MapServer:

    """
    MapServer

    Class holding and managing a set of MapInterface, and some managing tasks.

    Is intended to be the facade of the mapping functions.
        - Create a set of MapInterface from a configuration file.
        - Single instance holding all the MapInterface
        - Mapping bounds.

    Attributes
    ----------
    maps : dict({str:MapInterface},...)
        Set of maps. Keys are map names. MapInterface can be either a
        MesonhMap or a GprPredictor (or... ?).

    bounds : tuple(None, nephelae.types.Bounds,...)
        Bounds of mapping query in each dimension. When requesting a map
        slice, keys while be cropped to these bounds. If bounds of a dimension
        are None, keys are not cropped.

    dataServer : nephelae.database.NephelaeDataServer
        Data server from which GprPredictor will fetch data for building maps.
        Can be None if no GprPredictor are used as maps.
    """

    def __init__(self, configFile=None, mapSet=None, mapBounds=None, dataServer=None):

        """
        Parameters
        ----------
        configFile : None, str
            Configuration file from which to build the map server.
            /!\ If this parameter is set, the following parameters are ignored.

        mapSet : dict({str,MapInterface},...)
            Ignored if configFile is set.
            Dictionary of maps to be managed by the map server. Keys are 
            map names (str), values are instances of MapInterface sub-classes.

        mapBounds : tuple(None, nephelae.types.Bounds,...)
            Ignored if configFile is set. 
            Bounds of mapping query in each dimension. When requesting a map
            slice, keys while be cropped to these bounds. If bounds of a
            dimension are None, keys won't be cropped. If is None,
            self.bounds will be set to (None, None, None, None), (no bounds 
            in (t,x,y,z) dimensions).

        dataServer : nephelae.database.NephelaeDataServer
            Instance of a NephelaeDataServer from which GprPredictor will fetch
            data for building maps. Can be None if no GprPredictor are used as
            maps.
        """
        
        if configFile is None:
            self.maps       = mapSet
            self.bounds     = mapBounds
            self.dataServer = dataServer
        else:
            self.maps       = None
            self.bounds     = None
            self.dataServer = dataServer
            self.build_from_file(configFile)


    def build_from_file(self, configFile):
        """Build the MapServer instance from a configuration file"""
        raise NotImplemented("This is not implemented yet. Please wait, we are working as fast as we can.")


    def names(self):
        return self.maps.keys()


    def __getitem__(self, mapId):
        class MapReader:
            """
            MapReader.

            This class is only for syntactic sugar. This is to be able to call
            directly MapServer['map'][keys] but by cropping keys according to
            MapServer.bounds.

            """
            def __init__(self, mapServer, mapId):
                self.mapServer = mapServer
                self.mapId     = mapId
            def __getitem__(self, keys):
                return self.mapServer.maps[self.mapId][self.mapServer.process_keys(keys)]
        return MapReader(self, mapId)


    def process_keys(self, keys):

        """Will crop key from a __getitem__ method according to self.bounds"""

        def process_key(key, dim):
            if dim.min is not None:
                key = max(key, dim.min)
            if dim.max is not None:
                key = min(key, dim.max)
            return key

        keys = list(keys)
        while len(keys) < len(self.bounds):
            keys.append(slice(None))

        newKeys = []
        for key, b in zip(keys, self.bounds):
            if b is None:
                newKeys.append(key)
            elif isinstance(key, slice):
                newKeys.append(slice(
                    b.min if key.start is None else process_key(key.start, b),
                    b.max if key.stop  is None else process_key(key.stop,  b)))
            else:
                newKeys.append(process_key(key, b))
        return newKeys

