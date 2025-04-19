import firebase_admin
from firebase_admin import db
from firebase_admin import firestore

default_app = firebase_admin.initialize_app()
print(default_app.name)

db = firestore.client()

collection_name, document_name = "notes", "90"
payload = {
    "content" : "The quick brown fox jumped over the lazy dog",
    "id" : 90,
    "importance" : "MEDIUM",
    "timestamp" : 1732040104190,
    "title" : "This is from my server!"
}

db.collection(collection_name).document(document_name).set(payload)
