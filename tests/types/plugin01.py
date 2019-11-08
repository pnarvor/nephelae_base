#! /usr/bin/python3

import sys
sys.path.append('../../')

from nephelae.types import Pluginable


class BaseClass(Pluginable):

    def __init__(self, value):
        self.baseValue = value

    def display1(self):
        print("Base class display1 :", self.baseValue)

    def display2(self):
        print("Base class display2 :", self.baseValue)

    def display3(self):
        print("Base class display3 :", self.baseValue)


class Plugin:

    def __pluginmethods__():
        return [{'name'         : 'display1',
                 'method'       : Plugin.display1,
                 'conflictMode' : 'append'},
                {'name'         : 'display2',
                 'method'       : Plugin.display2,
                 'conflictMode' : 'prepend'},
                {'name'         : 'display3',
                 'method'       : Plugin.display3,
                 'conflictMode' : 'replace'},
                {'name'         : 'display4',
                 'method'       : Plugin.display4,
                 'conflictMode' : 'abort'},
                 ]

    def __initplugin__(self, value):
        self.pluginValue = value

    def display1(self):
        print("Plugin class display1 :", self.pluginValue, self.baseValue)

    def display2(self):
        print("Plugin class display2 :", self.pluginValue, self.baseValue)

    def display3(self):
        print("Plugin class display3 :", self.pluginValue, self.baseValue)

    def display4(self):
        print("Plugin class display4 :", self.pluginValue, self.baseValue)



b0 = BaseClass(1)
b0.load_plugin(Plugin, 2)
print(b0.display1(), end='\n\n')
print(b0.display2(), end='\n\n')
print(b0.display3(), end='\n\n')
print(b0.display4(), end='\n\n')



