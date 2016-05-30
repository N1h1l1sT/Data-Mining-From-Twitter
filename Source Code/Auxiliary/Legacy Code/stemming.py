#region Imports
import os
import sys
import time
import json
import pymongo
import encodings
from datetime import datetime
from nltk.corpus import stopwords
#from getch import getch, pause, pause_exit
from nltk.tag.stanford import StanfordNERTagger
from nltk import PorterStemmer

#Connect to a MongoDB Database
client = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
#collection = db['refcrisis']
proc_coll = db['proctweets']
stemmedCollection = db['StemmedTweets']
#Initializing the stemmer
stemmer = PorterStemmer()
#endregion

def isEnglish(text):
    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True
#Removes non English words
#[input: string] [output: list]

#region Checking if there already are data in the DB
if proc_coll.count() > 0:
    print("There's already data on the proc_coll collection!!")
    #pause_exit(status=0, message='Press any key to exit...')
#endregion
count = 0


for sTweet in proc_coll.find(): #in case we need to continue from a particular place in the collection, add the appropriate skip argument on find()
	#region Acquiring basic info from the Raw Twitter JSON

	tweetid = sTweet["id"]
	username = sTweet["username"]
	tweettimestamp = sTweet["datetime"]
	orig_tweet = sTweet["orig_tweet"]
	is_retweet = sTweet["is_retweet"]
	lang = sTweet["lang"]
	hashtags = sTweet["hashtags"]
	URLs = sTweet["URLs"]
	mentions = sTweet["Mentions"]
	namedEntities = sTweet["namedEntities"]
	proc_tweet = sTweet["proc_tweet"]

	print(count)
	count += 1

	try:
		#print(proc_tweet)
		textList = proc_tweet.split(' ')
		#print(textList)
	except Exception as e:
			print(e)

	cleanWords = list()


	for word in textList:
		if isEnglish(word):
			cleanWords.append(word)

	singles = [stemmer.stem(stemTweet) for stemTweet in cleanWords]

	stemmedString = ''

	for word in singles:
		stemmedString += word + ' '

	stemmedTweet = stemmedString

	stemmedData = { "id": tweetid,
                    "username": username,
                   "datetime": tweettimestamp,
                    "orig_tweet": orig_tweet,
                    "is_retweet": is_retweet,
                    "lang": lang,
                    "hashtags": hashtags,
                    "URLs": URLs,
                    "Mentions": mentions,
                    "namedEntities": namedEntities,
                    "proc_tweet": proc_tweet,
	      			"stemmed": stemmedTweet,
                    }

	result2 = stemmedCollection.insert_one(stemmedData) #The Processed + Stemmed JSON format

	#w8 = input("Pause")
	#if w8 == "stop":
		#sys.exit("exiting...")

