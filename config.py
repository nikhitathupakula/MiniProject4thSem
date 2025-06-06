from dotenv import load_dotenv
import os
from pymongo import MongoClient
load_dotenv()
client = MongoClient(mongo_uri)
db = client["test"]