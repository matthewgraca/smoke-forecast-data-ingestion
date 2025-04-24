import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
import xarray as xr
#from herbie import Herbie, wgrib2
#import json
#from datetime import date, datetime, timedelta
from hrrr_processor import HRRRProcessor

HP = HRRRProcessor(
    date="2025-01-16", 
    variable_name='MASSDEN',
    lon_min=-124.40,
    lon_max=-114.13,
    lat_min=32.53,
    lat_max=42.00,
    extent_name='california_region'
)
print(HP.data)
print(HP.firebase_data.keys())

'''
# convert dict -> json 
data_json = json.dumps(data_dict, indent=4)
with open("data.json", "w") as f:
    f.write(data_json)
'''

'''
with open("data.json", "r") as f:
    data = json.load(f)
    print(data.keys())

# connect to firebase database
default_app = firebase_admin.initialize_app()
db = firestore.client()

collection_name, document_name = "conda test", "90"
payload = {
    "content" : "The quick brown fox jumped over the lazy dog",
    "id" : 90,
    "importance" : "MEDIUM",
    "timestamp" : 1732040104190,
    "title" : "This is from my server!"
}

try:
    db.collection(collection_name).document(document_name).set(payload)
except Exception as e:
    print(f"Error occurred: {e}")
'''
