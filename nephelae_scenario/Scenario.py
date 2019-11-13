import yaml
import os

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

        self.localFrame    = None
        self.flightZone    = None
        self.uavs          = {}
        self.database      = None
        self.mesonhDataset = None
        self.maps          = None


    def load(self):
        self.config = self.parser.parse()
        
