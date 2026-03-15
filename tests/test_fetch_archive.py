import unittest
import datetime as dt
from unittest.mock import patch, MagicMock

from src import fetch_archive


class TestWaybackFunctions(unittest.TestCase):

    def test_adjust_day_of_month(self):

        # Case 1: day_of_month value is "1"
        result = fetch_archive.adjust_day_of_month(2024, 5, 1)
        self.assertEqual(result, 1)

        # Case 2: day_of_month value is "31" for April
        result = fetch_archive.adjust_day_of_month(2024, 4, 31)
        self.assertEqual(result, 30)

        # Case 3: day_of_month value is "31" for February (leap year)
        result = fetch_archive.adjust_day_of_month(2024, 2, 31)
        self.assertEqual(result, 29)


    def test_seconds_since_midnight(self):

        # Case 1: midnight
        ts = dt.datetime(2024, 1, 1, 0, 0, 0)
        self.assertEqual(fetch_archive.seconds_since_midnight(ts), 0)

        # Case 2: midday
        ts = dt.datetime(2024, 1, 1, 12, 0, 0)
        self.assertEqual(fetch_archive.seconds_since_midnight(ts), 43200)

        # Case 3: end of day
        ts = dt.datetime(2024, 1, 1, 23, 59, 59)
        self.assertEqual(fetch_archive.seconds_since_midnight(ts), 86399)


    def test_choose_closest(self):

        group = [
            dt.datetime(2024, 1, 1, 3, 0, 0),
            dt.datetime(2024, 1, 1, 12, 0, 0),
            dt.datetime(2024, 1, 1, 18, 0, 0),
        ]

        # Case 1: time_of_day = 0 (closest to midnight)
        result = fetch_archive.choose_closest(group, 0)
        self.assertEqual(result, group[0])

        # Case 2: time_of_day = 51 (after midday)
        result = fetch_archive.choose_closest(group, 51)
        self.assertEqual(result, group[1])

        # Case 3: time_of_day = 69
        result = fetch_archive.choose_closest(group, 69)
        self.assertEqual(result, group[2])


    def test_filter_date_range(self):

        timestamps = [
            dt.datetime(2023, 12, 31),
            dt.datetime(2024, 1, 1),
            dt.datetime(2024, 6, 1),
            dt.datetime(2025, 1, 1)
        ]

        # Case 1: start_date filter
        result = fetch_archive.filter_date_range(
            timestamps,
            dt.date(2024, 1, 1),
            None
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result, [dt.datetime(2024, 1, 1),
                                  dt.datetime(2024, 6, 1),
                                  dt.datetime(2025, 1, 1)])

        # Case 2: end_date filter
        result = fetch_archive.filter_date_range(
            timestamps,
            None,
            dt.date(2024, 12, 31)
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result, [dt.datetime(2023, 12, 31),
                                  dt.datetime(2024, 1, 1),
                                  dt.datetime(2024, 6, 1)])

        # Case 3: both start_date and end_date
        result = fetch_archive.filter_date_range(
            timestamps,
            dt.date(2024, 1, 1),
            dt.date(2024, 12, 31)
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result, [dt.datetime(2024, 1, 1),
                                  dt.datetime(2024, 6, 1)])


    def test_group_snapshots_weekday(self):

        args = MagicMock()
        args.day_of_week = 3
        args.day_of_month = None

        timestamps = [
            dt.datetime(2024, 1, 3, 12),   # Wednesday
            dt.datetime(2024, 1, 10, 13),  # Wednesday
            dt.datetime(2024, 1, 4, 12)    # Thursday
        ]

        groups = fetch_archive.group_snapshots(timestamps, args)

        # Case 1: only Wednesdays should appear
        self.assertEqual(len(groups), 2)

        # Case 2: ensure timestamps inside groups are Wednesdays
        for group in groups.values():
            for ts in group:
                self.assertEqual(ts.isoweekday(), 3)


    def test_sanitize_filename(self):

        # Case 1: already safe string
        result = fetch_archive.sanitize_filename("sample.html")
        self.assertEqual(result, "sample.html")

        # Case 2: URL string requiring sanitization
        result = fetch_archive.sanitize_filename("https://example.com/page")
        self.assertNotIn(":", result)
        self.assertNotIn("/", result)



class TestMain(unittest.TestCase):

    @patch("src.fetch_archive.download_snapshot")
    @patch("src.fetch_archive.group_snapshots")
    @patch("src.fetch_archive.filter_date_range")
    @patch("src.fetch_archive.fetch_snapshots")
    def test_main_execution(
        self,
        mock_fetch,
        mock_filter,
        mock_group,
        mock_download
    ):

        args = MagicMock()
        args.url = "https://example.com"
        args.file_string = "sample.html"
        args.output_dir = "."
        args.day_of_week = 3
        args.day_of_month = None
        args.time_of_day = 50
        args.start_date = None
        args.end_date = None
        args.verbose = False

        ts1 = dt.datetime(2024, 1, 3, 12)
        ts2 = dt.datetime(2024, 1, 10, 13)

        mock_fetch.return_value = [ts1, ts2]
        mock_filter.return_value = [ts1, ts2]

        mock_group.return_value = {
            (2024, 1): [ts1],
            (2024, 2): [ts2]
        }

        fetch_archive.fetch_from_archive(args)

        # Case 1: fetch_snapshots called
        mock_fetch.assert_called_once()

        # Case 2: download_snapshot called for each group
        self.assertEqual(mock_download.call_count, 2)

        # Case 3: group_snapshots used
        mock_group.assert_called_once()