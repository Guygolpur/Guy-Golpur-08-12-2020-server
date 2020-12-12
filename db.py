from flask import Flask
from flask_pymongo import pymongo

CONNECTION_STRING = "mongodb+srv://GuyGo:7yWhwSTjmEaXhPKD@cluster0.8xt4f.mongodb.net/email-app?retryWrites=true&w=majority"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('email-app')
user_collection = pymongo.collection.Collection(db, 'users')

