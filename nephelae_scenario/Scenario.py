import yaml
import os
import time

from nephelae.types             import NavigationRef, Position, Pluginable
from nephelae.database          import NephelaeDataServer
from nephelae_paparazzi         import build_aircraft
from nephelae_paparazzi.plugins import WindSimulation

from .YamlParser import YamlParser

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
        
        self.missionT0   = None
        self.localFrame  = None
        self.flightArea  = None
        self.aircrafts   = {}
        self.database    = None
        self.mesonhFiles = None
        self.maps        = None
        self.running     = False


    def load(self):
        
        self.config = self.parser.parse()

        # Using current time as global mission time
        self.missionT0 = time.time()
        ref = Position(self.missionT0,
                       self.config['local_frame']['east'],
                       self.config['local_frame']['north'],
                       self.config['local_frame']['alt'])
        self.localFrame = NavigationRef(ref)
        self.flightArea = self.config['flight_area']
        
        self.database = self.configure_database()
            
        if 'mesonh_files' in self.config.keys():
            self.mesonhFiles = self.config['mesonh_files']
        
        for key in self.config['aircrafts']:
            aircraft = build_aircraft(str(key), self.localFrame,
                                      self.config['aircrafts'])
            aircraft.add_gps_observer(self.database)
            if hasattr(aircraft, 'add_sensor_observer'):
                aircraft.add_sensor_observer(self.database)
            self.aircrafts[str(key)] = aircraft

        if 'wind_feedback' in self.config.keys():
            if self.config['wind_feedback']:
                self.load_plugin(WindSimulation, self.mesonhFiles)
                                 

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

