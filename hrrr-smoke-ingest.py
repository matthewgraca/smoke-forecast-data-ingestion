import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
import xarray as xr
from hrrr_processor import HRRRProcessor
import argparse
import sys

def init_argparser():
    """ Defines command line argument parser """
    parser = argparse.ArgumentParser()
    # print argument
    parser.add_argument(
        "-p", 
        "--print", 
        help="prints inventory of ingested data to standard output", 
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

def data_inventory(HP):
    """ Creates a string of the inventory of the data processed """
    # generate string of dictionary items
    dict_str = '\n'.join(
        map(
            lambda key_val: f"\t{key_val[0]}: {key_val[1]}", 
            HP.data_dict['metadata'].items()
        )
    )
    # examine full inventory and some values
    return (
        f"🗃️  Dataset inventory: {HP.data_xr}\n\n"
        f"🔑 Dictionary keys: {HP.data_dict.keys()}\n"
        f"🚬 First mdens value: {HP.data_dict['mdens'][str(0)][0]}\n"
        f"📍 First longitude value: {HP.data_dict['longitude'][str(0)][0]}\n"
        f"📍 First latitude value: {HP.data_dict['latitude'][str(0)][0]}\n"
        f"🕰️  Time: {HP.data_dict['time']['data']}\n"
        f"📜 Metadata:\n"
        f"{dict_str}\n"
    )

def write_to_firebase(db, data, collection_name):
    """ Attempts to write the data into the firebase database """
    try:
        print("✏️  Attempting to write to firebase database...")
        for doc_name, payload in data.data_dict.items():
            db.collection(collection_name).document(doc_name).set(payload)
        print("✅ Success!")
    except Exception as e:
        print("🔴 Error occurred while adding data to firebase:", e)
        sys.exit(1)

def connect_to_firebase():
    """ Attempts to connect to the firebase database. 
        Returns the database client """
    try:
        print("🔎 Connecting to firebase database...")
        default_app = firebase_admin.initialize_app()
        db = firestore.client()
        print("✅ Success!")
    except Exception as e:
        print("🔴 Error occurred while connecting to firebase:", e)
        sys.exit(1)

    return db

def main():
    parser = init_argparser()
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
        print(data_inventory(HP))

    if args.no_write:
        print("⏭️  Skipping the write to database.")
    else:
        db = connect_to_firebase()
        collection_name = 'hrrr-smoke-data'
        write_to_firebase(db, HP, collection_name)

if __name__ == "__main__":
    main()
