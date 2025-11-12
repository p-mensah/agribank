# db.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# === CONNECT TO ATLAS (YOUR CLUSTER) ===
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("Set MONGO_URI in .env")

# FIXED: MongoClient, NOT MongoClientClient
client = MongoClient(MONGO_URI)
db = client["agribank"]

# === COLLECTIONS ===
users_collection = db["users"]
accounts_collection = db["accounts"]
transactions_collection = db["transactions"]

def get_db():
    """Returns the database client.

    Returns:
        Db: The database client.
    """
    return db