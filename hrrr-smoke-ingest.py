import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
import xarray as xr
from hrrr_processor import HRRRProcessor

HP = HRRRProcessor(
    date="2025-01-16", 
    variable_name='MASSDEN',
    lon_min=-119.1,
    lon_max=-117.3,
    lat_min=33.28,
    lat_max=34.86,
    extent_name='la_subregion'
)
print(HP.data)
'''
#print(HP.firebase_data)
# decompose the nested dictionaries
# data vars
data_attrs = HP.data_dict['data_vars']['mdens']['attrs']
data_dims = HP.data_dict['data_vars']['mdens']['dims']
data_data = HP.data_dict['data_vars']['mdens']['data']

# dims
data_dims_x = HP.data_dict['dims']['x']
data_dims_y = HP.data_dict['dims']['y']

# attrs
data_attrs2 = HP.data_dict['attrs']

# coords
data_coords = HP.data_dict['coords']
print(HP.data_dict['coords']['time'].keys())
print(HP.data_dict.keys())
print(data_data[0])
print(data_coords['longitude']['data'][0])
'''

i = 0
j = 0
mdens_data = HP.data_dict['data_vars']['mdens']['data']
lon_data = HP.data_dict['coords']['longitude']['data']
lat_data = HP.data_dict['coords']['latitude']['data']
temp_dict = {}
'''
for mdens, lon, lat in zip(mdens_data[i], lon_data[i], lat_data[i]):
    temp_dict[(lon, lat)] = mdens
'''
for mdens in mdens_data:
    temp_dict[str(i)] = mdens
    i += 1

print(temp_dict.keys())

# connect to firebase database
default_app = firebase_admin.initialize_app()
db = firestore.client()

collection_name = 'hrrr-smoke-data'
document_name = 'mdens-data'
try:
    db.collection(collection_name).document(document_name).set(temp_dict)
except Exception as e:
    print(f"Error occurred: {e}")

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

collection_name, document_name = "conda test", "90"
payload = {
    "content" : "The quick brown fox jumped over the lazy dog",
    "id" : 90,
    "importance" : "MEDIUM",
    "timestamp" : 1732040104190,
    "title" : "This is from my server!"
}
'''
