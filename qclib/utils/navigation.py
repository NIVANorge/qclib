'''
Reference: MATLAB script based on American Practical Navigator, Vol II, 1975 Edition, p 5
Based on python script from Anna Birgitta Ledang
'''
import datetime
import numpy as np

KNOT2MPS = 1852.0 / 3600.0


def latitude2meters(dlat=None, alat=None, lat=None):
    if dlat is None:
        dlat = np.diff(lat)
    if alat is None:
        i1 = np.arange(1, len(lat))
        i0 = i1 - 1
        alat = 0.5 * (lat[i0] + lat[i1])
    rlat = np.deg2rad(alat)
    m = 111132.09 - 566.05 * np.cos(2 * rlat) + 1.2 * np.cos(4 * rlat)
    dy = m * dlat
    return dy


def longitude2meters(dlon=None, alat=None, lon=None, lat=None):
    if dlon is None:
        dlon = np.diff(lon)
    if alat is None:
        i1 = np.arange(1, len(lat))
        i0 = i1 - 1
        alat = 0.5 * (lat[i0] + lat[i1])
    rlat = np.deg2rad(alat)
    p = 111415.13 * np.cos(rlat) - 94.55 * np.cos(3 * rlat)
    dx = p * dlon
    return dx


def lonlat2meters(lon, lat):
    dx = longitude2meters(lon=lon, lat=lat)
    dy = latitude2meters(lat=lat)
    m = np.sqrt(dx * dx + dy * dy)
    return m


def dt2seconds(dt):
    test = False
    if isinstance(dt, np.ndarray) and (dt.dtype == datetime.timedelta):
        test = True
    elif isinstance(dt, list) and isinstance(dt[0], datetime.timedelta):
        test = True
    elif isinstance(dt, datetime.timedelta):
        test = True
    if test:
        s = map(lambda x: x.total_seconds(), dt)
    else:
        s = dt
    return s


def velocity(time, lon, lat):
    dt = dt2seconds(np.diff(time))
    ds = lonlat2meters(lon, lat)
    mps = ds / dt
    i1 = np.arange(1, len(mps))
    i0 = i1 - 1
    mps = 0.5 * (mps[i1] + mps[i0])
    mps = np.insert(mps, 0, np.nan)
    mps = np.append(mps, np.nan)
    return mps


def knot2mps(spd):
    return spd * KNOT2MPS

