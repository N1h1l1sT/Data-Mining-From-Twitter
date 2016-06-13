import sys
import pymongo
import numpy as np
from datetime import datetime
import pdb
import collections

def main():
    #CONNECT TO DATABASE & COLLECTION
    client = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
    db = client['mongorefcon']
    tweets = db['refcrisis']

    #FIND DISTINCT USERS
    usernames = get_distinct(tweets)

    #WRITE USERS IN FILE
    text_file = open("usernames.txt", "w")
    for usr,val in sorted(usernames.items(),key=lambda kv: kv[1],reverse=True):
        text_file.write("%s => %s \n" % (usr,val))

    text_file.close()

def get_distinct(tweets):
    usernames = collections.defaultdict(int)

    try:
        for tweet in tweets.find():
            try:
                username = tweet['user']['screen_name']

                if username:
                    usernames[username.encode(sys.stdout.encoding, errors='replace')] += 1
            except Exception as ex:
                print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
                continue

    except Exception as ex:
        print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')

    print(len(usernames))
    return usernames

main()
