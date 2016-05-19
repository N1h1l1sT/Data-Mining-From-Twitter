#region Imports
import os
import sys
import time
import json
import pymongo
import encodings
from datetime import datetime
from nltk.corpus import stopwords
from getch import getch, pause, pause_exit
from nltk.tag.stanford import StanfordNERTagger

#endregion

#region Initialisation

#Setting (environmental) variables
StanfordNERClassifierPath = "C:\Progs\stanfordNER\classifiers\english.all.3class.distsim.crf.ser.gz"
StanfordNERjarPath = "C:\Progs\stanfordNER\stanford-ner.jar"
st = StanfordNERTagger(StanfordNERClassifierPath, StanfordNERjarPath)

java_path = "C:/Program Files/Java/jdk1.8.0_92/bin"
os.environ['JAVAHOME'] = java_path

#Connect to a MongoDB Database
client = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
collection = db['refcrisis']
proc_coll = db['ProcessedTweets']
#endregion

#region Functions
#Returns a list of words that starts with the input pattern like "#","http" etc.
#[input: list] [output: list]
def getWordsStartingWith(words, startsWith):
    result = list()
    length = len(startsWith)
    for i in range(0, len(words)):
        word = words[i].strip()
        if word[:length] == startsWith:
            result.append(words[i])
    return result

#Removes the stopwords from a text (warning: the input string must be in lowercase)
#[input: string] [output: string]
def removeStopwords(text):
    result = text
    words = text.strip().split(" ")
    stopwordsList = stopwords.words("english")
    result = ' '.join([word for word in words if word not in stopwordsList])
    return result

#Checks whether the input is in English
#[input: string] [output: boolean]
def isEnglish(text):
    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True
#Removes non English words
#[input: string] [output: list]
def removeNonEnglishText(text):
    result = list()
    words = text.strip().split(" ")

    for i in range(0, len(words)):
        if isEnglish(words[i]) == True:
            result.append(words[i])

    return result

#Removes the list items from a text
#[input: string] [output: string]
def removeListItemsFromText(text, lst):
    words = text.strip().split(" ")
    text = ' '.join([word for word in words if word not in lst])
    return text

#Removes the superfluous space characters
#[input: string] [output: string]
def SentenceStringStrip(text):
    words = text.strip().split(" ")
    result = ' '.join(word.strip() for word in words if word.strip())
    return result

#Removes Special Characters from a string
#[input: string] [output: string]
def removeSpecialCharsFromText(text):
    dirtyChars = [',', '.', ';', '?', '/', '\\', '`', '[', ']', '"', ':', '>', '<', '|', '-', '_', '=', '+']
    for i in range(0, len(dirtyChars)):
        text = str.replace(text, dirtyChars[i], " ")
    result = SentenceStringStrip(text)
    return result

#Replaces all the occurrences of a dictionary's name with the corresponding value
#[input: string, dictionary] [output: string]
def replace_all(text, dic):
    for i, j in iter(dic.items()):
        text = text.replace(i, j)
    return text

#Returns a list of named entities
#[input: text] [output: dictionary]
def getTheNamedEntities(text):
    Clean_Text = ' '.join([word for word in text.split() if not word[:1] == '$'])
    lstTag = st.tag(Clean_Text.split())

    result = {}
    for tag in lstTag:
        result [str(str(tag[0])).replace('.','')] = str(tag[1])
    return result
#endregion

#region Main

#region Checking if there already are data in the DB
if proc_coll.count() > 0:
    print("There's already data on the proc_coll collection!!")
    pause_exit(status=0, message='Press any key to exit...')
#endregion

try:
    for RawTweet in collection.find(): #in case we need to continue from a particular place in the collection, add the appropriate skip argument on find()
        #region Acquiring basic info from the Raw Twitter JSON
        tweet_id = RawTweet["id_str"]
        user_id = RawTweet["user"]["id_str"]
        user_screenname = "@" + RawTweet["user"]["screen_name"]
        created_at = RawTweet["created_at"]
        timestamp_ms = RawTweet["timestamp_ms"]
        in_reply_to_status_id_str = RawTweet["in_reply_to_status_id_str"]
        in_reply_to_user_id_str = RawTweet["in_reply_to_user_id_str"]
        in_reply_to_screen_name = RawTweet["in_reply_to_screen_name"]
        friends_count = RawTweet["user"]["friends_count"]
        followers_count = RawTweet["user"]["followers_count"]
        statuses_count = RawTweet["user"]["statuses_count"]
        lang = RawTweet["user"]["lang"]
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

        #region Cleaning & Extrapolation data
        tweet_lowercase = orig_tweet.lower()
        tweet_lowercaseList = tweet_lowercase.split(" ")

        is_retweet = tweet_lowercase[:2] == "rt"

        CleanURLs = getWordsStartingWith(tweet_lowercaseList, "http:")
        CleanURLs += getWordsStartingWith(tweet_lowercaseList, "https:")

        tweet_cleaned = removeListItemsFromText(tweet_lowercase, "rt ")
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
        #tweet_cleaned = normaliseText(tweet_cleaned) ###############################################################################
        tweet_cleaned = removeStopwords(tweet_cleaned)
        tweet_cleaned = tweet_cleaned.strip()
        namedEntities = getTheNamedEntities(tweet_cleaned)
        #tweet_cleaned = StemAll(tweet_cleaned) #####################################################################################
        proc_tweet = tweet_cleaned
        #endregion

        #region Data Processing for saving
        #Getting the Processed Data JSON ready to be inserted into the MongoDB
        proc_data = {
                    "user_screenname": user_screenname,
                    "user_id": user_id,
                    "tweet_id": tweet_id,
                    "created_at": created_at,
                    "timestamp_ms": timestamp_ms,
                    "is_retweet": is_retweet,
                    "in_reply_to_status_id_str": in_reply_to_status_id_str,
                    "in_reply_to_user_id_str": in_reply_to_user_id_str,
                    "in_reply_to_screen_name": in_reply_to_screen_name,
                    "friends_count": friends_count,
                    "followers_count": followers_count,
                    "statuses_count": statuses_count,
                    "urls": urls,
                    "hashtags": hashtags,
                    "user_mantions": user_mentions,
                    "namedEntities": namedEntities,
                    "proc_tweet": proc_tweet
                    }
        #endregion

        #region Saving the Data
        #Inserting them to the MongoDB database
        mongo_proc_data = proc_coll.insert_one(proc_data)    #Saving Collection Processed Tweet
        #endregion


        try:
            print(orig_tweet)
        except Exception as ex:
            print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
            continue

    print("The programme has finished!")

except Exception as e:
    eMessage = 'Main error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n'
    print (str(eMessage))
    saveFile = open('TweetProcessing_Problems.txt', 'a')
    saveFile.write(eMessage)
    saveFile.close()
#endregion

