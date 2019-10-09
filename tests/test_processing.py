import unittest
from datetime import datetime, timedelta
import numpy as np
from qclib.utils.navigation import velocity, KNOT2MPS, velocity_from_location_list
from tests.testdata import velocity_test_data


base_time = datetime.strptime('2017-01-12 14:08:06', '%Y-%m-%d %H:%M:%S')
d = timedelta(seconds=60)


def make_toy_data():
    latitude = ["56.2497", "56.2542", "56.2589", "56.2636", "56.2682", "56.2728", "56.2774", "56.2820", "56.2867",
                "56.2912"]
    longitude = ["11.3549", "11.3596", "11.3639", "11.3683", "11.3728", "11.3773", "11.3817", "11.3861", "11.3905",
                 "11.3950"]
    latitude = np.array(latitude).astype(float)
    longitude = np.array(longitude).astype(float)
    time = [base_time + d * i for i in range(0, len(longitude))]

    return time, longitude, latitude


class Tests(unittest.TestCase):

    def test_velocity_calculation(self):
        time, lon, lat = make_toy_data()
        vel = velocity(time, lon, lat) / KNOT2MPS
        ref_vel = [18.77790109, 19.02674804, 19.11822276, 18.89371568, 18.89320847, 18.79757968, 18.79709284,
                   19.11582111, 18.57509891]
        vel = list(np.around(np.array(vel), 8))
        assert vel == ref_vel

    def test_velocity_calculation_with_list_inputs(self):
        ref_vel = [1.81405198, 1.84044109, 1.42478698, 1.60458303, 1.59835892, 2.24388431,
                   1.66525115, 2.14261112, 1.75225005, 1.54525518]
        test_data = velocity_test_data.walk_test_data
        velocities = velocity([el[0] for el in test_data], [el[1] for el in test_data], [el[2] for el in test_data])
        assert np.allclose(ref_vel, velocities)

    def test_velocity_calculation_with_none(self):
        ref_vel = [1.81405198, 1.84044109, np.nan, np.nan, np.nan, 1.60458303, 1.59835892,
                   2.24388431, 1.66525115, np.nan, np.nan, 1.75225005, 1.54525518]
        test_data = velocity_test_data.test_data_with_nones
        print()
        assert all(np.isclose(a, b) for a, b in zip(ref_vel, velocity_from_location_list(test_data)) if not np.isnan(a))
