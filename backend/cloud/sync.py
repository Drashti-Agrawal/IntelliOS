import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# Initialize Firebase app only once
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def push_state(local_file: str = "state.json"):
    """Upload local state.json to Firebase Firestore."""
    if not os.path.exists(local_file):
        print(f"[ERROR] {local_file} not found.")
        return

    with open(local_file, "r") as f:
        state = json.load(f)

    db.collection("intellios").document("state").set(state)
    print("[INFO] State pushed to Firebase successfully.")

def pull_state(remote_file: str = "state.json") -> dict:
    """Download state.json from Firebase Firestore and save locally."""
    doc = db.collection("intellios").document("state").get()
    if not doc.exists:
        print("[ERROR] No state found in Firebase.")
        return {}

    state = doc.to_dict()
    with open(remote_file, "w") as f:
        json.dump(state, f, indent=2)

    print("[INFO] State pulled from Firebase successfully.")
    return state
