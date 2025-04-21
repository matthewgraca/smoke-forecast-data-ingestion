import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
from herbie import Herbie, wgrib2
import xarray as xr
import json
from datetime import date, datetime, timedelta

def serialize_date(obj):
    """ Makes date, datetime, and timedelta objects serializable """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, (timedelta)):
        return obj.total_seconds()
    else:
        raise TypeError(f"Type {type(obj)} not serializable.")

def subregion_file(H, extent, extent_name, product):
    """ Uses wgrib2 to subregion the grib file """
    file = H.get_localFilePath(product)
    idx_file = wgrib2.create_inventory_file(file)
    subset_file = wgrib2.region(file, extent, name=extent_name)
    
    return subset_file

# massden = smoke 8m from the surface
# another useful product is COLMD, which is vertically integrated smoke plumes
# Usually 40 MB per frame. however, when serialized, it's ~100 MB, leaving us < 10 frames
# my plan is a 12 hour forecast, so there may need to be some form of trimming.
# we can also subregion the data; if we pick just california, we can definitely expand the forecast hours

# now, with california, the data is 19MB as json, much more managable

# pull today's forecast using Herbie
test_date = "2025-01-16"
H = Herbie(
    test_date,
    model='hrrr',
    product='sfc',
    fxx=0
)

# define california subregion 
lon_min, lon_max = -124.40, -114.13
lat_min, lat_max= 32.53, 42.00
extent = (lon_min, lon_max, lat_min, lat_max)

# subregion herbie using wgrib2
data_grib = subregion_file(
    H=H, extent=extent, extent_name="california_region", product='MASSDEN'
)
print(f"Path of subset file: {data_grib}")

# convert grib -> xarray
data_xr = xr.open_dataset(
    data_grib, engine='cfgrib', decode_timedelta=False, decode_times=False
)
print(data_xr.info)

# if we want to convert kg -> ug, we'd do it here
'''
ug_per_kg = 1000000000
...
'''

# convert xarray -> dict
data_dict = data_xr.to_dict()
print(data_dict.keys())

# remember to flip y, x to x, y. we may only need mdens and lat/lon

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
