#import MySQLdb                 #For MySQL Database
import time
import json
import bson
import re
import os
import sys
import nltk
import datetime
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from pymongo import MongoClient #For MongoDB Database
from datetime import datetime
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordNERTagger
from urllib.request import urlopen
import encodings

##########################
###   Initialisation   ###
##########################

StanfordNERClassifierPath = "C:\Progs\stanfordNER\classifiers\english.all.3class.distsim.crf.ser.gz"
StanfordNERjarPath = "C:\Progs\stanfordNER\stanford-ner.jar"

java_path = "C:/Program Files/Java/jdk1.8.0_92/bin"
os.environ['JAVAHOME'] = java_path

## Connect to a MySQL Database
##        replace "mysql.server" with "localhost" if you are running via your own server!
##                        server       MySQL username	MySQL pass  Database name.
#conn = MySQLdb.connect("localhost","root","","refcrisis")
#c = conn.cursor()

#Connect to a MongoDB Database
#Example: MongoClient("mongodb://mongodb0.example.net:27019")
client = MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
collection = db['refcrisis']
proc_coll = db['proctweets']

#We need the consumer key, consumer secret, access token, access secret.
ckey = "jrzcRp3AQUvNADKxbZkfiXtnE"
csecret = "RHFxfGdZyn3K2jMXtwuhZ22Cy1yGOlHZWpF25ZydYWUY79tQhZ"
atoken = "1211288082-P6Ee5j6H0bjMfEze5t9mSWL9sSvyFvcYBL9WaV0"
asecret = "y31CRerUXliV7MDkGJO2WjS2Dw95M6L53fRJwsq2s9753"

#####################
###   Functions   ###
#####################

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

#Returns a list of words that starts with the input pattern like "#","http" etc
#[input: list] [output: list]
def getWordsStartingWith(words, startsWith):
    result = list()
    length = len(startsWith)

    for i in range(0, len(words)):
        word = words[i].strip()

        if word[:length] == startsWith:
            result.append(words[i])
    
    return result

#Returns a list of named entities
#[input: text] [output: dictionary]
def getTheNamedEntities(text):
    st = StanfordNERTagger(StanfordNERClassifierPath, StanfordNERjarPath)

    lstTag = st.tag(text.split())

    result = {}
    for tag in lstTag:
        #if str(tag[1]).lower() != 'o': #### CAUTION - DROPPING the General Term 'Object' items
        result [str(str(tag[0])).replace('.','')] = str(tag[1])
        
    return result

#Returns the expanded URL from links such as bit.ly
#[input: string] [output: string]
def getFullLink(URL):
    try:
        resp = urlopen(URL)
        result = resp.url
    except Exception:
        result = URL

    return result

#Removes the list items from a text
#[input: string] [output: string]
def removeListItemsFromText(text, lst):
    words = text.strip().split(" ")
    text = ' '.join([word for word in words if word not in lst])

    return text


###################
###   Classes   ###
###################

