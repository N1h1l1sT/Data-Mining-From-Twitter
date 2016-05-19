#region Imports
import time
import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from pymongo import MongoClient
from datetime import datetime
#endregion

#region Initialisation
client = MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
collection = db['refcrisis']

#We need the consumer key, consumer secret, access token, access secret.
ckey = "jrzcRp3AQUvNADKxbZkfiXtnE"
csecret = "RHFxfGdZyn3K2jMXtwuhZ22Cy1yGOlHZWpF25ZydYWUY79tQhZ"
atoken = "1211288082-P6Ee5j6H0bjMfEze5t9mSWL9sSvyFvcYBL9WaV0"
asecret = "y31CRerUXliV7MDkGJO2WjS2Dw95M6L53fRJwsq2s9753"
#endregion

#region Classes
#Creating the Listener with the actual steps implementation in it
class listener(StreamListener):

    #Defining what to do when data become available
    def on_data(self, data):

        try:
            all_data = json.loads(data)
            #Inserting them to the MongoDB database
            result = collection.insert_one(all_data)  #The Full JSON format

            try:
                print(all_data["text"])
            except Exception as ex:
                print ("Error on printing the tweet: ", str(ex))

            return true

        #in case internet drops or something, let's not stop the whole procedure
        except BaseException as e:
            print ('failed with error: ', str(e))
            saveFile = open('Problem_Encountered.txt', 'a')
            eMessage = 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n\n'
            saveFile.write(eMessage)
            saveFile.close()
            time.sleep(0.5)

    #Defining what to do in case of an error
    def on_error(self, status):
        print (status)

#endregion

#region Main
try:
    #Authenticating ourselves for the API
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    twitterStream = Stream(auth, listener())

except Exception as e:
    print (str(e))
    saveFile = open('Problem_Encountered.txt', 'a')
    eMessage = 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n\n'
    saveFile.write(eMessage)
    saveFile.close()

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
        saveFile.write(eMessage)
        saveFile.close()
        continue
#endregion