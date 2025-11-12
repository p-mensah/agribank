# utils.py
from bson import ObjectId

def replace_mongo_id(doc):
    """Replaces the '_id' field in a document with 'id' and converts it to a string.

    Args:
        doc (dict): The document to process.

    Returns:
        dict: The processed document.
    """
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
    return doc