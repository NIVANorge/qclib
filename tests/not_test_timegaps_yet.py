# import unittest
# from datetime import datetime
#
# import pandas as pd
#
# from qclib.utils.transform_input import validate_data_for_time_gaps
#
#
# def _date(datestring):
#     return datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S")
#
#
# class TimegapsTest(unittest.TestCase):
#
#     def setUp(self):
#         self.dates = [
#             _date('2019-02-11 00:01:01'),
#             _date('2019-02-10 23:46:58'),
#             _date('2019-02-10 23:47:58'),
#             _date('2019-02-10 23:48:59'),
#             _date('2019-02-10 23:49:59'),
#             _date('2019-02-10 23:50:59'),
#             _date('2019-02-10 23:51:59'),
#             _date('2019-02-10 23:52:59'),
#             _date('2019-02-10 23:53:59'),
#             _date('2019-02-10 23:55:00'),
#             _date('2019-02-10 23:56:00'),
#             _date('2019-02-10 23:57:00'),
#             _date('2019-02-10 23:58:00'),
#             _date('2019-02-10 23:59:00'),
#             _date('2019-02-11 00:00:00')
#         ]
#
#     def test_should_detect_time_gaps(self):
#         df = pd.DataFrame({'time': self.dates})
#         sorted = df.sort_values(by="time", ascending=True)
#         self.assertEqual(validate_data_for_time_gaps(sorted), False)
#         self.assertEqual(validate_data_for_time_gaps(sorted, fuzzy_seconds=1), True)
#
#     def test_should_work_with_arbitrary_sort_order(self):
#         df = pd.DataFrame({'time': self.dates})
#         sorted = df.sort_values(by="time", ascending=False)
#         self.assertEqual(validate_data_for_time_gaps(sorted), False)
#         self.assertEqual(validate_data_for_time_gaps(sorted, 1), True)
