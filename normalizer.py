import csv
import sys
import fileinput
import io
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal


def get_total_seconds(time_str):
    [hour_min_sec, ms] = time_str.split(".")
    [hours, minutes, seconds] = hour_min_sec.split(":")

    # I am rounding here since ms will be two decimal places
    return round(
        3600 * int(hours) + 60 * int(minutes) + int(seconds) + Decimal(0.01) * int(ms),
        2,
    )


def normalize_timestamp(row):
    timestamp = row[0]

    # get the tz naive datetime
    dt_in = datetime.strptime(timestamp, "%m/%d/%y %I:%M:%S %p")
    
    # assign the pacific tz to the date time
    dt_tz = dt_in.replace(tzinfo=ZoneInfo("America/Los_Angeles"))

    # Return the iso formatted Eastern time
    return dt_tz.astimezone(ZoneInfo("America/New_York")).isoformat()


def normalize_address(row):
    address = row[1]
    return address


def normalize_zipcode(row):
    zipcode = row[2]
    if len(zipcode) > 5:
        zipcode = zipcode[:5]
    return zipcode.zfill(5)


def normalize_full_name(row):
    full_name = row[3]
    return full_name.upper()


def normalize_foo_duration(row):
    foo_duration = row[4]
    return get_total_seconds(foo_duration)


def normalize_bar_duration(row):
    bar_duration = row[5]
    return get_total_seconds(bar_duration)


def normalize_total_duration(row):
    foo_duration = row[4]
    bar_duration = row[5]

    return get_total_seconds(foo_duration) + get_total_seconds(bar_duration)


def normalize_notes(row):
    notes = row[7]
    return notes


NORMALIZER_FUNCTIONS = (
    normalize_timestamp,
    normalize_address,
    normalize_zipcode,
    normalize_full_name,
    normalize_foo_duration,
    normalize_bar_duration,
    normalize_total_duration,
    normalize_notes,
)


def main():
    # set the stdin file to a file with bad chars replaced
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="UTF-8", errors="replace")

    # set up the reader and writers
    reader = csv.reader(fileinput.input())
    writer = csv.writer(sys.stdout)

    # Reuse the header from the input file
    header = next(reader)
    writer.writerow(header)

    for row in reader:
        error_encountered = False
        new_row = []

        # Loop through the normalizer functions in order and try to append them to the new row
        for function in NORMALIZER_FUNCTIONS:
            try:
                new_row.append(function(row))

            # If we catch an exception we write it to stderr and set the row to be skipped.
            except Exception as e:
                sys.stderr.write(
                    f"There was an error with normalizing the following row: \n {row} \n {e} \n"
                )
                error_encountered = True

        if not error_encountered:
            writer.writerow(new_row)


main()
