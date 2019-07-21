'''

    This file contains an API that may be used for collaborative story writing.
    Backend   - Python
    Database  - MongoDB
    Framework - Flask
    Library   - PyMongo

'''

import pymongo
from flask import Flask, request,jsonify
import requests
from datetime import datetime

# DB connection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
curr = myclient["mydb"]
mycol = curr["stories2"]

# Constraint Constants
S_LENGTH = 2            # Sentence length
P_LENGTH = 2            # Paragraph Length
ST_LENGTH = 2           # Story Length

# Flask app init
app = Flask(__name__)

# Add story
@app.route('/add',methods=['POST'])
def add_word():
    data = request.get_json()
    return data
