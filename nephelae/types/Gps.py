from .Position      import Position
from .NavigationRef import NavigationRef

class Gps:

    def __init__(self, uavId, position, mode=3, course=0.0, speed=0.0,
                 climb=0.0, week=0, itow=0, utm_zone=31, gps_nb_err=0):
        
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
        # For compatibility with paparazzi Gps type
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
        if type(other) == NavigationRef:
            return self.position - other.position
        else:
            raise ValueError("Invalid operand type")

