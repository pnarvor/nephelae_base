from .Position import Position

class NavigationRef:

    """
    NavigationRef

    Local frame position. Roughly a copy of Paparazzi NAVIGATION_REF message.
    TODO make this independent of Paparazzi.

    Attributes
    ----------
    position : types.Position
        GPS position of the local frame in UTM coordinate system.
        position.t : Origin of time (start of mission ?)
        position.x : UTM east coordinate.
        position.y : UTM north coordinate.
        position.z : Altitude (from sea level).

    utm_zone : str?, int?
        UTM zone of the local frame (NOT USED).

    Methods
    -------
    __getattr__(name) -> float:
        Retrieve either 'stamp', 'utm_east', 'utm_north' or 'alt' of
        reference frame. 'stamp' is the mission start time.
    """

    def __init__(self, position=Position(0,0,0,0), utm_zone=31):
        """
        Parameters
        ----------
        position : types.Position
            GPS position of the local frame in UTM coordinate system.
            position.t : Origin of time (start of mission ?)
            position.x : UTM east coordinate.
            position.y : UTM north coordinate.
            position.z : Altitude (from sea level).

        utm_zone : str?, int?
            UTM zone of the local frame (NOT USED, can be omited without
            consequences).
        """
        self.position = position
        self.utm_zone = utm_zone
        

    def __str__(self):
        return "NavigationRef : "+str(self.position)+", utm_zone : "+str(self.utm_zone)


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
        # For compatibility with paparazzi Gps type
        if name == 'stamp':
            return self.position.t
        if name == 'utm_east':
            return self.position.x
        if name == 'utm_north':
            return self.position.y
        if name == 'ground_alt':
            return self.position.z
        else:
            raise AttributeError("Gps has no attribute '"+name+"'")


    def __getitem__(self, key):
        return self.__getattr__(key)


