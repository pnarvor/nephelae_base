

class Bounds:
    
    """Bounds

    Convenience class to store a min and a max value with
    helper update member functions
    """

    def from_array(array):
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
        self.min = minValue
        self.max = maxValue
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "bounds : [min: "+str(self.min) + ", max: "+str(self.max)+"]"

    def update(self, value):
        if self.min is None:
            self.min = value
        else:
            self.min = min(self.min, value)
        if self.max is None:
            self.max = value
        else:
            self.max = max(self.max, value)

    def reset(self):
        self.min = None
        self.max = None



