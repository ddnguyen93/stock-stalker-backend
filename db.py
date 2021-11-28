# from pymongo import MongoClient
# cluster = MongoClient("mongodb://localhost:27017/")
# db = cluster["shop"]

import mongoengine as db
import dotenv
import os

# db.connect(alias='shop', name='shop')

dotenv.load_dotenv()

uri = os.getenv("DB_URI")

db.connect(host=uri)