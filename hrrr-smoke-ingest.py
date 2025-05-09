import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
import xarray as xr
from hrrr_processor import HRRRProcessor
import argparse
from firebase_manager import FirebaseManager

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

def main():
    """
    Entry point of the script. Processes HRRR data for a specific region
    and date, optionally prints the data inventory, and writes the data
    to Firebase unless suppressed with a command-line argument.
    """
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
