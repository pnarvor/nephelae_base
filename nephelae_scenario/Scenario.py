import yaml
import os
import time

from nephelae.types     import NavigationRef, Position
from nephelae.database  import NephelaeDataServer
from nephelae_paparazzi import build_aircraft, AircraftLogger

from .YamlParser import YamlParser

class Scenario:

    """
    Scenario

    This is a class holding all the components for a Nephelae run.

    Its main goals are :
        - Holding all nephelae components (database, mesonh, uavs...)
        - All are loaded from config files written in yaml

    """

    def __init__(self, mainConfigPath):
        
        self.parser = YamlParser(mainConfigPath)
        
        self.missionTime = None
        self.localFrame  = None
        self.flightArea  = None
        self.aircrafts   = {}
        self.database    = None
        self.mesonhFiles = None
        self.maps        = None
        self.logger      = AircraftLogger(quiet=True)


    def load(self):
        
        self.config = self.parser.parse()

        # Using current time as global mission time
        self.missionTime = time.time()
        ref = Position(self.missionTime,
                       self.config['local_frame']['east'],
                       self.config['local_frame']['north'],
                       self.config['local_frame']['alt'])
        self.localFrame = NavigationRef(ref)
        self.flightArea = self.config['flight_area']
        
        self.database = NephelaeDataServer()

        # TODO
        # try:
        #     if self.config['database']['enable_save']:
        #         self.database.enable_periodic_save(
        #             self.config['database']['enable_save'])
        # except KeyError:
        #     pass
        
        if 'mesonh_files' in self.config.keys():
            self.mesonhFile = self.config['mesonh_files']
        
        for key in self.config['aircrafts']:
            aircraft = build_aircraft(str(key), self.localFrame,
                                      self.config['aircrafts'])
            aircraft.add_gps_observer(self.logger)
            aircraft.add_status_observer(self.logger)
            aircraft.add_sensor_observer(self.logger)
            self.aircrafts[str(key)] = aircraft

    def start():
        for aircraft in self.aircrafts.values():
            aircraft.start()
    
    def stop():
        for aircraft in self.aircrafts.values():
            aircraft.stop()
