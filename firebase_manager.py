import firebase_admin
from firebase_admin import db
from firebase_admin import firestore
import sys
from functools import reduce
import json
import traceback
from hrrr_processor import HRRRProcessor

class FirebaseManager:
    def __init__(self):
        pass

    def __size_in_MB(self, data):
        """
        The size of the data that will be written to firebase. Approximated,
        since Firebase is very mysterious on how much you've actually written.

        Args:
            data (HRRRProcessor): Processed HRRR data to write.

        Returns:
            float: The size of the data in megabytes.
        """
        bytes_per_MB = 1000000
        return len(json.dumps(data).encode('utf-8')) / bytes_per_MB

    def add_payload_to_firebase(self, db, collection_name, doc_and_payload):
        """
        Writes the collection, document, and payload to the firebase database.
        It's assumed that doc_and_payload is a pair, and element of dict.items()
        """
        doc, payload = doc_and_payload
        db.collection(collection_name).document(doc).set(payload)
        return doc_and_payload

    def write_to_firebase(self, db, data):
        """
        Writes the HRRR data to a Firestore collection in Firebase.

        Args:
            db (firestore.Client): Firestore database client.
            data (HRRRProcessor): Processed HRRR data to write.

        Raises:
            SystemExit: If an error occurs during the write process.
        """
        try:
            print("✏️  Attempting to write to firebase database...")
            # write data description once
            add_payload_to_firebase(
                db=db, 
                collection_name="hrrr-model-description", 
                doc_and_payload=("description", data.data_desc_dict)
            )

            # write every frame
            # list() is needed to force execution of map()
            '''
            list(map(
                lambda item: add_payload_to_firebase(db, item[0], item[1].items()),
                zip(
                    # collection names
                    map(lambda x: f"f{str(x).zfill(2)}", range(0, 24)),
                    # dict items
                    data.data_dict
                )
            ))
            '''

            fxx = list(map(lambda x: f"f{str(x).zfill(2)}", range(0, 24)))
            for i, d in enumerate(data.data_dict):
                for doc_and_payload in d.items():
                    add_payload_to_firebase(db, fxx[i], doc_and_payload)

            print(
                f"✅ Success! "
                f"{reduce(lambda acc, x: acc + size_in_MB(x), data.data_dict, 0):.2f}"
                f"MB written."
            )
        except Exception as e:
            print("🔴 Error occurred while adding data to firebase")
            print(traceback.format_exc())
            sys.exit(1)

    def connect_to_firebase(self):
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
