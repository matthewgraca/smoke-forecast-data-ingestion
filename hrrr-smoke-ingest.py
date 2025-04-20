import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
from herbie import Herbie
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

# pull today's forecast using Herbie
test_date = "2025-01-16"
H = Herbie(
    test_date,
    model='hrrr',
    product='sfc',
    fxx=0
)

# massden = smoke 8m from the surface
# another useful product is COLMD, which is vertically integrated smoke plumes
# Usually 40 MB per frame. however, when serialized, it's ~100 MB, leaving us < 10 frames
# my plan is a 12 hour forecast, so there may need to be some form of trimming.
# we can also subregion the data; if we pick just california, we can definitely expand the forecast hours
ds = H.xarray('MASSDEN')

# convert to json
ds_dict = ds.to_dict()
ds_json = json.dumps(ds_dict, indent=4, default=serialize_date)
with open("data.json", "w") as f:
    f.write(ds_json)
with open("data.json", "r") as f:
    data = json.load(f)
    print(data.keys())

'''
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

db.collection(collection_name).document(document_name).set(payload)
'''
