"""
nephelae.type package

Contains a bunch of base types used in Nephelae libraries.
"""

from .Position      import Position
from .SensorSample  import SensorSample
from .Gps           import Gps
from .NavigationRef import NavigationRef

from .DataShape import DimensionShape # deprecated
from .DataShape import Shape4D # deprecated
from .Bounds    import Bounds

from .ObserverPattern import ObserverSubject
from .ObserverPattern import MultiObserverSubject
from .Pluginable      import Pluginable

from .DeepcopyGuard import DeepcopyGuard

from .DataContainer import TimedData
