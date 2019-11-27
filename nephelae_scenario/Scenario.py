import yaml
import os
import time
from warnings import warn

from nephelae.types             import NavigationRef, Position, Pluginable, Bounds
from nephelae.database          import NephelaeDataServer

from nephelae_paparazzi         import build_aircraft
from nephelae_paparazzi.plugins import WindSimulation

from nephelae.mapping import WindMapConstant, WindObserverMap
from nephelae.mapping import GprPredictor, ValueMap, StdMap

from nephelae_mesonh import MesonhDataset, MesonhMap

from .YamlParser import YamlParser
from .loadables  import kernels as KernelTypes

def ensure_dictionary(config):
    """
    ensure_dictionary

    Ensure that config is a dictionary. If not, it is probably a list of one
    element dictionaries (the writer of the configuration file probably put
    hyphens '-' in front of his keys). If it is the case, this function will
    return a single dictionary built by fusing all the elements of the list.

    This function is mostly intended to simplify the parsing functions, as
    the output is always a dictionary.
    """
    if isinstance(config, dict):
        return config
    if not isinstance(config, list):
        raise TypeError("Unforeseen error in configuration file.\n" +
                        str(config))

    output = {}
    for element in config:
        if not isinstance(element, dict):
            raise ValueError("Parsing error in the configuration file.\n" +
                             str(element))
        if len(element) != 1:
            raise ValueError("Parsing error in the configuration file.\n" +
                             str(element))

        # getting one key in the dictionary
        key = next(iter(element))

        # Checking if key is not already in the output
        if key in output.keys():
            raise ValueError("Parsing error in the configuration file."+
                             "Two elements have the same key : " + str(key))
        
        # inserting this element in the output dictionary
        output[key] = element[key]

    return output

def ensure_list(config):
    """
    ensure_list

    Ensure that config is a list of one-valued dictionaries. This is called
    when the order of elements is important when loading the config file. (The
    yaml elements MUST have hyphens '-' in front of them).

    This function returns nothing, as no recovery can be achieved, the order of
    elements being lost when the dictionary is built.
    """

    if not isinstance(config, list):
        raise TypeError("config is not a list. Did you forget some '-' "+
                        "in your configuration file ?\n" + str(config))

    for element in config:
        if not isinstance(element, dict):
            raise ValueError("Parsing error in the configuration file.\n" +
                             str(element))
        if len(element) != 1:
            raise ValueError("Parsing error in the configuration file.\n" +
                             str(element))


        
