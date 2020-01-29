from .Position import Position

class SensorSample:
    
    """
    SensorSample

    Holds a data sample with its metadata.
    Mostly to be used in SpatializedDatabase.

    Attributes
    ----------

    variableName : str
        Identifier for the sample (ex: 'temperature', 'windVector'...).

    producer : str
        Identifier of the producer of this particular sample (ex: a UAV id).

    timeStamp : int
        Acquisition date of the sample (in milliseconds).

    position : types.Position
        Location of acquisition of the sample.
        position.t should be the timeStamp of the measure of the sensor location.
        ex: GPS location closest to acquisition time (self.timestamp).

    data :
        Sample data.
        Sample data type is undefined for now but an array of float is advised.
        (TODO fix this type.)
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


    def one_line_str(self):
        output = "SensorSample_" + self.producer + ", " +\
                 self.variableName               + ", " +\
                 str(self.position.t)            + ", " +\
                 str(self.position.x)            + ", " +\
                 str(self.position.y)            + ", " +\
                 str(self.position.z)
        for value in self.data:
            output = output + ", " + str(value)
        return output






