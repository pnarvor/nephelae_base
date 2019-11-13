import yaml
import os


class YamlParser:

    """
    YamlParser

    Parse a set of yaml file for a Nephelae Scenario. It concatenates the
    yaml files for them to be treated as one.
    """

    def __init__(self, mainConfigFile):

        self.mainConfigFile = mainConfigFile
        self.configFiles    = {}
        self.yamlStream     = ""
        self.configRoot     = None


    def parse(self):
        self.__init__(self.mainConfigFile)
        self.__build_yaml()
        self.config = yaml.safe_load(self.yamlStream)

        return self.config
        

    def __build_yaml(self):

        """Builds a single yaml string by concatenating several yaml files"""
        
        with open(self.mainConfigFile, "r") as f:
            self.configFiles = yaml.safe_load(f)

        self.yamlStream = "# " + self.find_file(self.configFiles['head'])+'\n'
        with open(self.find_file(self.configFiles['head']), "r") as f:
            self.yamlStream = self.yamlStream + f.read() + '\n'

        if 'definitions' in self.configFiles.keys():
            self.__append_yaml(self.configFiles['definitions'])

        if 'aircrafts' in self.configFiles.keys():
            self.yamlStream = self.yamlStream + "aircrafts:\n"
            for filename in self.configFiles['aircrafts']:
                self.yamStream = self.yamlStream + ' - '
                self.__append_yaml(filename, prefix='    ')
                self.yamlStream = self.yamlStream + '\n'
        
        
    def __append_yaml(self, filename, prefix=''):
        filename = self.find_file(filename) 
        self.yamlStream = self.yamlStream + "# " + filename + '\n'
        with open(filename, 'r') as f:
            for line in f:
                if '---' in line:
                    continue
                self.yamlStream = self.yamlStream + prefix + line


    def find_file(self, path):
        """Find a file according to several search path (complete this)"""
        
        if os.path.exists(path):
            return path
        
        if self.configRoot is None:
            self.configRoot = os.path.split(self.mainConfigFile)[0]
        
        if os.path.exists(os.path.join(self.configRoot, path)):
            return os.path.join(self.configRoot, path)
        
        raise ValueError("File "+path+" was not found.")

