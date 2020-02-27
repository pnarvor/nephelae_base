import numpy as np
from PIL import Image

from .TimedData import TimedData


def heading_to_trigo(deg):
    """
    Converts a paparazzi heading or course value given as clockwise angle
    relative to the north in degrees to an anti-clockwise angle relative to
    east in radians.
    """
    return np.pi / 2 - np.pi * deg / 180.0


def estimate_wind(database, aircraft, timeInterval):
    """
    Least square advective wind estimation (average of wind vector in x,y
    plane). Based on the ground velocity vector measured by the GPS, the
    airspeed measured by the pitot tube, and the heading of the aircraft (angle
    in x,y plane).
    """
    
    keys = (slice(timeInterval[0], timeInterval[-1]),)
    course       = TimedData.from_database(database, ['10', 'STATUS'],   keys, 'course',       lambda x: x.data.course)
    heading      = TimedData.from_database(database, ['10', 'STATUS'],   keys, 'heading',      lambda x: x.data.heading)
    ground_speed = TimedData.from_database(database, ['10', 'STATUS'],   keys, 'ground_speed', lambda x: x.data.speed)
    airspeed     = TimedData.from_database(database, ['10', 'airspeed'], keys, 'airspeed',     lambda x: x.data.data[0])
    airspeed.sync_on(ground_speed)
    T = len(airspeed.data) # number of samples on which the estimation will be done
    
    # Unit vector pointing to the front of the aircraft
    vh = np.empty([T, 2])
    vh[:,0] = np.cos(heading_to_trigo(heading.data))
    vh[:,1] = np.sin(heading_to_trigo(heading.data))
   
    # (x,y) ground velocity vector
    vg = np.empty([T, 2])
    vg[:,0] = ground_speed.data * np.cos(heading_to_trigo(course.data))
    vg[:,1] = ground_speed.data * np.sin(heading_to_trigo(course.data))
        
    # airspeed
    a = airspeed.data
    
    # Least square wind estimation. (finding the best x,y wind vector that
    # projected on the aircraft heading, gives on average the value closest to
    # the measured airspeed).
    A = vh.T @ vh
    y = (np.sum(vh * vg, axis=1) - a).T @ vh
    wind = np.linalg.solve(A, y)

    seqm = np.sqrt(np.mean((np.sum(vh*(vg - np.ones([T,1])*wind.T), axis=1) - a)**2))

    return wind, seqm


def voltage_fit_parameters_estimation(database, aircraft, cloud_channel, timeInterval):
    """
    Find linear fit parameter of aircraft battery voltage in cloud sensor
    measurements.
    """

    # Keys for a search in the database (tuple of slices)
    keys = (slice(timeInterval[0], timeInterval[-1]),)
    cloud   = TimedData.from_database(database, [cloud_channel, aircraft], keys, dataFetchFunc=lambda x: x.data.data[0])
    voltage = TimedData.from_database(database,      ['energy', aircraft], keys, dataFetchFunc=lambda x: x.data.data[1])

    # resampling (interpolating) the voltage data to synchronize with cloud data
    voltage.sync_on(cloud)

    # Least square linear fit of battery voltage to cloud data
    y = cloud.data   - np.mean(cloud.data)
    x = voltage.data - np.mean(voltage.data)
    alpha = np.dot(y,x) / np.dot(x,x)
    beta  = np.mean(cloud.data) - alpha*np.mean(voltage.data)

    return alpha, beta


def aircraft_position_at_time(database, aircraft, t):
    """
    Returns aircraft position at time t as a (t,x,y,z) numpy.array.
    """

    status   = database[aircraft, 'STATUS'](sortCriteria=lambda x: x.position.t)[:]
    position = np.array([[e.position.t, e.position.x, e.position.y, e.position.z] for e in status])
    idx = np.where(np.abs(position[:,0] - t) == np.min(np.abs(position[:,0] - t)))
    
    return position[idx,:].squeeze()


def keys_from_position(position, width, height=None):
    """
    Generate a set of keys suitable to be used on a map generator to get a
    horizontal rectangular slice of a (t,x,y,z) space centered on position.
    (Returns a tuple (float, slice, slice, float).
    """

    if height is None:
        height = width
    return (position[0],
            slice(position[1] - width/2,  position[1] + width/2),
            slice(position[2] - height/2, position[2] + height/2),
            position[3])


def display_scaled_array(array, axes=None, resample=None, rng=None):
    if axes is None:
        fig, axes = plt.subplots(1,1)

    data = array.data.squeeze().T

    if resample is not None:
        newShape = (data.shape[0]*resample, data.shape[1]*resample)
        data = np.array(Image.fromarray(data).resize(newShape, Image.BICUBIC))

    bounds = array.bounds
    extent=[bounds[0].min, bounds[0].max, bounds[1].min, bounds[1].max]

    options={}
    if rng is not None:
        options['vmin'] = rng[0]
        options['vmax'] = rng[-1]
    
    axes.imshow(data, origin='lower', extent=extent, aspect='equal', **options)

