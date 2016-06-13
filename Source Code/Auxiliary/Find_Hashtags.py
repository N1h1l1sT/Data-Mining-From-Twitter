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

    #FIND DISTINCT HASHTAGS
    hashtags = get_distinct(tweets)

    #WRITE HASHTAGS IN FILE
    text_file = open("hashtags.txt", "w")
    for tag,val in sorted(hashtags.items(),key=lambda kv: kv[1],reverse=True):
        text_file.write("%s, %s \n" % (tag,val))

    text_file.close()

def get_distinct(tweets):
    finalhashtags = collections.defaultdict(int)

    try:
        for tweet in tweets.find():
            try:
                hashtaglist = tweet['entities']['hashtags']

                if hashtaglist:
                    #tags = [d['text'] for d in hashtaglist]
                    for tag in [d['text'] for d in hashtaglist]:
                        finalhashtags[tag.encode(sys.stdout.encoding, errors='replace')] += 1
            except Exception as ex:
                print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
                continue

    except Exception as ex:
        print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')

    print(len(finalhashtags))
    return finalhashtags

main()
