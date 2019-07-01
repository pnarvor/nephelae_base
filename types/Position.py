import numpy as np

class Position(object):

    """Position
    Simple type for 4D space-time vector manipulation
    """

    def __init__(self, t=0.0, x=0.0, y=0.0, z=0.0):
        if type(t) == list:
                self.__init__(np.array(t))
        elif type(t) == Position:
                self.__init__(t.data)
        elif type(t) == np.ndarray:
            if not t.shape == (4,):
                raise Exception("Position : invalid vector shape as constructor argument")
            super().__setattr__('data', np.array(t))
        else:
            super().__setattr__('data', np.array([float(t),float(x),float(y),float(z)]))

    def __repr__(self):
        return "Position (t,x,y,z)"

    def __str__(self):
        return ('(t: ' + str(self.t) +
               ', x: ' + str(self.x) +
               ', y: ' + str(self.y) +
               ', z: ' + str(self.z) + ')')

    def __add__(self, other):
        return Position(self.data + other.data)
    
    def __sub__(self, other):
        return Position(self.data - other.data)

    def __mul__(self, other):
        if type(other) == Position:
            return np.dot(self.data, other.data)
        else:
            return Position(self.data*other)

    def __getattr__(self, name):
        if name == 't':
            return self.data[0]
        if name == 'x':
            return self.data[1]
        if name == 'y':
            return self.data[2]
        if name == 'z':
            return self.data[3]
        raise AttributeError("Position has no attribute '" + name + "'")

    def __setattr__(self, name, value):
        if name == 't':
            self.data[0] = value
        elif name == 'x':
            self.data[1] = value
        elif name == 'y':
            self.data[2] = value
        elif name == 'z':
            self.data[3] = value
        else:
            raise AttributeError("'Position' object has no attribute '" + name + "'")




