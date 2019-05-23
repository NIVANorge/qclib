from datetime import datetime
from typing import List, Dict, Tuple

import matplotlib as mpl
import numpy as np
from matplotlib import path


def is_inside_geo_region(locations: List[Tuple[datetime, float, float]],
                         area: Dict[str, Tuple[float, float, float, float]]) -> np.ndarray:
    lon = area['lon']
    lat = area['lat']
    number_of_points = len(lon)
    points_of_geo_region = np.ones([number_of_points + 1, 2], dtype=np.float64)
    points_of_geo_region[0:number_of_points, 0] = lon
    points_of_geo_region[0:number_of_points, 1] = lat
    points_of_geo_region[number_of_points, 0:2] = [lon[0], lat[0]]
    geo_region = mpl.path.Path(points_of_geo_region)
    pts = np.ones([len(locations), 2])
    pts[:, 0] = np.array(locations)[:, 1]
    pts[:, 1] = np.array(locations)[:, 2]
    inside = geo_region.contains_points(pts)
    return inside.astype(bool)
