from hrrr_processor import HRRRProcessor
from herbie import Herbie
from firebase_manager import FirebaseManager
import argparse
import datetime as dt
from datetime import datetime, timedelta
import time

def init_argparser():
    """ 
    Initializes and returns the command-line argument parser.

    Returns:
        argparse.ArgumentParser: Parser configured with arguments for 
        printing data and skipping Firebase writes.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", 
        "--print", 
        help="prints inventory of ingested data to standard output", 
        action="store_true"
    )
    parser.add_argument(
        "-nw", 
        "--no-write", 
        help="prevents program from writing data into firebase database", 
        action="store_true"
    )
    return parser

def wait_until(time_to_ingest, freq):
    """
    Waits until the given date arrives, checking at the given frequency.
    Separate from wait for grib so we ping AWS as little as possible.
    """
    while datetime.now(dt.UTC) < time_to_ingest:
        time.sleep(freq)

def wait_for_grib(time_to_ingest, freq):
    """
    Ping for data. look for 23th hour forecast; if it exists, [0, 22] will exist 
    """
    H = Herbie(date=tomorrow_dt, model='hrrr', fxx=23)
    while H.grib is None:
        time.sleep(freq)
        H = Herbie(date=tomorrow_dt, model='hrrr', fxx=23)

def main():
    parser = init_argparser()
    args = parser.parse_args()

    hrrr = HRRRProcessor(
        date="2025-01-10", 
        variable_name='MASSDEN',
        lon_min=-119.1,
        lon_max=-117.3,
        lat_min=33.28,
        lat_max=34.86,
        extent_name='la_subregion'
    )

    """ 
    unfortunately, python has no tail call optimization;
    so this can't be converted to a recursive function at all, so this portion
    of the code can't be converted functionally. 
    """
    """
    today_dt = datetime.now(dt.UTC)
    while True:
        tomorrow_dt = today_dt.replace(second=0, hour=0, minute=0) + timedelta(days=1)

        # check if tomorrow + 1 hour has arrrived; usually takes an hour to upload
        wait_until(time_to_ingest=tomorrow_dt + timedelta(hours=1), freq=5 * 60)
        wait_for_grib(time_to_ingest=tomorrow_dt, freq=5 * 60)

        # data should exist at this point -- send it
        hrrr = HRRRProcessor(
            date=tomorrow_dt,
            variable_name='MASSDEN',
            lon_min=-119.1,
            lon_max=-117.3,
            lat_min=33.28,
            lat_max=34.86,
            extent_name='la_subregion'
        ) 
        
        if args.print:
            print(hrrr.full_data_inventory())

        if args.no_write:
            print("⏭️  Skipping the write to database.")
        else:
            fbm = FirebaseManager()
            db = fbm.connect_to_firebase()
            fbm.write_to_firebase(db, hrrr)

        # repeat
        today_dt = tomorrow_dt
    """
    
    if args.print:
        print(hrrr.full_data_inventory())

    if args.no_write:
        print("⏭️  Skipping the write to database.")
    else:
        fbm = FirebaseManager()
        db = fbm.connect_to_firebase()
        fbm.write_to_firebase(db, hrrr)

if __name__ == "__main__":
    main()
