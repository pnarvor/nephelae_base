

class Bounds:
    
    """Bounds

    Convenience class to store a min and a max value with
    helper update member functions
    """

    def __init__(self, value=None):
        self.min = value
        self.max = value
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "min: "+str(self.min) + ", max: "+str(self.max)

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



