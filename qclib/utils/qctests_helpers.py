import matplotlib as mpl
import numpy as np


def is_inside_geo_region(longitude, latitude, **opts)->bool:

    lon = opts['area']['lon']
    lat = opts['area']['lat']
    number_of_points = len(lon)
    points_of_geo_region = np.ones([number_of_points + 1, 2], dtype=np.float64)
    points_of_geo_region[0:number_of_points, 0] = lon
    points_of_geo_region[0:number_of_points, 1] = lat
    points_of_geo_region[number_of_points, 0:2] = [lon[0], lat[0]]
    geo_region = mpl.path.Path(points_of_geo_region)
    current_geo_point = [[longitude, latitude]]
    inside = geo_region.contains_points(current_geo_point)
    return inside

