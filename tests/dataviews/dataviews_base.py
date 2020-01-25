#! /usr/bin/python3

import sys
sys.path.append('../../')

from nephelae.dataviews import DataView

class StringView(DataView):

    def __init__(self, string, parents=[]):
        super().__init__(parents)
        self.string = string

    def process_notified_sample(self, sample):
        print(self.string, sample, flush=True)
        return sample

    def process_fetched_samples(self, samples):
        return samples


class LeafView(StringView):

    def __init__(self, string, l):
        super().__init__(string)
        self.l = l

    def process_fetched_samples(self, samples):
        return self.l
    

dataview0 = LeafView('n1', ['data0', 'data1'])
dataview1 = LeafView('n2', ['dada0', 'dada1'])
dataview2 = StringView('n3', parents=[dataview0, dataview1])

dataview0.add_sample('sample1')
print('')
dataview1.add_sample('sample2')
print('')
dataview2.add_sample('sample3')


print('')
print(dataview2[1:1])

