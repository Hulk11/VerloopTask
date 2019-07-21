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

# create a DB
curr = myclient["mydb"]

# create a collection for stories
mycol = curr["stories10"]

# create collection for stories' overview summary
mysum = curr["summary9"]

# summary parameters limit
story_limit = 10
offset = 0
story_count = 0

# insert story summary document
if(mysum.find({}).count()==0):
    mysum.insert({
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

        # Denotes the end of the story
        # if(p_count>P_LENGTH-1):
        #
        #     curr_sent = last['current_sentence']
        #     # Add a word to te same sentence
        #     if(not(curr_sent)):
        #         curr_sent = data['word']
        #     else:
        #         curr_sent += " " + data['word']
        #
        #     # update the sentence
        #     mycol.find_one_and_update({'_id':curr_id-1},{'$set':{'current_sentence':curr_sent}})

            # # add sentence to trials array
            # mycol.find_one_and_update({'_id':curr_id-1},{'$push':{'trials':curr_sent}})


            # # Add the story summary to summary collection
            # mysum.find_one_and_update({},{'$push':{'results':{'id':curr_id-1,'title':last['title'],'created':last['created'],'updated':last['updated']}}})

        if(curr_id>story_limit):
            return '{"error" : "story limit exceeded"}',400

        # Insert the below document to the collection
        mycol.insert({
                        "_id":curr_id,
                        "title":data['word'],
                        "created":datetime.now().strftime("%H:%M:%S"),
                        "updated":datetime.now().strftime("%H:%M:%S"),
                        "paragraphs": [
                            {
                                "sentences" : [
                                    {

                                    }
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
            curr_sent = mycol.find_one({'_id':curr_id})['current_sentence']
            # If sentence length reached, add another sentence and update fields
            #     # print("-------",curr_sent.split(" "))
            # if(len(curr_sent.split(" "))>S_LENGTH-1):
            #     print("sentence length reached")
            #     mycol.find_one_and_update({'_id':curr_id},{'$push':{'trials':curr_sent}})
            #     mycol.find_one_and_update({'_id':curr_id},{'$inc': {'sentence_count': 1}})
            #     mycol.find_one_and_update({'_id':curr_id},{'$set':{'current_sentence':data['word']}})
            #
            # # Add a word to the same sentence
            # else:
            print("sentence length not reached")
            if(not(curr_sent)):
                curr_sent = data['word']
            else:
                curr_sent += " " + data['word']
            mycol.find_one_and_update({'_id':curr_id},{'$set':{'current_sentence':curr_sent}})
            if(len(curr_sent.split(" "))>S_LENGTH-1):
                mycol.find_one_and_update({'_id':curr_id},{'$inc': {'sentence_count': 1}})

        # Title only has one word, add one more to it
        else:
            title += " " + data['word']
            mycol.find_one_and_update({'_id':curr_id},{'$set':{'title':title}})

    # Increment the paragraph counter
    if(mycol.find_one({'_id':curr_id})['sentence_count']>P_LENGTH-1):
        mycol.find_one_and_update({'_id':curr_id},{'$inc': {'para_count': 1}})

    # Increment the number of words counter
    mycol.find_one_and_update({'_id':curr_id},{'$inc': {'word_count': 1}, '$set': {'updated':datetime.now().strftime("%H:%M:%S") }})
    return jsonify(mycol.find_one({'_id':curr_id},{'_id':1,'title':1,'current_sentence':1})),return_code

# Get stories API
@app.route('/stories',methods=['GET'])
def get_stories():
    return jsonify(mysum.find({})),200

# Get story by ID
@app.route('/stories/<id>',methods=['GET'])
def get_story(id):
    print(type(id))
    return jsonify(mycol.find_one({'_id':int(id)})),200

if __name__ == '__main__':
    app.run(debug=True)
