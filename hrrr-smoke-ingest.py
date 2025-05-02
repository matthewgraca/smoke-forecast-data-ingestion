import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
import xarray as xr
from hrrr_processor import HRRRProcessor
import argparse

def argparser():
    """ Defines command line argument parser """
    parser = argparse.ArgumentParser()
    # print argument
    parser.add_argument(
        "-p", 
        "--print", 
        help="prints xarray data inventory to stdout", 
        action="store_true"
    )
    # no write to database argument
    parser.add_argument(
        "-nw", 
        "--no-write", 
        help="prevents program from writing data into firebase database", 
        action="store_true"
    )

    return parser

def print_inventory(HP):
    """ Prints inventory of the data processed """
    # examine full inventory
    print(HP.data_xr, "\n")

    # check out some values
    print(f"🔑 Dictionary keys : {HP.data_dict.keys()}")
    print(f"🚬 First mdens value : {HP.data_dict['mdens'][str(0)][0]}")
    print(f"📍 First longitude value : {HP.data_dict['longitude'][str(0)][0]}")
    print(f"📍 First latitude value : {HP.data_dict['latitude'][str(0)][0]}")
    print(f"🕰️  Time : {HP.data_dict['time']['data']}")
    print(f"📜 Metadata :")
    for k, v in HP.data_dict['metadata'].items():
        print(f"\t{k} : {v}")

def write_to_firebase(HP):
    collection_name = 'hrrr-smoke-data'

    # attempt connect to firebase database
    try:
        print("🔎 Connecting to firebase database...")
        default_app = firebase_admin.initialize_app()
        db = firestore.client()
        print("✅ Success!")
    except Exception as e:
        print("🔴 Error occurred while connecting to firebase:", e)
        sys.exit(1)

    # attempt write to firebase
    try:
        print("✏️  Attempting to write to firebase database...")
        for doc_name, payload in HP.data_dict.items():
            db.collection(collection_name).document(doc_name).set(payload)
        print("✅ Success!")
    except Exception as e:
        print("🔴 Error occurred while adding data to firebase:", e)
        sys.exit(1)

def main():
    parser = argparser()
    args = parser.parse_args()

    HP = HRRRProcessor(
        date="2025-01-16", 
        variable_name='MASSDEN',
        lon_min=-119.1,
        lon_max=-117.3,
        lat_min=33.28,
        lat_max=34.86,
        extent_name='la_subregion'
    )

    if args.print:
        print_inventory(HP)

    if args.no_write:
        print("⏭️  Skipping the write to database.")
    else:
        write_to_firebase(HP)

if __name__ == "__main__":
    main()
