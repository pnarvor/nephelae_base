#! /usr/bin/python3

import sys
sys.path.append('../../')

from nephelae_scenario import Scenario


scenario = Scenario('config_examples/main01.yaml')
scenario.load()

print(scenario.parser.yamlStream)
print(scenario.config)
