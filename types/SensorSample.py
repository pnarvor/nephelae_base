from .Position import Position

class SensorSample:
    
    """SensorSample

    Holds a single data sample (can be of any type) with its metadata

    Attributes:

        variableName     (string): Identifier for the sample (ex: 'temperature', 'windVector').
        timeStamp           (int): Date of acquisition of the sample (in milliseconds)
        position (types.Position): Location of acquisition of the sample.
                                   (position.t is the timeStamp of the measure of the sensor location, ex: gps measurement.)
        data          (undefined): Sample data type is undefined for now but an array of float is advised.
    """

    def __init__(self, variableName='noname', producer='unknown', timeStamp=0,
                       position=Position(), data=[]):

        self.variableName = variableName
        self.producer     = producer
        self.timeStamp    = timeStamp
        self.position     = position
        self.data         = data

    def __str__(self):
        return ("SensorSample:"+
                "\n  variable name : " + str(self.variableName) +
                "\n  producer      : " + str(self.producer) +
                "\n  timeStamp     : " + str(self.timeStamp) +
                "\n  position      : " + str(self.position) +
                "\n  data          : " + str(self.data) + "\n")



