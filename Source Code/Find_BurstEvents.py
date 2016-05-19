from pymongo import MongoClient
from datetime import datetime
import csv

#region Initialisation
client = MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
collection = db['proctweets']

def finddates():
    datefile = open('datefile.csv', 'w')

    try:
        for ProcTweet in collection.find(): #in case we need to continue from a particular place in the collection, add the appropriate skip argument on find()
            #region Acquiring basic info from the Raw Twitter JSON
            tweet_id = ProcTweet["id"]
            tweet_datetime = ProcTweet["datetime"]

            newdate = datetime.strptime(tweet_datetime,'%a %b %d %X %z %Y').strftime('%d/%m/%y %X')

            datefile.write(tweet_id + "," + newdate + "\n")

        datefile.close()
    except Exception as e:
        eMessage = 'Main error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n'
        print (str(eMessage))
        saveFile = open('FindBurstEvent_Problems.txt', 'a')
        saveFile.write(eMessage)
        saveFile.close()
        #endregion

finddates()
