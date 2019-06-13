'''
Reference: MATLAB script based on American Practical Navigator, Vol II, 1975 Edition, p 5
Modification of python script from Anna Birgitta Ledang
'''
import numpy as np
KNOT2MPS = 1852.0 / 3600.0


def latitude2meters(delta_latitude=None, average_latitude=None, latitude=None):
    if delta_latitude is None:
        delta_latitude = np.diff(latitude)
    if average_latitude is None:
        i1 = np.arange(1, len(latitude))
        i0 = i1 - 1
        average_latitude = 0.5 * (latitude[i0] + latitude[i1])
    average_latitude_radians = np.deg2rad(average_latitude)
    # length_of_degree at in meters, of a degree of the meridian
    length_of_degree = \
        111132.09 - 566.05 * np.cos(2 * average_latitude_radians) + 1.2 * np.cos(4 * average_latitude_radians)
    distance_y = length_of_degree * delta_latitude
    return distance_y


def longitude2meters(delta_longitude=None, average_latitude=None, longitude=None, latitude=None):
    if delta_longitude is None:
        delta_longitude = np.diff(longitude)
    if average_latitude is None:
        i1 = np.arange(1, len(latitude))
        i0 = i1 - 1
        average_latitude = 0.5 * (latitude[i0] + latitude[i1])
    average_latitude_radians = np.deg2rad(average_latitude)
    # length of degree depends on latitude
    length_of_degree = 111415.13 * np.cos(average_latitude_radians) - 94.55 * np.cos(3 * average_latitude_radians)
    distance_x = length_of_degree * delta_longitude
    return distance_x


def lonlat2meters(longitude, latitude):
    dx = longitude2meters(longitude=longitude, latitude=latitude)
    dy = latitude2meters(latitude=latitude)
    distance = np.sqrt(dx * dx + dy * dy)
    return distance


def dt2seconds(time):
    delta_time = np.diff(time)
    seconds = [x.total_seconds() for x in delta_time]
    return seconds


def velocity(time, lon, lat):
    " Finite difference , forward scheme "
    dt = dt2seconds(time)
    ds = lonlat2meters(lon, lat)
    vel = ds / dt
    return vel



