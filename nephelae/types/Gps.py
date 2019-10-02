from .Position      import Position
from .NavigationRef import NavigationRef

class Gps:

    """
    Gps

    Local copy of Paparazzi Gps type. 
    TODO make this independent of Paparazzi.

    Attributes
    ----------
    uavId : str
        Identifier of the UAV related to this GPS position.

    position : types.Position
        GPS position in UTM coordinate system.
        position.t : time of GPS measurement.
        position.x : UTM east coordinate.
        position.y : UTM north coordinate.
        position.z : Altitude (from sea level).

    All other attributes are derived from Paparazzi GPS message.
    (see here: http://docs.paparazziuav.org/latest/paparazzi_messages.html).

    Methods
    -------
    __getattr__(name) -> float:
        Retrieve either 'stamp', 'utm_east', 'utm_north' or 'alt' of
        GPS position.

    __sub__(other) -> types.Position:
        Returns GPS position in local frame.
        /!\ Roughly returns self.position - other.position BUT
        altitude (result.z) is kept relative to sea level regardless of
        other.z. (TODO check and maybe change that).
    """


    def __init__(self, uavId, position, mode=3, course=0.0, speed=0.0,
                 climb=0.0, week=0, itow=0, utm_zone=31, gps_nb_err=0):
        
        """
        Parameters
        ----------
        uavId : str
            Identifier of the UAV related to this GPS position.

        position : types.Position
            GPS position in UTM coordinate system.
            position.t : time of GPS measurement.
            position.x : UTM east coordinate.
            position.y : UTM north coordinate.
            position.z : Altitude (from sea level).
       
        Other parameters/attributes are for compatibility with Paparazzi
        Gps message. Subject to change.
        """
        
        self.uavId    = uavId
        self.position = position

        # For compatibility with nephelae_paparazzi.Gps type
        self.mode       = mode
        self.course     = course
        self.speed      = speed
        self.climb      = climb
        self.week       = week
        self.itow       = itow
        self.utm_zone   = utm_zone
        self.gps_nb_err = gps_nb_err


    def __str__(self):
        return "Gps " + self.uavId + " : " + str(self.position)


    def __getattr__(self, name):
        """
        Retrieve either 'stamp', 'utm_east', 'utm_north' or 'alt' of
        GPS position. Respectively aliases to self.position.t,
        self.position.x, self.position.y ans self.position.z.

        Parameters
        ----------

        name : str
            Name of the attribute to retrieve.
        """
        # For compatibility with Paparazzi Gps type
        if name == 'stamp':
            return self.position.t
        if name == 'utm_east':
            return self.position.x
        if name == 'utm_north':
            return self.position.y
        if name == 'alt':
            return self.position.z
        else:
            raise AttributeError("Gps has no attribute '"+name+"'")


    def __sub__(self, other):
        """
        Returns GPS position in local frame.

        other : types.NavigationRef
            Usually represente a UTM position near the UAV landing site.

            /!\ Roughly returns self.position - other.position BUT
            altitude (result.z) is kept relative to sea level regardless of
            other.z. (TODO check and maybe change that).
        """

        if type(other) == NavigationRef:
            res = self.position - other.position
            res.z = self.position.z
            return res
        else:
            raise ValueError("Invalid operand type")

