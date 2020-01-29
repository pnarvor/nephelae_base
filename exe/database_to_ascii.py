#! /usr/bin/python3

import argparse

from nephelae.database import NephelaeDataServer

parser = argparse.ArgumentParser(description='Converts a NephelaeDataServer binary file to ASCII')
parser.add_argument('inputpath', type=str,
                    help="Path to database to be converted.")
parser.add_argument('-o', '--outputpath', dest='outputpath', type=str, default=None,
                    help="File to write the output to (default is stdout)")
args = parser.parse_args()

# database = NephelaeDataServer.load('/home/pnarvor/work/nephelae/data/barbados/logs/flight_01_28_02/database/database01.neph')
database = NephelaeDataServer.load(args.inputpath)
data = [entry.data for entry in database['STATUS'][:]]
data = data + [entry.data for entry in database['SAMPLE'][:]]
data.sort(key=lambda x: x.position.t)

if args.outputpath is None:
    print(database.navFrame.one_line_str())
    for datum in data:
        print(datum.one_line_str())
else:
    with open(args.outputpath, 'w') as f:
        f.write(database.navFrame.one_line_str() + '\n')
        for datum in data:
            f.write(datum.one_line_str() + '\n')
            print(datum.one_line_str())

