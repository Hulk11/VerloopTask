'''
    This file contains an API that may be used for collaborative story writing.
    Backend   - Python
    Database  - MongoDB
    Framework - Flask
    Library   - PyMongo

    Maintaining 2 collections, one for story details and other for summary
'''

import pymongo
from flask import Flask, request,jsonify
import requests
from datetime import datetime

# DB connection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

# create a DB
curr = myclient["mydb"]

# create a collection for stories
mycol = curr["stories12"]

# create collection for stories' overview summary
mysum = curr["summary12"]

# summary parameters limit
story_limit = 10
offset = 0
story_count = 0

# insert story summary document
if(mysum.find({}).count()==0):
    mysum.insert({
                    '_id': 0,
                    'limit':story_limit,
                    'offset':offset,
                    'count':story_count,
                    'results':[

                    ]
                })


# Constraint Constants
S_LENGTH = 3            # Sentence length
P_LENGTH = 1            # Paragraph Length
ST_LENGTH = 1           # Story Length

# Flask app init
app = Flask(__name__)

# Add story
@app.route('/add',methods=['POST'])
def add_word():
    data = request.get_json()

    # If more than one word given as input , throw error 400
    if(len(data['word'].split(" "))>1):
        return jsonify('{ "error" : "multiple words sent" }'),400

    # get the latest added Story
    last = mycol.find_one(sort=[('_id',pymongo.DESCENDING)])

    # helper variables
    curr_id = 0                 # to get the current story ID
    p_count = 0                 # to get the paragraph count
    init_counts = 0             # initialize count data in document , otherwise insert query adds string instead of int
    return_code = 200           # return codes set before returning

    # If a collection already exists, then set the above parameters accordingly
    if(last):
        curr_id = last['_id']
        p_count = int(last['para_count'])

    # If the collection is empty OR story has ended, add another document
    if(mycol.find({}).count()==0 or p_count>ST_LENGTH-1):
        curr_id += 1            # increment the story ID
        return_code = 201

        # Put a check on number of stories, should be under a limit
        if(curr_id>story_limit):
            return '{"error" : "story limit exceeded"}',400

        # Insert the below document to the collection
        mycol.insert({
                        "_id":curr_id,
                        "title":data['word'],
                        "created":datetime.utcnow().isoformat(),
                        "updated":datetime.utcnow().isoformat(),
                        "paragraphs": [
                            {
                                "sentences" : [

                                ]
                            }
                        ],
                        "trials":[],            # trial field for storing all sentences
                        "current_sentence":'',
                        "count":init_counts,
                        "para_count":init_counts,
                        "sentence_count":init_counts,
                        "word_count":init_counts
        })

        # Add the story summary to summary collection
        mysum.find_one_and_update({},{'$push':{
                                                'results':{
                                                            'id':curr_id,
                                                            'title':data['word'],
                                                            'created':datetime.utcnow().isoformat(),
                                                            'updated':datetime.utcnow().isoformat()
                                                           }
                                                }
                                     })



    # If the collection already has a valid document where an addition can be made,
    # add the word in the sentence, and accordingly update the fields
    else:
        title = last['title']           # title of the current story

        # If title already has 2 words, add the new word in a sentence
        if(len(title.split(" "))>1):

            # Keep track of the current sentence
            curr_sent = mycol.find_one({'_id':curr_id})['current_sentence']

            # Keep track of current number of paragraphs
            curr_para = mycol.find_one({'_id':curr_id})['para_count']


            # Updating the current sentence
            # If it's empty, then fill
            if(not(curr_sent)):
                curr_sent = data['word']

            # oterwise add
            else:
                curr_sent += " " + data['word']
            mycol.find_one_and_update({'_id':curr_id},{'$set':{'current_sentence':curr_sent}})

            # If a sentence has exhausted it's word limit, then increase the sentence count by 1,
            # and add it to the current paragraph. The current has been kept in track by using,
            # curr_para variable defined above
            if(len(curr_sent.split(" "))>S_LENGTH-1):
                mycol.find_one_and_update({'_id':curr_id},{'$inc': {'sentence_count': 1}})
                mycol.find_one_and_update({'_id':curr_id},{'$push': {'paragraphs.'+str(curr_para)+'.sentences': curr_sent}})

        # Title only has one word, add one more to it
        else:
            title += " " + data['word']
            # Update the title in details collection
            mycol.find_one_and_update({'_id':curr_id},{'$set':{'title':title}})

            # Update the title in summary collection
            mysum.find_one_and_update({'limit':story_limit},{'$set':{'results.'+str(curr_id-1)+'.title':title}})

    # Increment the paragraph counter
    if(mycol.find_one({'_id':curr_id})['sentence_count']>P_LENGTH-1):
        mycol.find_one_and_update({'_id':curr_id},{'$inc': {'para_count': 1}})

    # Increment the number of words counter
    mycol.find_one_and_update({'_id':curr_id},{'$inc': {'word_count': 1}, '$set': {'updated':datetime.utcnow().isoformat() }})

    # updating the summary collection
    mysum.find_one_and_update({'limit':story_limit},{'$set':{'results.'+str(curr_id-1)+'.updated':datetime.utcnow().isoformat()}})


    return jsonify(mycol.find_one({'_id':curr_id},{'_id':1,'title':1,'current_sentence':1})),return_code

# Get stories API
# Here, we just return the whole summary collection
@app.route('/stories',methods=['GET'])
def get_stories():
    return jsonify(mysum.find_one({'limit':story_limit})),200

# Get story by ID
# Return story by story id
@app.route('/stories/<id>',methods=['GET'])
def get_story(id):
    print(type(id))
    return jsonify(mycol.find_one({'_id':int(id)},{'_id':1,'title':1,'created':1,'updated':1,'paragraphs':1})),200

# Remove both collections
@app.route('/clear',methods=['POST'])
def clear_doc():
    mycol.delete_many({})
    mysum.delete_many({})
    return '{"message":"the docs been cleared"}'


if __name__ == '__main__':
    app.run(debug=False) # False, since it was meant to be kept in mind that it this in production.
