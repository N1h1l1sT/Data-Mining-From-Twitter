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

    #FIND DISTINCT LOCATIONS
    locations = get_distinct(tweets)

    #WRITE LOCATIONS IN FILE
    text_file = open("locations.txt", "w")
    for loc,val in sorted(locations.items(),key=lambda kv: kv[1],reverse=True):
        text_file.write("%s => %s \n" % (loc,val))

    text_file.close()

def get_distinct(tweets):
    locations = collections.defaultdict(int)

    try:
        for tweet in tweets.find():
            try:
                location = tweet['user']['location']

                if location:
                    locations[location.encode(sys.stdout.encoding, errors='replace')] += 1
            except Exception as ex:
                print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
                continue

    except Exception as ex:
        print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')

    print(len(locations))
    return locations

main()
