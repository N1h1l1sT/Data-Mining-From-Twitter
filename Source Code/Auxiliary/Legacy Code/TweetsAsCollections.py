#region Imports
import os
import sys
import time
import json
import pymongo
import encodings
from datetime import datetime

def returndocs(collection):
    doc_set = []
    try:
        for RawTweet in collection.find(): #in case we need to continue from a particular place in the collection, add the appropriate skip argument on find()
            try:
                tmpTweet = RawTweet["proc_tweet"]
                doc_set.append(tmpTweet)
                #print(tmpTweet) ##############################
            except Exception as ex:
                print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
                continue

    except Exception as ex:
        print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')

    return doc_set


#Connect to a MongoDB Database
client = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
proc_coll = db['proctweets']
returndocs(proc_coll)