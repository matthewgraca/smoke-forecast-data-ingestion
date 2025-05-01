import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
import xarray as xr
from hrrr_processor import HRRRProcessor
import sys

HP = HRRRProcessor(
    date="2025-01-16", 
    variable_name='MASSDEN',
    lon_min=-119.1,
    lon_max=-117.3,
    lat_min=33.28,
    lat_max=34.86,
    extent_name='la_subregion'
)

# examine full inventory
print(HP.data_xr)

# examine data trimmed and converted to dictionary
print(f"\nDictionary keys: {HP.data_dict.keys()}\n")

# check out a value
print(f"mdens value: {HP.data_dict['mdens'][str(0)][0]}")
print(f"longitude value: {HP.data_dict['longitude'][str(0)][0]}")
print(f"latitude value: {HP.data_dict['latitude'][str(0)][0]}")
print(f"time: {HP.data_dict['time']['data']}")
print(f"metadata: {HP.data_dict['metadata']}\n")

# connect to firebase database
collection_name = 'hrrr-smoke-data'
try:
    print("🔎 Connecting to firebase database...")
    default_app = firebase_admin.initialize_app()
    db = firestore.client()
    print("✅ Success!\n")
except Exception as e:
    print(f"🔴 Error occurred while connecting to firebase: {e}")

try:
    print("✏️  Attempting to add data to firebase database...")
    for doc_name, payload in HP.data_dict.items():
        db.collection(collection_name).document(doc_name).set(payload)
    print("✅ Success!\n")
except Exception as e:
    print(f"🔴 Error occurred while adding data to firebase: {e}")
