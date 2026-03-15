import argparse
import os

from src.fetch_archive import fetch_from_archive

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("url")

    parser.add_argument("-file_string", default=None)
    parser.add_argument("-output_dir", default=os.getcwd())

    parser.add_argument("-day_of_week", type=int,
                        help="1=Monday, 2=Tuesday ... 7=Sunday")
    parser.add_argument("-day_of_month", type=int,
                        help="1-31, if month has fewer days defaults to last day")

    parser.add_argument("-time_of_day", type=int, default=50)

    parser.add_argument("-start_date", help="In format yyyy-mm-dd")
    parser.add_argument("-end_date", help="In format yyyy-mm-dd")

    parser.add_argument("-verbose", action="store_true")

    parser.add_argument(
    "--force_redownload",
    action="store_true",
    help="Ignore resume logic and redownload all files")

    args = parser.parse_args()

    if (args.day_of_week is None and args.day_of_month is None) or \
       (args.day_of_week is not None and args.day_of_month is not None):
        raise ValueError("Specify exactly one of -day_of_week or -day_of_month")

    if args.day_of_week is not None:
        if not (1 <= args.day_of_week <= 7):
            raise ValueError("day_of_week must be 1-7")

    if args.day_of_month is not None:
        if not (1 <= args.day_of_month <= 31):
            raise ValueError("day_of_month must be 1-31")

    if not (0 <= args.time_of_day <= 100):
        raise ValueError("time_of_day must be 0-100")

    return args

if __name__ == "__main__":
    args = parse_args()
    fetch_from_archive(args)
