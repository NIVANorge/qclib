import unittest
from datetime import datetime
from qclib.utils.qc_input import QCInput_df, QCInput, Measurement
from qclib.utils.validate_input import validate_additional_data, has_duplicates
from qclib.utils.transform_input import transform_input_to_df
import qclib.Platforms
import pandas as pd

from qclib.utils.validate_input import validate_additional_data


def _date(datestring):
    return datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S")


class ValidateInput(unittest.TestCase):
    def setUp(self):
        self.qcinput = QCInput(value=10, timestamp=datetime(2017, 1, 12, 14, 10, 6), longitude=61, latitude=10,
                               historical_data=[Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                                Measurement(value=12.0, datetime=datetime(2017, 1, 12, 14, 8, 6)),
                                                Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 7, 6)),
                                                Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 9, 6))],
                               future_data=[
                                   Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 12, 6)),
                                   Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 11, 6))])

        self.qcinput_gaps = QCInput(value=10, timestamp=datetime(2017, 1, 12, 14, 10, 6), longitude=61, latitude=10,
                                    historical_data=[Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                                     Measurement(value=12.0, datetime=datetime(2017, 1, 12, 12, 8, 6)),
                                                     Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 7, 6)),
                                                     Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 9, 6))],
                                    future_data=[
                                        Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 12, 6)),
                                        Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 11, 6))])
        self.qcinput_duplicates = QCInput(value=10, timestamp=datetime(2017, 1, 12, 14, 10, 6), longitude=61, latitude=10,
                                    historical_data=[Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                                     Measurement(value=12.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                                     Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 7, 6)),
                                                     Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 9, 6))],
                                    future_data=[
                                        Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 12, 6)),
                                        Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 11, 6))])

    def test_should_work_with_arbitrary_sort_order(self):
        qcinput_df = transform_input_to_df(self.qcinput)
        self.assertEqual(validate_additional_data(qclib.Platforms.FerryboxQC, qcinput_df), True)

    def test_should_detect_time_gaps(self):
        qcinput_df = transform_input_to_df(self.qcinput_gaps)
        self.assertEqual(validate_additional_data(qclib.Platforms.FerryboxQC, qcinput_df), False)
        self.assertEqual(len(qcinput_df.historical_data), 0)

    def test_should_detect_duplicates(self):
        qcinput_df = transform_input_to_df(self.qcinput_duplicates)
        self.assertEqual(has_duplicates(qcinput_df.historical_data), True)


if __name__ == '__main__':
    unittest.main()
