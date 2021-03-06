import yaml
import os
import time
from warnings import warn

from nephelae.types             import NavigationRef, Position, Pluginable, Bounds
from nephelae.types             import Bounds, DeepcopyGuard
from nephelae.database          import NephelaeDataServer
try:
    from nephelae.dataviews         import DataViewManager
except Exception as e:
    print("###### ERROR:", e)
    raise e

from nephelae_paparazzi         import Aircraft
from nephelae_paparazzi.plugins import WindSimulation
from nephelae_paparazzi.plugins.loaders import load_plugins

from nephelae.mapping import WindMapConstant, WindObserverMap
from nephelae.mapping import GprPredictor, ValueMap, StdMap
from nephelae.mapping import BorderIncertitude, BorderRaw

from nephelae_mesonh import MesonhDataset, MesonhMap

from .YamlParser import YamlParser
from .loadables  import kernels as KernelTypes
from .utils      import ensure_dictionary, ensure_list, find_aircraft_id


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
        self.dataviews     = {}
        self.mesonhFiles   = None
        self.mesonhDataset = None
        self.maps          = None
        self.kernels       = None
        self.borderClasses = None
        self.warmStart     = False

        self.running = False


    def load(self):
        
        self.config = ensure_dictionary(self.parser.parse())

        # Using current time as global mission time
        self.missionT0 = time.time()
        localFrameConfig = ensure_dictionary(self.config['local_frame'])
        ref = Position(self.missionT0,
                       localFrameConfig['east'],
                       localFrameConfig['north'],
                       localFrameConfig['alt'])
        self.localFrame = NavigationRef(ref, localFrameConfig['utm_zone'])
        self.flightArea = self.config['flight_area']
        
        self.database = self.configure_database()

        if 'data_views' in self.config.keys():
            self.dataviews = \
                DataViewManager.from_yaml_config(self.config['data_views'],
                                                  self.database)
        else:
            print("Warning : no data_views defined in config file.")

        # To be configured in config file
        # self.windMap = WindMapConstant('Horizontal Wind', [0.0, 0.0])
        # self.windMap = WindObserverMap('Horizontal Wind', sampleName=str(['UT','VT']))
        if 'wind_map' in self.config.keys():
            self.load_wind_map(self.config['wind_map'])
        else:
            raise KeyError('No wind map detected ! Wind maps types MUST be' +
                    'declared using wind_map as yaml keyword.')

        if 'mesonh_files' in self.config.keys():
            self.mesonhFiles   = self.config['mesonh_files']
            self.mesonhDataset = MesonhDataset(self.mesonhFiles)
       
        if 'wind_feedback' in self.config.keys():
            if self.config['wind_feedback']:
                self.load_plugin(WindSimulation, self.mesonhFiles)
        
        if 'maps' in self.config.keys():
            self.load_maps(self.config['maps'])
        else:
            print("Warning : no maps defined in config file")

        if 'aircrafts' in self.config.keys():
            self.load_aircrafts(self.config['aircrafts'])
        else:
            print("Warning : no aircrafts defined in config file")


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
        
        database = None
        try:
            self.warmStart = self.config['allow_warm_start']
        except KeyError as e:
            warn("No warm start configuration specified. No warm start " +
                 "allowed byt default. Exception feedback : " + str(e))
            self.warmStart = False
            
        
        try:
            config = self.config['database']
        except KeyError:
            # No specific options were given to the database.
            # Leaving default behavior.
            if self.warmStart:
                raise RuntimeError("Warm start enable but no database " + 
                                   "configuration was given. Aborting.")
            else:
                database = NephelaeDataServer()
                database.set_navigation_frame(self.localFrame)
                return database

        try:
            enableSave = config['enable_save']
        except KeyError:
            # No saving configuration
            enableSave = False
        try:
            filePath = config['filepath']
        except KeyError:
            filePath = None

        # This is safe (in python spec, x and y returns false if x is false
        # without trying to evaluate y)
        if self.warmStart and filePath is not None and os.path.exists(filePath):
            database = NephelaeDataServer.load(filePath)
            self.missionT0 = database.navFrame.position.t
            self.localFrame.position.t = self.missionT0
        else:
            database = NephelaeDataServer()
        database.set_navigation_frame(self.localFrame)

        if enableSave:
            if filePath is None:
                raise ValueError("Configuration file "+self.mainConfigPath+\
                    " asked for database saving but did not set a 'filepath' field.")
            try:
                timerTick = config['timer_tick']
            except KeyError:
                # Save database every 60.0 seconds if no tick given
                timerTick = 60.0
            try:
                force = config['overwrite_existing']
            except KeyError:
                # Don;t overwrite existing database by default
                force = False
            database.enable_periodic_save(filePath, timerTick, force)

        return database


    def load_wind_map(self, config):
        """
        Instanciate WindMaps objects. These objects includes WindMapConstant and
        WindObserverMap.
        """
        config = ensure_dictionary(config)
        keys = config.keys()
        params = {'name': config['name']}
        if config['type'] == 'WindMapConstant':
        
            if 'wind' in keys:
                params['wind'] = config['wind']
            if 'resolution' in keys:
                params['resolution'] = config['resolution']
            if 'threshold' in keys:
                params['threshold'] = config['threshold']

            self.windMap = WindMapConstant(**params)
        elif config['type'] == 'WindObserverMap':
            if 'sampleName' in keys:
                params['sampleName'] = str(config['sampleName'])
            if 'wind' in keys:
                params['defaultWindValue'] = config['wind']
            if 'maxSamples' in keys:
                params['maxSamples'] = config['maxSamples']
            if 'minSamples' in keys:
                params['minSamples'] = config['minSamples']
            if 'resolution' in keys:
                params['resolution'] = config['resolution']
            if 'threshold' in keys:
                params['threshold'] = config['threshold']

            self.windMap = WindObserverMap(**params)
            self.database.add_sensor_observer(self.windMap)
        else:
            raise ValueError(config['type'] + " is not a valid map type. "+
                     "Cannot instanciate '" + config['name'] + "'.")
        pass
    
    def load_aircrafts(self, config):
        """
        Instanciate Aircrafts objects, load aicrafts plugins and populate the
        self.aircrafts attribute.
        """
        config = ensure_dictionary(config)
        for item in config.items():
            self.load_aircraft(item)

    
    def load_aircraft(self, item):
        """
        load_aircraft

        Instanciate and returns an Aircraft instance with all its plugin
        loaded.
        """
        
        config     = ensure_dictionary(item[1])
        aircraftId = find_aircraft_id(item[0], config)

        if aircraftId in self.aircrafts.keys():
            raise RuntimeError("Aircraft '"+aircraftId+"' already loaded. " +
                               "This should not happen at all, aborting.")
        
        aircraft = Aircraft(aircraftId, self.localFrame)
        if 'plugins' in config.keys():
            load_plugins(aircraft, ensure_list(config['plugins']))

        aircraft.add_status_observer(self.database)
        if hasattr(aircraft, 'add_sensor_observer'):
            aircraft.add_sensor_observer(self.database)

        # find better way
        if hasattr(aircraft, 'windMap'):
            aircraft.windMap = self.windMap

        if hasattr(aircraft, 'mapWhereCenterIs'):
            aircraft.mapWhereCenterIs = self.maps[aircraft.mapWhereCenterIs]

        self.aircrafts[aircraftId] = aircraft


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
                  'mesonhVar': config['mesonh_variable'],
                  'threshold': (config['threshold'] if 'threshold' in
                      config.keys() else 0)}

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
        
        # gpr = GprPredictor(config['name'], self.database,
        #                 config['database_tags'],
        #                 self.kernels[config['kernel']])
        gpr = GprPredictor(config['name'], self.dataviews[config['data_view']],
                           self.kernels[config['kernel']])

        if 'threshold' in config.keys():
            gpr.threshold = config['threshold']

        if 'data_range' in config.keys():
            gpr.dataRange = (Bounds(config['data_range'][0],
                config['data_range'][1]),)
            gpr.updateRange = False

        self.maps[mapId] = ValueMap(config['name'], gpr)

        if 'std_map' in config.keys():
            # If std_map if defined in the config, creating a new StdMap with
            # the same GprPredictor as the above StdMap.
            if mapId+'_std' in self.maps.keys():
                warn("The map '"+mapId+"_std' id is already defined. Cannot "+
                     "instanciate '"+config['std_map']+"' map.")
            else:
                self.maps[mapId+'_std'] = StdMap(config['std_map'], gpr)

        if 'border_map' in config.keys():
            if mapId+'_border' in self.maps.keys():
                warn("The map '"+mapId+"_std' id is already defined. Cannot "+
                     "instanciate '"+config['border_map']+"' map.")
            else:
                if mapId+'_std' in self.maps.keys():
                    self.maps[mapId+'_border'] = BorderIncertitude(
                            config['border_map'], self.maps[mapId],
                            self.maps[mapId+'_std'])
                else:
                    self.maps[mapId+'_border'] = BorderRaw(config['border_map'],
                            self.maps[mapId])

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

            shallowParams = {} # this is because of sklean clone function
            if 'mean' in kernelConfig.keys():
                shallowParams['mean']      = kernelConfig['mean']
            if kernelConfig['type'] == 'WindKernel':
                shallowParams['windMap'] = self.windMap
            if len(shallowParams) > 0:
                params['shallowParameters'] = DeepcopyGuard(**shallowParams)

            # Kernel instanciation
            self.kernels[key] = KernelTypes[kernelConfig['type']](**params)
