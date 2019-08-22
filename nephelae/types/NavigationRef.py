from .Position import Position

class NavigationRef:


    def __init__(self, position=Position(0,0,0,0), utm_zone=31):
        self.position = position
        self.utm_zone = utm_zone


    def __str__(self):
        return "NavigationRef : "+str(self.position)+", utm_zone : "+str(self.utm_zone)


    def __getattr__(self, name):
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