#Creating the Listener with the actual steps implementation in it
class listener(StreamListener):

    #Defining what to do when data become available
    def on_data(self, data):

        try:
            true = True

            ###########################
            ###   Data Processing   ###
            ###########################
            
            all_data = json.loads(data)
            
            tweetid = str(all_data["id"])
            username = all_data["user"]["screen_name"]
            tweettimestamp = all_data["created_at"]
            orig_tweet = all_data["text"]
            
            tweet_lowercase = orig_tweet.lower()
            tweet_lc_stopwords = removeStopwords(tweet_lowercase)
            tweet_lc_stopwordsList = tweet_lc_stopwords.split(" ")

            is_retweet = tweet_lc_stopwords[:2] == "rt"
            lang = all_data["user"]["lang"]
            
            hashtags = getWordsStartingWith(tweet_lc_stopwordsList, "#")
            #many links on the actual tweets go "https:...", so "//" are removed
            URLs = getWordsStartingWith(tweet_lc_stopwordsList, "http:")
            URLs += getWordsStartingWith(tweet_lc_stopwordsList, "https:")
            
            for i in range(0, len(URLs)):
                URLs[i] = getFullLink(URLs[i])
            
            mentions = getWordsStartingWith(tweet_lc_stopwordsList, "@")
            
            tweet_lc_stopwords = removeListItemsFromText(tweet_lc_stopwords, "rt ")
            tweet_lc_stopwords = removeListItemsFromText(tweet_lc_stopwords, hashtags)
            tweet_lc_stopwords = removeListItemsFromText(tweet_lc_stopwords, URLs)
            proc_tweet = removeListItemsFromText(tweet_lc_stopwords, mentions)


            #########################################
            namedEntities = getTheNamedEntities(orig_tweet)

            proc_data = { "id": tweetid,
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
                        }
            
            #proc_data_JSON = bson.json_util.dumps(proc_data, indent=4)


            ###########################
            ###   Saving the Data   ###
            ###########################

            ##Savin them as JSON inside a txt file
            ##a is for Append
            #saveFile = open('Actual_Ref_Tweets.txt', 'a')
            #saveFile.write(data)
            #saveFile.write('\n')
            #saveFile.close()

            
            ##Inserting them to the MySQL database
            #c.execute("INSERT INTO reftweets (time, username, orig_tweet) VALUES (%s,%s,%s)", (time.time(), username, orig_tweet))
            #conn.commit()


            #Inserting them to the MongoDB databse
            result = collection.insert_one(all_data)  #The Full JSON format
            result2 = proc_coll.insert_one(proc_data) #The Processed JSON format
            
            print("Full Data Mongo ID: ", result.inserted_id,
                  ",", "Proc Data Mongo ID: ", result2.inserted_id)

            print(orig_tweet)
            #print((username,str(orig_tweet).encode("utf-8")))

            return true

        #in case internet drops or something, let's not stop the whole procedure
        except BaseException as e:
            print ('failed with error: ', str(e))
            
            saveFile = open('Problem_Encountered.txt', 'a')
            eMessage = 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n\n'
            #saveFile.write(eMessage)
            saveFile.close()
            
            time.sleep(1)

    #Defining what to do in case of an error
    def on_error(self, status):
        print (status)


################
###   Main   ###
################

try:
    #Authenticating ourselves for the API
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)

    twitterStream = Stream(auth, listener())
    
except Exception as e:
    print (str(e))
    
    saveFile = open('Problem_Encountered.txt', 'a')
    eMessage = 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n\n'
    #saveFile.write(eMessage)
    saveFile.close()

#Streaming ONLY ENGLISH tweets
#These are the keywords we'd like to collect about
while True:
    try:
        twitterStream.filter(languages=["en"], track=["migrants", "migration crisis",  "migration flow",  "refugees",  "#RefugeeCrisis",
                                "#refugeesGr",  "#refugeeswelcome",  "#WelcomeRefugees",  "#ProMuslimRefugees",
                                "asylum seekers",  "human rights",  "#helpiscoming",  "solidarity",
                                "#solidaritywithrefugees",  "Balkan route",  "irregular migrants",  "borders",
                                "open borders",  "border closure",  "border share",  "No borders",  "#OpentheBorders",
                                "Syria",  "Iraq",  "Afghanistan",  "Pakistan",  "islamists",  "ISIS",  "daesh",
                                "muslims",  "Idomeni",  "Calais",  "Lesbos",  "Lesvos",  "Lesbosisland",
                                "migrant camps",  "refugee camps",  "#safepassage",  "rapefugees",  "#antireport ",
                                "Aylan",  "European Mobilisation",  "Amnesty International",  "Frontex",  "UNHCR",
                                "UN Refugee Agency",  "#FortressEurope",  "@MovingEurope"])
    except Exception as e:
        print (str(e))
        
        saveFile = open('Problem_Encountered.txt', 'a')
        eMessage = 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n\n'
        #saveFile.write(eMessage)
        saveFile.close()
        continue


