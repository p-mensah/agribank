# utils.py
from bson import ObjectId

def replace_mongo_id(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
    return doc