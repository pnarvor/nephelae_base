import numpy as np

class Position(object):

    """
    Position

    Simple type for 4D space-time vector manipulation. The dimension order
    in the vector is (t,x,y,z).

    Access to dimensions should be only through the __getattr__ and __setattr__
    methods. For example to set the x dim value to 14.0 : position.x = 14.0 .

    /!\ Trying to access directly Position.data will raise a ValueError
    exception as if data were not a Position attribute (see it as a strong
    private attribute).

    More details on __setattr__ and __getattr__ in their respective definitions.

    Attributes
    ----------
    data : numpy.array (shape=(4,)), private attribute
        Hold the (t,x,y,z) values. Rational of having a vector instead of
        separated t,x,y,z attributes is to be able to use numpy algebra.

        However setting or getting t,x,y,z values is done as if
        self.t, self.x, self.y, self.z where attributes of Position thanks
        to the __setattr__ and __getattr__ methods. Example : setting the x
        dimension value to 14.0 is done as such : position.x = 14.0

        /!\ Trying to access directly Position.data will raise a ValueError
        exception as if data were not a Position attribute (see it as a strong
        private attribute).


    Methods
    -------
    __add__, __sub__ -> Position:
        Addition or subtraction of Position objects.

    __mult__ -> scalar:
        Dot product of two position or
        matrix multiplication, depending on parameter.

    __eq__, __ne__ -> bool:
        Comparison operator. Two Position are equal if and only
        if norm(v1 - v2) = 0.0 .

    __getattr__ -> None:
        Get a dimension value. (ex: xvalue = position.x, effectively call
        xvalue = position.__getattr__('x'), and is equivalent to
        xvalue = position.data[1]).

    __setattr__ -> None:
        Set a dimension value. (ex: position.x = 14.0 will effectively call
        position.__setattr__('x', 14.0), and is equivalent to
        position.data[1] = 14.0).

    to_list -> list(scalar):
        Returns [self.t, self.x, self.y, self.z].
    """

    def __init__(self, t=0.0, x=0.0, y=0.0, z=0.0):

        """
        Parameters
        ----------
        t : scalar, or Position, or list, or numpy.array .
            scalar : self.t (self.data[0]) set to t.
            Position : self.data is set to t.data (x,y,z ignored).
            list : self.data is set to numpy.array(t) (x,y,z ignored).
            numpy.array : self.data is set to t.
                          raise Exception if t.shape != (4,).
        x,y,z : scalar
            self.x (self.data[1]) set to x.
            self.y (self.data[2]) set to y.
            self.z (self.data[3]) set to z.
            Ignored if t is not a scalar.
        """

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
        """Add two Position."""
        return Position(self.data + other.data)


    def __sub__(self, other):
        """Subtract two Position."""
        return Position(self.data - other.data)


    def __mul__(self, other):
        """Dot product of two Position, or matrix multiplication"""
        if type(other) == Position:
            return np.dot(self.data, other.data)
        else:
            return Position(self.data*other)


    def __eq__(self, other):
        """Compare two Position. (True if norm(self - other) == 0.0)"""
        return np.array_equal(self.data, other.data)


    def __ne__(self, other):
        """Compare two Position. (True if norm(self - other) != 0.0)"""
        return not np.array_equal(self.data, other.data)


    def __getattr__(self, name):
        """Get self.{name}. name can only be 't','x','y' or 'z'"""
        if name == 't':
            return self.data[0]
        if name == 'x':
            return self.data[1]
        if name == 'y':
            return self.data[2]
        if name == 'z':
            return self.data[3]
        raise ValueError("Position has no attribute '" + name + "'")


    def __setattr__(self, name, value):
        """Set self.{name} to value. name can only be 't','x','y' or 'z'"""
        if name == 't':
            self.data[0] = value
        elif name == 'x':
            self.data[1] = value
        elif name == 'y':
            self.data[2] = value
        elif name == 'z':
            self.data[3] = value
        else:
            raise ValueError("'Position' object has no attribute '" + name + "'")


    def __getstate__(self):
        """For serialization (pickling) purposes."""
        return self.data


    def __setstate__(self, data):
        """For serialization (unpickling) purposes."""
        super().__setattr__('data', data)

    def to_list(self):
        """Returns [self.t, self.x, self.y, self.z]"""
        return list(self.data)


