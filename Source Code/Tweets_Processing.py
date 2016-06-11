#region Imports
import os
import sys
import time
import json
import pymongo
import encodings
from Functions import *
from datetime import datetime
from nltk import PorterStemmer
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordNERTagger
#endregion

#region Initialisation

#Setting (environmental) variables
LogDir = "./Source Code/Logs/"
DistributionDir = "./Source Code/Distribution/"
StanfordNERClassifierPath = "C:\Progs\stanfordNER\classifiers\english.all.3class.distsim.crf.ser.gz"
StanfordNERjarPath = "C:\Progs\stanfordNER\stanford-ner.jar"
NamedEntityRecogn = StanfordNERTagger(StanfordNERClassifierPath, StanfordNERjarPath)
stemmer = PorterStemmer() #Initialising the stemmer
java_path = "C:/Program Files/Java/jdk1.8.0_92/bin"
os.environ['JAVAHOME'] = java_path

#Connect to a MongoDB Database
client = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
refcrisis_coll = db['refcrisis']
ProcessedTweets_coll = db['ProcessedTweets']
DistinctStemmedTweets_coll = db['DistinctStemmedTweets']
#endregion

#region Functions
#Moved to Functions.py
#endregion

#region Main

#region Checks
#Checking if there already are data in the DB
if ProcessedTweets_coll.count() > 0:
    print("There's already data on the ProcessedTweets_coll collection!!")
    input(status=0, message='Press enter to exit...')
#Checking if there already are data in the DistinctStemmedTweets DB
if DistinctStemmedTweets_coll.count() > 0:
    print("There's already data on the DistinctStemmedTweets_coll collection!!")
    input(status=0, message='Press enter to exit...')
#endregion

