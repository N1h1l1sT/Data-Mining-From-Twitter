from pymongo import MongoClient
from datetime import datetime
import csv

#region Initialisation
client = MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
collection = db['refcrisis']

def finddates():
    datefile = open('datefile_users.csv', 'w')

    try:
        for ProcTweet in collection.find(): #in case we need to continue from a particular place in the collection, add the appropriate skip argument on find()
            #region Acquiring basic info from the Raw Twitter JSON
            username = ProcTweet["user"]["screen_name"]
            tweet_datetime = ProcTweet["created_at"]

            newdate = datetime.strptime(tweet_datetime,'%a %b %d %X %z %Y').strftime('%d/%m/%y %X')

            datefile.write(username + "," + newdate + "\n")

        datefile.close()
    except Exception as e:
        eMessage = 'Main error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n'
        print (str(eMessage))
        saveFile = open('FindBurstEvent_Problems.txt', 'a')
        saveFile.write(eMessage)
        saveFile.close()
        #endregion

finddates()
