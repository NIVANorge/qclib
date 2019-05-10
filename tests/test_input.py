import unittest
from datetime import datetime
from qclib.utils.qc_input import QCInput, Measurement
from qclib.utils.transform_input import transform_input_to_df
import qclib.Platforms
from qclib.utils.validate_input import remove_data_after_time_gap, validate_additional_data, has_duplicates


def _date(datestring):
    return datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S")


class ValidateInput(unittest.TestCase):
    def setUp(self):
        self.qcinput = QCInput(value=10, timestamp=datetime(2017, 1, 12, 14, 10, 6), longitude=61, latitude=10,
                               historical_data=[Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                                Measurement(value=12.0, datetime=datetime(2017, 1, 12, 14, 7, 6)),
                                                Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 8, 6)),
                                                Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 9, 6))],
                               future_data=[
                                   Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 11, 6)),
                                   Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 12, 6))])

        self.qcinput_gaps = QCInput(value=10, timestamp=datetime(2017, 1, 12, 14, 10, 6), longitude=61, latitude=10,
                                    historical_data=[Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 9, 6))],
                                    future_data=[
                                        Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 15, 6))])
        self.qcinput_gaps1 = QCInput(value=10, timestamp=datetime(2017, 1, 12, 14, 10, 6), longitude=61, latitude=10,
                                     historical_data=[Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 5, 6)),
                                                      Measurement(value=12.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                                      Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 8, 6)),
                                                      Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 9, 6))],
                                     future_data=[
                                         Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 11, 6)),
                                         Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 12, 6)),
                                         Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 15, 6))])
        self.qcinput_gaps2 = QCInput(value=10, timestamp=datetime(2017, 1, 12, 14, 10, 6), longitude=61, latitude=10,
                                     historical_data=[Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                                      Measurement(value=12.0, datetime=datetime(2017, 1, 12, 14, 7, 6)),
                                                      Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 8, 6)),
                                                      Measurement(value=13.0,
                                                                  datetime=datetime(2017, 1, 12, 14, 10, 6))],
                                     future_data=[Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 11, 6)),
                                                  Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 12, 6))])
        self.qcinput_duplicates = QCInput(value=10, timestamp=datetime(2017, 1, 12, 14, 10, 6), longitude=61,
                                          latitude=10,
                                          historical_data=[
                                              Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                              Measurement(value=12.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                              Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 7, 6)),
                                              Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 9, 6))],
                                          future_data=[
                                              Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 11, 6)),
                                              Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 12, 6))])

        self.qcinput_wg_gaps = QCInput(value=10, timestamp=datetime(2017, 1, 12, 14, 10, 6), longitude=61, latitude=10,
                                       historical_data=[
                                           Measurement(value=11.0, datetime=datetime(2017, 1, 12, 13, 36, 6)),
                                           Measurement(value=12.0, datetime=datetime(2017, 1, 12, 14, 6, 6)),
                                           Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 7, 16)),
                                           Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 9, 6))],
                                       future_data=[
                                           Measurement(value=11.0, datetime=datetime(2017, 1, 12, 14, 11, 6)),
                                           Measurement(value=13.0, datetime=datetime(2017, 1, 12, 14, 12, 6))])

        self.qc_fb = qclib.Platforms.FerryboxQC
        self.qc_wg = qclib.Platforms.WaveGliderQC

    def test_should_work_with_arbitrary_sort_order(self):
        qcinput_df = transform_input_to_df(self.qcinput)
        validate_additional_data(self.qc_fb, qcinput_df)
        self.assertEqual(len(qcinput_df.historical_data), 4)
        self.assertEqual(len(qcinput_df.future_data), 2)

    def test_should_detect_time_gaps_for_spike(self):
        qcinput_df = transform_input_to_df(self.qcinput_gaps)
        validate_additional_data(self.qc_fb, qcinput_df)
        self.assertEqual(len(qcinput_df.historical_data), 0)
        self.assertEqual(len(qcinput_df.future_data), 0)

    def test_should_detect_time_gaps(self):
        qcinput_df = transform_input_to_df(self.qcinput_gaps1)
        validate_additional_data(self.qc_fb, qcinput_df)
        self.assertEqual(len(qcinput_df.historical_data), 2)
        self.assertEqual(len(qcinput_df.future_data), 2)

    def test_should_detect_duplicates(self):
        qcinput_df = transform_input_to_df(self.qcinput_duplicates)
        self.assertEqual(has_duplicates(qcinput_df.historical_data), True)

    def test_should_not_discard_historical_data_for_waveglider(self):
        qcinput_df = transform_input_to_df(self.qcinput_wg_gaps)
        validate_additional_data(self.qc_wg, qcinput_df)
        self.assertEqual(len(qcinput_df.historical_data), 4)

    def test_should_remove_data_with_time_gaps(self):
        qcinput_df = transform_input_to_df(self.qcinput_gaps2)
        remove_data_after_time_gap(qcinput_df.historical_data, 0)
        remove_data_after_time_gap(qcinput_df.future_data, 0)


if __name__ == '__main__':
    unittest.main()
