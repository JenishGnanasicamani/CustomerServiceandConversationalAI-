import pymongo
from bson import SON

print("pymongo version:", pymongo.__version__)
print("SON import successful")

client = pymongo.MongoClient("mongodb://localhost:27017/")
try:
    client.admin.command('ismaster')
    print("MongoDB connection successful")
except Exception as e:
    print("MongoDB connection failed:", str(e))
