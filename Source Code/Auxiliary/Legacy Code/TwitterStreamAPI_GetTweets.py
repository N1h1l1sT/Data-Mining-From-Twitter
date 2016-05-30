from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from pymongo import MongoClient #For MongoDB Database
from datetime import datetime
#import MySQLdb                 #For MySQL Database
import time
import json

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


#We need the consumer key, consumer secret, access token, access secret.
ckey = "jrzcRp3AQUvNADKxbZkfiXtnE"
csecret = "RHFxfGdZyn3K2jMXtwuhZ22Cy1yGOlHZWpF25ZydYWUY79tQhZ"
atoken = "1211288082-P6Ee5j6H0bjMfEze5t9mSWL9sSvyFvcYBL9WaV0"
asecret = "y31CRerUXliV7MDkGJO2WjS2Dw95M6L53fRJwsq2s9753"

#Creating the Listener
class listener(StreamListener):

    #Defining what to do when data become available
    def on_data(self, data):

        try:
            true = True
            #Getting the tweets and usernames
            all_data = json.loads(data)
            tweet = all_data["text"]
            username = all_data["user"]["screen_name"]

            ##Savin them (also) as JSON inside a txt file
            ##a is for Append
            #saveFile = open('Actual_Ref_Tweets.txt', 'a')
            #saveFile.write(data)
            #saveFile.write('\n')
            #saveFile.close()
            
            ##Inserting them to the MySQL databse
            #c.execute("INSERT INTO reftweets (time, username, tweet) VALUES (%s,%s,%s)", (time.time(), username, tweet))
            #conn.commit()

            #Inserting them to the MongoDB databse as FULL JSON
            result = collection.insert_one(all_data)
            print("ID = ", result.inserted_id)
            
            print(data)
            #print((username,tweet))
            return true

        #in case internet drops or something, let's not stop the whole procedure
        except BaseException as e:
            print ('failed with error: ', str(e))
            time.sleep(5)

    #Defining what to do in case of an error
    def on_error(self, status):
        print (status)

try:
    #Authenticating ourselves for the API
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)

    twitterStream = Stream(auth, listener())

    #Streaming ONLY ENGLISH tweets
    #These are the keywords we'd like to collect about
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
    
