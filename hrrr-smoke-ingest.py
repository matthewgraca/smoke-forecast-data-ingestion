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

def data_inventory(hrrr):
    """
    Generates a human-readable summary of the processed HRRR data.

    Args:
        hrrr (HRRRProcessor): Instance containing xarray and dictionary-formatted
            HRRR data.

    Returns:
        str: Formatted summary string showing dataset structure, key data 
        points, and metadata.
    """
    dict_str = reduce(
        lambda acc, k_v: str().join([acc, f"\t{k_v[0]}: {k_v[1]}\n"]),
        hrrr.data_dict['metadata'].items(),
        str()
    )
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

def size_in_MB(data):
    """
    The size of the data that will be written to firebase. Approximated,
    since Firebase is very mysterious on how much you've actually written.

    Args:
        data (HRRRProcessor): Processed HRRR data to write.

    Returns:
        float: The size of the data in megabytes.
    """
    bytes_per_MB = 1000000
    return len(json.dumps(data.data_dict).encode('utf-8')) / bytes_per_MB

def write_to_firebase(db, data, collection_name):
    """
    Writes the HRRR data to a Firestore collection in Firebase.

    Args:
        db (firestore.Client): Firestore database client.
        data (HRRRProcessor): Processed HRRR data to write.
        collection_name (str): Name of the Firestore collection to update.

    Raises:
        SystemExit: If an error occurs during the write process.
    """
    try:
        print("✏️  Attempting to write to firebase database...")
        for doc_name, payload in data.data_dict.items():
            db.collection(collection_name).document(doc_name).set(payload)
        print(f"✅ Success! {size_in_MB(data):.2f}MB written.")
    except Exception as e:
        print("🔴 Error occurred while adding data to firebase:", e)
        sys.exit(1)

def connect_to_firebase():
    """
    Initializes and returns a connection to the Firebase Firestore database.

    Returns:
        firestore.Client: Authenticated Firestore client.

    Raises:
        SystemExit: If the connection attempt fails.
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
    """
    Entry point of the script. Processes HRRR data for a specific region
    and date, optionally prints the data inventory, and writes the data
    to Firebase unless suppressed with a command-line argument.
    """
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
