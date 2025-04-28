import os
from pymongo import MongoClient

def connect_to_db():
    """Connect to MongoDB database"""
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongodb_uri)
    return client['job_tracker']