#! /usr/bin/python3

import sys
sys.path.append('../../')

from nephelae_base.types import ObserverSubject
from nephelae_base.types import MultiObserverSubject

class Observer1:

    def __init__(self, data="Hello1"):
        self.data = data

    def notify1(self):
        print(self.data)


class Observer2:

    def __init__(self, data="Hello2"):
        self.data = data

    def notify2(self, arg):
        print(self.data, arg)


class Thingy1(ObserverSubject):

    def __init__(self):
        super().__init__('notify1')


class Thingy2(ObserverSubject):

    def __init__(self):
        super().__init__('notify2')


class Thingy3(MultiObserverSubject):

    def __init__(self):
        super().__init__(['notify1', 'notify2'])


thingy1 = Thingy1()
thingy2 = Thingy2()
thingy3 = Thingy3()

obs10 = Observer1()
obs11 = Observer1("Hello 11")
obs20 = Observer2()
obs21 = Observer2("Hello 22")

thingy1.attach_observer(obs10)
thingy1.attach_observer(obs11)

thingy2.attach_observer(obs20)
thingy2.attach_observer(obs21)

thingy3.attach_observer(obs10, 'notify1')
thingy3.attach_observer(obs11, 'notify1')
thingy3.attach_observer(obs20, 'notify2')
thingy3.attach_observer(obs21, 'notify2')


print("thingy1:")
try:
    # should fail
    thingy1.attach_observer(obs2)
except Exception as e:
    print("Ok : \"" + str(e) + "\"")
thingy1.notify1()

print("thingy2:")
thingy2.notify2("! Hi !")
try:
    # should fail
    thingy2.notify()
except Exception as e:
    print("Ok : \"" + str(e) + "\"")

print("thingy3:")
thingy3.notify1()
thingy3.notify2(" thingy3 !")

