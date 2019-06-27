from .Position import Position

class SensorSample:

    def __init__(self, variableName='noname', stamp=0,
                       position=Position(), data=[]):

        self.variableName = name
        self.stamp        = stamp
        self.position     = position
        self.data         = data

    def __str__(self):
        return ("SensorSample:"+
                "\n  variable name : "  + str(self.variableName) +
                "\n  stamp         : "  + str(self.stamp) +
                "\n  position      : "  + str(self.position) +
                "\n  data          :\n" + str(self.data) + "\n")



