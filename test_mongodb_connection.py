import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URI")
database_name = os.getenv("MONGODB_DATABASE", "fuzzy_happiness_DB")

if not uri:
    raise RuntimeError("MONGODB_URI is missing from .env")

client = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    client.admin.command("ping")
    print("MongoDB connection successful!")
    print(f"Database: {database_name}")
finally:
    client.close()
