'''

    This file contains an API that may be used for collaborative story writing.
    Backend   - Python
    Database  - MongoDB
    Framework - Flask
    Library   - PyMongo

'''

import pymongo
from flask import Flask, request,jsonify
from flask_restful import Resource, Api
import requests
from datetime import datetime
