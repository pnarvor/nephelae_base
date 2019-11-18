#! /usr/bin/python3

import yaml

filename = 'config_examples/full01.yaml'

config = None
with open(filename, 'r') as f:
    config = yaml.safe_load(f)