class Scenario(Pluginable):

    """
    Scenario

    This is a class holding all the components for a Nephelae run.

    Its main goals are :
        - Holding all nephelae components (database, mesonh, uavs...)
        - All are loaded from config files written in yaml

    """

    def __init__(self, mainConfigPath):

        print(mainConfigPath)
        
        self.parser = YamlParser(mainConfigPath)
        
        self.missionT0     = None
        self.localFrame    = None
        self.flightArea    = None
        self.aircrafts     = {}
        self.database      = None
        self.mesonhFiles   = None
        self.mesonhDataset = None
        self.maps          = None
        self.kernels       = None

        self.running = False


    def load(self):
        
        self.config = ensure_dictionary(self.parser.parse())

        # Using current time as global mission time
        self.missionT0 = time.time()
        ref = Position(self.missionT0,
                       self.config['local_frame']['east'],
                       self.config['local_frame']['north'],
                       self.config['local_frame']['alt'])
        self.localFrame = NavigationRef(ref)
        self.flightArea = self.config['flight_area']
        
        self.database = self.configure_database()

        # To be configured in config file
        # self.windMap = WindMapConstant('Horizontal Wind', [-7.5, -0.5])
        self.windMap = WindObserverMap('Horizontal Wind', sampleName=str(['UT','VT']))
        self.database.add_sensor_observer(self.windMap)

            
        if 'mesonh_files' in self.config.keys():
            self.mesonhFiles   = self.config['mesonh_files']
            self.mesonhDataset = MesonhDataset(self.mesonhFiles)
        
        for key in self.config['aircrafts']:
            aircraft = build_aircraft(str(key), self.localFrame,
                                      self.config['aircrafts'])

            aircraft.add_gps_observer(self.database)
            if hasattr(aircraft, 'add_sensor_observer'):
                aircraft.add_sensor_observer(self.database)

            # find better way
            if hasattr(aircraft, 'windMap'):
                aircraft.windMap = self.windMap
            self.aircrafts[str(key)] = aircraft

        if 'wind_feedback' in self.config.keys():
            if self.config['wind_feedback']:
                self.load_plugin(WindSimulation, self.mesonhFiles)
        
        if 'maps' in self.config.keys():
            self.load_maps(self.config['maps'])
        else:
            print("Warning : no maps defined in config file")



    def start(self):
        self.running = True
        for aircraft in self.aircrafts.values():
            aircraft.start()
    
    def stop(self):
        self.running = False
        for aircraft in self.aircrafts.values():
            aircraft.stop()

        # Disabling database periodic save (will ave once before stoping)
        # Will be ignore if periodic save was already disabled
        self.database.disable_periodic_save()


    def configure_database(self):
        """TODO implement the replay"""

        database = NephelaeDataServer()
        database.set_navigation_frame(self.localFrame)
        
        try:
            config = self.config['database']
        except KeyError:
            # No specific options were given to the database.
            # Leaving default behavior.
            return database

        enableSave = False
        try:
            enableSave = config['enable_save']
        except KeyError:
            # No saving configuration
            pass

        if enableSave:
            try:
                filePath = config['filepath']
            except KeyError:
                raise ValueError("Configuration file "+self.mainConfigPath+\
                    " asked for database saving but did not set a 'filepath' field.")
            try:
                timerTick = config['timer_tick']
            except KeyError:
                timerTick = 60.0
            try:
                force = config['overwrite_existing']
            except KeyError:
                force = False
            database.enable_periodic_save(filePath, timerTick, force)

        return database


    def load_maps(self, config):
        """
        load_maps

        Instanciate GPR kernels and maps from the yaml parsed configuration and
        populates the self.kernels and self.maps attributes.
        """
        config = ensure_dictionary(config)
        if 'kernels' in config.keys():
            self.load_kernels(config['kernels'])
            
        self.maps = {}
        for key in config:
            if key == 'kernels':
                continue
            mapConfig = ensure_dictionary(config[key])
            if mapConfig['type'] == 'MesonhMap':
                self.load_mesonh_map(key, mapConfig)
            elif mapConfig['type'] == 'GprMap':
                self.load_gpr_map(key, mapConfig)
            else:
                warn(mapConfig['type'] + " is not a valid map type. "+
                     "Cannot instanciate '" + mapConfig['name'] + "'.")


    def load_mesonh_map(self, mapId, config):
        """
        load_mesonh_map

        Loads a single MesonhMap from a yaml parsed configuration and add it to
        the self.maps attribute.
        """
        if self.mesonhDataset is None:
            warn("No mesonh files were given in configuration file. "+
                 "Cannot instanciate MesonhMap '" + config['name']  +"'")
            return

        # Populating parameters for MesonhMap init
        params = {'name': config['name'],
                  'atm' : self.mesonhDataset,
                  'mesonhVar': config['mesonh_variable']}
        if 'interpolation' in config.keys():
            params['interpolation'] = config['interpolation']
        if 'origin' in config.keys():
            params['origin'] = config['origin']

        # Instanciation
        self.maps[mapId] = MesonhMap(**params)

        if 'data_range' in config.keys():
            self.maps[mapId].dataRange = (Bounds(rng[0], rng[1]),)


    def load_gpr_map(self, mapId, config):
        """
        load_gpr_map

        Loads a ValueMap from a yaml parsed configuration and add it to the
        self.maps attributes. Depending on the configuration, may also load a
        StdMap with the same GprPredictor.
        """
        
        if 'kernel' not in config.keys():
            warn("No kernel defined for GprMap '"+str(config['name'])+"'. "+
                 "Cannot instanciate this map.")
            return
        if config['kernel'] not in self.kernels.keys():
            warn("No kernel '"+config['kernel']+" defined. " +
                 "Cannot instanciate '"+config['name']+"' map.")
            return
        
        gpr = GprPredictor(self.database,
                           config['database_tags'],
                           self.kernels[config['kernel']])
        self.maps[mapId] = ValueMap(config['name'], gpr)
        if 'data_range' in config.keys():
            rng = config['data_range']
            self.maps[mapId].dataRange = (Bounds(rng[0], rng[1]),)

        if 'std_map' in config.keys():
            # If std_map if defined in the config, creating a new StdMap with
            # the same GprPredictor as the above StdMap.
            if mapId+'_std' in self.maps.keys():
                warn("The map '"+mapId+"_std' id is already defined. Cannot "+
                     "instanciate '"+config['std_map']+"' map.")
            else:
                self.maps[mapId+'_std'] = StdMap(config['std_map'], gpr)


    def load_kernels(self, config):
        """
        load_kernels

        Instanciate kernels from the yaml parsed configuration and populates
        the self.kernels attribute.
        """
        config = ensure_dictionary(config)
        self.kernels = {}
        for key in config:
            kernelConfig = ensure_dictionary(config[key])
            if kernelConfig['type'] not in KernelTypes.keys():
                raise ValueError(str(kernelConfig['type']) + " is not "+ 
                    "declared as a loadable kernel type. Did you forget " + 
                    "to declare it in nephelae_scenario.loadable.kernels ?")

            # Building parameter dictionary to be passed down to the kernel
            # __init__ method
            params = {}
            params['lengthScales']  = kernelConfig['length_scales']
            params['variance']      = kernelConfig['variance']
            params['noiseVariance'] = kernelConfig['noise_variance']
            if 'mean' in kernelConfig.keys():
                params['mean']      = kernelConfig['mean']
            if kernelConfig['type'] == 'WindKernel':
                params['windMap'] = self.windMap

            # Kernel instanciation
            self.kernels[key] = KernelTypes[kernelConfig['type']](**params)

        



