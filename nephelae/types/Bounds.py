

class Bounds:
    
    """
    Bounds

    Convenience class to store a min and a max value with
    helper update member functions. (mostly for shorten code when used used).

    Attributes
    ----------

    min : comparable value (float, int...)
        current min value

    max : comparable value (float, int...)
        current max value


    Methods
    -------

    update(value) -> None:
        Update min and max attributes with respect to value

    reset() -> None:
        Set min and max attributes to None. (Next update, min and max
        attributes will be equal to value).


    Class methods
    -------------

    from_array(array) -> None or Bounds or [Bounds]:
        Builds a new Bound object from an array. Returns None if the array is empty.
        Returns a list of Bounds if the array has more than 1 dimension.
    """

    def from_array(array):

        """Builds a new Bound object from an array

        Parameters
        ----------
        array : N-D iterable with comparable elements (list, numpy.array...)
            Array to search for bounds. Can have more than 1 dimension.

        Returns
        -------
        None
            If array was empty
        Bounds
            A single Bounds object id the array was 1D
        list
            A list of Bounds object or of lists of Bounds object if the array
            was more than 1D
        """

        if len(array.shape) == 0:
            return None
        elif len(array.shape) == 1:
            res = Bounds()
            for v in array:
                res.update(v)
            return res
        else:
            res = []
            for l in array:
                res.append(Bounds.from_array(l))
            return res
        

    def __init__(self, minValue=None, maxValue=None):
        """
        Parameters
        ----------
        minValue : comparable value (float, int...)
            Initial value of self.min
        maxValue : comparable value (float, int...)
            Initial value of self.max
        """
        self.min = minValue
        self.max = maxValue
   

    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return "bounds : [min: "+str(self.min) + ", max: "+str(self.max)+"]"


    def update(self, value):
        """Updates min and max attributes with respect to value."""
        if self.min is None:
            self.min = value
        else:
            self.min = min(self.min, value)
        if self.max is None:
            self.max = value
        else:
            self.max = max(self.max, value)


    def reset(self):
        """Set min and max attributes to None (will take the next update value)."""
        self.min = None
        self.max = None


    def span(self):
        """Returns difference between max and min atributes."""
        return self.max - self.min



