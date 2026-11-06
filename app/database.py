try:
    from .config import MONGODB_URL
except ImportError:
    from config import MONGODB_URL
from pymongo import MongoClient

client = MongoClient(MONGODB_URL)
db = client['mydb'] #Get the default database from the connection string

#Collections
contracts_collection = db["contracts"]
analysis_collection = db["analysis"]


def init_db():
    # Create indexes for the collections if they don't exist
    contracts_collection.create_index("contract_id", unique=True)
    analysis_collection.create_index("analysis_id", unique=True)
    print("Database initialized and indexes created.")