try:
    TweetsPostTimeDistributionfile = open(DistributionDir + 'TweetsPostTimeDistribution.csv', 'w')
    curIndex = 0

    for RawTweet in refcrisis_coll.find(): #in case we need to continue from a particular place in the collection, add the appropriate skip argument on find()
        #region InfoAcquisition
		#Acquiring basic info from the Raw Twitter JSON
        tweet_id = RawTweet["id_str"]
        user_id = RawTweet["user"]["id_str"]
        user_screenname = "@" + RawTweet["user"]["screen_name"]
        created_at = RawTweet["created_at"]
        timestamp_ms = RawTweet["timestamp_ms"]
        profile_image_url = RawTweet["user"]["profile_image_url"]
        in_reply_to_status_id_str = RawTweet["in_reply_to_status_id_str"]
        in_reply_to_user_id_str = RawTweet["in_reply_to_user_id_str"]
        in_reply_to_screen_name = RawTweet["in_reply_to_screen_name"]
        friends_count = RawTweet["user"]["friends_count"]
        followers_count = RawTweet["user"]["followers_count"]
        statuses_count = RawTweet["user"]["statuses_count"]
        user_language = RawTweet["user"]["lang"]
        tweet_language = RawTweet["lang"]
        User_Location = RawTweet["user"]["location"]
        orig_tweet = RawTweet["text"]

        tempURLs = RawTweet["entities"]["urls"]
        urls = [None] * len(tempURLs)
        for i in range(0, len(tempURLs)):
            urls[i] = tempURLs[i]["expanded_url"].lower()

        temphashtags = RawTweet["entities"]["hashtags"]
        hashtags = [None] * len(temphashtags)
        for i in range(0, len(temphashtags)):
            hashtags[i] = temphashtags[i]["text"].lower()

        tempuser_mentions = RawTweet["entities"]["user_mentions"]
        user_mentions = [None] * len(tempuser_mentions)
        for i in range(0, len(tempuser_mentions)):
            user_mentions[i] = tempuser_mentions[i]["screen_name"].lower()

        for i in range(0, len(hashtags)):
            hashtags[i] = "#" + hashtags[i]

        for i in range(0, len(user_mentions)):
            user_mentions[i] = "@" + user_mentions[i]
        #endregion

        #region PreProcessing
		#Cleaning & Extrapolation data
        tweet_lowercase = orig_tweet.lower()
        tweet_lowercaseList = tweet_lowercase.split(" ")

        is_retweet = tweet_lowercase[:2] == "rt"
        retweeted_from_screenname = getRetweetedFromScreenname(orig_tweet)

        CleanURLs = getWordsStartingWith(tweet_lowercaseList, "http:")
        CleanURLs += getWordsStartingWith(tweet_lowercaseList, "https:")

        tweet_cleaned = " ".join([word for word in removeNonEnglishText(tweet_lowercase)])
        tweet_cleaned = removeListItemsFromText(tweet_cleaned, "rt ")
        tweet_cleaned = removeListItemsFromText(tweet_cleaned, hashtags)
        tweet_cleaned = removeListItemsFromText(tweet_cleaned, CleanURLs)
        tweet_cleaned = removeListItemsFromText(tweet_cleaned, user_mentions)
        other_possible_user_mentions = [None] * len(user_mentions)
        for i in range(0, len(user_mentions)):
            other_possible_user_mentions[i] = user_mentions[i] + ":"
        tweet_cleaned = removeListItemsFromText(tweet_cleaned, other_possible_user_mentions)
        #endregion

        #region NLP
        tweet_cleaned = removeSpecialCharsFromText(tweet_cleaned)
        tweet_cleaned = removeStopwords(tweet_cleaned, stopwords.words("english"))
        tweet_cleaned = tweet_cleaned.strip()
        namedEntities = getTheNamedEntities(tweet_cleaned, NamedEntityRecogn)
        proc_tweet = tweet_cleaned
        #endregion

        #region Stemming
        textList = proc_tweet.split(' ')
        cleanWords = list()
        for word in textList:
            cleanWords.append(word)
        singles = [stemmer.stem(stemTweet) for stemTweet in cleanWords]
        stemmedString = ''

        for word in singles:
            stemmedString += word + ' '

        stemmedTweet = stemmedString
        #endregion

        #region SavingTheData
        #Getting the Processed Data JSON ready to be inserted into the MongoDB
        proc_data = {
                    "tweet_id": tweet_id,
                    "user_id": user_id,
                    "user_screenname": user_screenname,
                    "created_at": created_at,
                    "timestamp_ms": timestamp_ms,
                    "is_retweet": is_retweet,
                    "retweeted_from_screenname": retweeted_from_screenname,
                    "profile_image_url": profile_image_url,
                    "in_reply_to_status_id_str": in_reply_to_status_id_str,
                    "in_reply_to_user_id_str": in_reply_to_user_id_str,
                    "in_reply_to_screen_name": in_reply_to_screen_name,
                    "friends_count": friends_count,
                    "followers_count": followers_count,
                    "statuses_count": statuses_count,
                    "user_language": user_language,
                    "tweet_language": tweet_language,
                    "User_Location": User_Location,
                    "orig_tweet": orig_tweet,
                    "urls": urls,
                    "hashtags": hashtags,
                    "user_mantions": user_mentions,
                    "namedEntities": namedEntities,
                    "proc_tweet": proc_tweet,
                    "stemmed_tweet": stemmedTweet,
                    }

        #Inserting them to the MongoDB database
        mongo_proc_data = ProcessedTweets_coll.insert_one(proc_data)    #Saving Collection Processed Tweet

        #SavingTheData continues below
        #endregion

        TweetPostTime = datetime.strptime(created_at,'%a %b %d %X %z %Y').strftime('%d/%m/%y %X')
        TweetsPostTimeDistributionfile.write(tweet_id + "," + TweetPostTime + "\n")

        try:
            curIndex += 1
            print(curIndex)
        except Exception as ex:
            print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
            continue

    #SavingTheData Continues
    #region SavingTheData
    #Creating the DistinctStemmedTweets_coll
    print('Creating the DistinctStemmedTweets_coll collection\n')
    doc_set1 = []

    for RawTweet in ProcessedTweets.distinct("stemmed_tweet"):
        try:
            doc_set1.append(RawTweet)
        except Exception as ex:
            print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
            continue

    for i in range(0, len(doc_set1)):
        stemmed = doc_set1[i]

        for RawTweet in StemmedTweets.find({"stemmed_tweet": stemmed_tweet}).limit(1):
                DistinctStemmedTweets_coll.insert_one(RawTweet)
    #endregion

    print("The programme has finished!")

except Exception as e:
    eMessage = 'Main error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n'
    print (str(eMessage))
    saveFile = open(LogDir + 'TweetProcessing_Problems.txt', 'a')
    saveFile.write(eMessage)
    saveFile.close()
#endregion

