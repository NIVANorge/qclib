import unittest
import qclib.utils.Thresholds as th
from qclib.utils.qctests_helpers import is_inside_geo_region


class ValidateQCHelpers(unittest.TestCase):

    def setUp(self):
        self.location1 = {"lon": 12, "lat": 45}
        self.true_geo_regions_location1 = {"Baltic": False, "NW_Shelf": False, "SW_Shelf": False, "NorthSea": False,
                                           "Arctic": False, "Iberic": False, "MedSea": True, "BlackSea": False,
                                           "Biscay": False, "W_GulfFinland": False, "S_BalticProper": False,
                                           "N_BalticProper": False}

    def test_is_inside_geo_region(self):
        geo_regions = {"Baltic": th.Baltic, "NW_Shelf": th.NW_Shelf, "SW_Shelf": th.SW_Shelf, "NorthSea": th.NorthSea,
                       "Arctic": th.Arctic, "Iberic": th.Iberic, "MedSea": th.MedSea, "BlackSea": th.BlackSea,
                       "Biscay": th.Biscay, "W_GulfFinland": th.W_GulfFinland, "S_BalticProper": th.S_BalticProper,
                       "N_BalticProper": th.N_BalticProper}

        result_geo_region = {}
        opts = {"area": {}}
        for region, threshold in geo_regions.items():
            opts["area"] = threshold
            result_geo_region[region] = is_inside_geo_region(self.location1["lon"], self.location1["lat"], **opts)

        self.assertEqual(result_geo_region, self.true_geo_regions_location1, "Wrong location")


if __name__ == '__main__':
    unittest.main()
