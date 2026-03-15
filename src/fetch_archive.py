"""
Fetching website snapshots from archive.com
"""
import datetime as dt
import logging
import os
import re
import time
import calendar
import requests
from collections import defaultdict

CDX_URL = "https://web.archive.org/cdx/search/cdx"
ARCHIVE_URL = "https://web.archive.org/web/{timestamp}/{url}"

REQUEST_DELAY = 3  # seconds

session = requests.Session()


def sanitize_filename(value):
    sanitized = re.sub(r"[^\w\-.]", "_", value)
    if sanitized != value:
        logging.warning("file_string required sanitization")
    return sanitized


def parse_date(value):
    if value is None:
        return None
    return dt.datetime.strptime(value, "%Y-%m-%d").date()


def fetch_snapshots(url):
    params = {
        "url": url,
        "output": "json",
        "fl": "timestamp",
        "filter": "statuscode:200"
    }

    r = requests.get(CDX_URL, params=params)
    r.raise_for_status()

    data = r.json()[1:]

    timestamps = []
    for row in data:
        ts = row[0]
        timestamps.append(dt.datetime.strptime(ts, "%Y%m%d%H%M%S"))

    return timestamps


def filter_date_range(timestamps, start_date, end_date):
    result = []

    for ts in timestamps:
        d = ts.date()

        if start_date and d < start_date:
            continue

        if end_date and d > end_date:
            continue

        result.append(ts)

    return result


def select_weekday(ts, target):
    return ts.isoweekday() == target


def adjust_day_of_month(year, month, target):
    last_day = calendar.monthrange(year, month)[1]
    return min(target, last_day)


def group_snapshots(timestamps, args):

    groups = defaultdict(list)

    if args.day_of_week:
        for ts in timestamps:
            if select_weekday(ts, args.day_of_week):
                key = ts.isocalendar()[:2]
                groups[key].append(ts)

    else:
        for ts in timestamps:
            adjusted = adjust_day_of_month(ts.year, ts.month, args.day_of_month)
            if ts.day == adjusted:
                key = (ts.year, ts.month)
                groups[key].append(ts)

    return groups


def seconds_since_midnight(ts):
    return ts.hour * 3600 + ts.minute * 60 + ts.second


def choose_closest(group, time_of_day):

    target = (time_of_day / 100.0) * 86400

    best = None
    best_diff = None

    for ts in group:
        s = seconds_since_midnight(ts)
        diff = abs(s - target)

        if best is None or diff < best_diff:
            best = ts
            best_diff = diff

    return best


def download_snapshot(ts, url, output_dir, file_string, force_redownload=False):

    ts_str = ts.strftime("%Y%m%d%H%M%S")
    formatted = ts.strftime("%Y-%m-%d-%H-%M-%S")

    archive_url = ARCHIVE_URL.format(timestamp=ts_str, url=url)

    filename = f"{formatted}_{file_string}"
    final_path = os.path.join(output_dir, filename)
    tmp_path = final_path + ".tmp"

    if not force_redownload and os.path.exists(final_path):
        logging.info(f"Skipping existing file: {filename}")
        return

    delay = REQUEST_DELAY

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            logging.info(f"Downloading {archive_url}")

            logging.warning("Rate limiting requests")
            time.sleep(delay)

            response = session.get(archive_url, timeout=30)

            if response.status_code >= 500:
                raise requests.exceptions.HTTPError(
                    f"Server error {response.status_code}"
                )

            response.raise_for_status()

            with open(tmp_path, "wb") as f:
                f.write(response.content)

            os.replace(tmp_path, final_path)

            logging.info(f"Saved {filename}")

            return

        except requests.exceptions.RequestException as e:

            if attempt == MAX_RETRIES:

                logging.error(
                    f"Failed after {MAX_RETRIES} attempts: {archive_url}"
                )

                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

                raise

            logging.warning(
                f"Attempt {attempt}/{MAX_RETRIES} failed: {e}"
            )

            delay *= 2


def fetch_from_archive(args):

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    start_date = parse_date(args.start_date)
    end_date = parse_date(args.end_date)

    file_string = args.file_string or args.url
    file_string = sanitize_filename(file_string)

    os.makedirs(args.output_dir, exist_ok=True)

    logging.info("Fetching snapshot list")

    timestamps = fetch_snapshots(args.url)

    timestamps = filter_date_range(timestamps, start_date, end_date)

    groups = group_snapshots(timestamps, args)

    selected = []

    for key, group in sorted(groups.items()):

        chosen = choose_closest(group, args.time_of_day)

        if args.verbose:

            logging.info(f"Group {key}")

            for ts in group:
                if ts == chosen:
                    logging.info(f"Selected {ts}")
                else:
                    logging.info(f"Discarded {ts}")

        selected.append(chosen)

    if not selected:
        logging.warning("No snapshots matched selection criteria")

    for ts in selected:
        download_snapshot(ts, args.url, args.output_dir, file_string, args.force_redownload)
