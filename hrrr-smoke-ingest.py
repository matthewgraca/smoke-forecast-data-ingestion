import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
import xarray as xr
from hrrr_processor import HRRRProcessor
import argparse
import sys
from functools import reduce

def init_argparser():
    """ 
    Defines command line argument parser 

    Returns:
        ArgumentParser: The initialized argument parser.
    """
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

def data_inventory(hrrr):
    """ Creates a string of the inventory of the data processed 

    Args:
        hrrr (HRRRProcessor): The class containing the processed data.

    Returns:
        str: A string of the data's inventory an a subset of its values.
    """
    # convert dictionary -> string 
    dict_str = reduce(
        lambda acc, k_v: str().join([acc, f"\t{k_v[0]}: {k_v[1]}\n"]),
        hrrr.data_dict['metadata'].items(),
        str()
    )
    # examine full inventory and some values
    return (
        f"🗃️  Dataset inventory: {hrrr.data_xr}\n\n"
        f"🔑 Dictionary keys: {hrrr.data_dict.keys()}\n"
        f"🚬 First mdens value: {hrrr.data_dict['mdens'][str(0)][0]}\n"
        f"📍 First longitude value: {hrrr.data_dict['longitude'][str(0)][0]}\n"
        f"📍 First latitude value: {hrrr.data_dict['latitude'][str(0)][0]}\n"
        f"🕰️  Time: {hrrr.data_dict['time']['data']}\n"
        f"📜 Metadata:\n"
        f"{dict_str}"
    )

def write_to_firebase(db, data, collection_name):
    """ 
    Attempts to write the data into the firebase database.

    Args:
        db (Client): The firestore client object.
        hrrr (HRRRProcessor): The data being written into the database.
        collection_name (str): The name of the collection being updated.
    """
    try:
        print("✏️  Attempting to write to firebase database...")
        for doc_name, payload in hrrr.data_dict.items():
            db.collection(collection_name).document(doc_name).set(payload)
        print("✅ Success!")
    except Exception as e:
        print("🔴 Error occurred while adding data to firebase:", e)
        sys.exit(1)

def connect_to_firebase():
    """ 
    Attempts to connect to the firebase database. 

    Returns:
        db (Client): The firebase database client.
    """
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

    hrrr = HRRRProcessor(
        date="2025-01-16", 
        variable_name='MASSDEN',
        lon_min=-119.1,
        lon_max=-117.3,
        lat_min=33.28,
        lat_max=34.86,
        extent_name='la_subregion'
    )

    if args.print:
        print(data_inventory(hrrr))

    if args.no_write:
        print("⏭️  Skipping the write to database.")
    else:
        db = connect_to_firebase()
        collection_name = 'hrrr-smoke-data'
        write_to_firebase(db, hrrr, collection_name)

if __name__ == "__main__":
    main()
