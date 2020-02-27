import numpy as np

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


