"""Seed Firestore with local static hospitals and ambulances data.
Run: python scripts/seed_firestore.py
"""
import json
import os
from app.services.firebase_service import FirebaseService

fs = FirebaseService()

def seed_collection(collection_name, data_path, id_key='id'):
    coll = fs.get_collection(collection_name)
    with open(data_path, 'r', encoding='utf-8') as f:
        items = json.load(f)
    for item in items:
        doc_ref = coll.document(str(item.get(id_key, '')) or None)
        if isinstance(item, dict):
            doc_ref.set(item)
    print(f"Seeded {len(items)} items into {collection_name}")

if __name__ == '__main__':
    base = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'data')
    seed_collection('hospitals', os.path.join(base, 'hospitals.json'))
    seed_collection('ambulances', os.path.join(base, 'ambulances.json'))