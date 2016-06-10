#region Imports
import lda
import sys
import pymongo
import numpy as np
from datetime import datetime
from nltk.tokenize import RegexpTokenizer
from getch import getch, pause, pause_exit
import csv
#endregion

#region Initialisation
LogDir = "./Source Code/Logs/"
LDADir = "./Source Code/LDA/"
LDACsvFile = 'LDA.csv'
LDALogFile = 'LDA.log'
OrderedLDACsv = 'OrderedLDA.csv'
FilteredLDATop10Csv = 'FilteredLDA_top10.csv'
FilteredLDATop100Csv = 'FilteredLDA_top100.csv'

#Connect to a MongoDB Database
client = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
StemmedTweets = db['StemmedTweets']
DistinctStemmedTweets = db['DistinctStemmedTweets']
#endregion

#region Functions
def WriteLog(text):
    LDA_Log_Write = open(LogDir + LDALogFile, 'a')
    LDA_Log_Write.write(text)
    LDA_Log_Write.close()
    print(text)

def get_vocabulary(doc_set):
    tokenizer = RegexpTokenizer(r'\w+')
    distinctwords = {}
    i = 0
    # loop through document list
    for text in doc_set:
        raw = text.lower()
        tokens = tokenizer.tokenize(raw)
        for word in tokens:
            if word not in distinctwords:
                #distinctwords.append(word)
                distinctwords[word] = i
                i = i + 1
    return distinctwords

def get_frequency_table(titles, vocab):
    tokenizer = RegexpTokenizer(r'\w+')
    freqtable = np.ndarray(shape=(len(titles),len(vocab)), dtype=int, order='C')
    freqtable.fill(0)
    for i in range(0,len(titles)):
        raw = titles[i].lower()
        tokens = tokenizer.tokenize(raw)
        for token in tokens:
            index = vocab[token]
            freqtable[i][index] +=1
    return freqtable


def get_titles(collection, TweetTextFieldName):
    doc_set = []
    try:
        for RawTweet in collection.find(): #.limit(1000): #in case we need to continue from a particular place in the collection, add the appropriate skip argument on find()
            try:
                tmpTweet = RawTweet[TweetTextFieldName]
                doc_set.append(tmpTweet)
            except Exception as ex:
                print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
                continue
    except Exception as ex:
        print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
    return doc_set
#endregion

#region Main
try:
    WriteLog('.-= New LDA Iteration =-.\nGetting the Titles\n')

    #region DistinctStemmedTweets
    #Creating the DistinctStemmedTweets
    doc_set1 = []
    doc_set2 = []

    for RawTweet in StemmedTweets.distinct("stemmed"):
        try:
            doc_set1.append(RawTweet)
        except Exception as ex:
            print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
            continue

    for i in range(0, len(doc_set1)):
        stemmed = doc_set1[i]

        for RawTweet in StemmedTweets.find({"stemmed": stemmed}).limit(1):
                DistinctStemmedTweets.insert_one(RawTweet)

    #endregion

    #region LDAPreProcessessing
    titles = get_titles(DistinctStemmedTweets, "stemmed") #Tweets to be used as documents for the LDA
    ids = get_titles(DistinctStemmedTweets, "id")  #IDs of each tweet

    WriteLog('Creating the Vocabulary\n')
    vocab = get_vocabulary(titles) #Distinct words

    WriteLog('Creating the Frequency Table\n')
    freqtable = get_frequency_table(titles, vocab) #tweets times by distinct words
    #endregion

    #region LDA
    WriteLog('Running the LDA\n')
    nof_topics = 25
    n_iter = 1000
    random_state = 1
    WriteLog("nof_topics = " + str(nof_topics) + "\n" + "n_topics = " + str(nof_topics) +  "\n" + "random_state = " + str(random_state) + "\n")

    WriteLog("Creating the Model\n")
    model = lda.LDA(n_topics = nof_topics, n_iter = 1000, random_state = 1)

    WriteLog("Fitting the Frequency Table\n")
    doc_topic = model.fit_transform(freqtable)

    WriteLog("Getting topic_word\n")
    topic_word = model.topic_word_  # model.components_ also works

    n_top_words = 10
    WriteLog("n_top_words = " + str(n_top_words) + "\n")

    WriteLog("Creating the Vocabulary\n")
    vocabl = list(vocab.keys())

    LDA_csv = open(LDADir + LDACsvFile, 'a')

    #unordered csv with columns: TweetID, TopicID, LDA-Given-Weight
    #is manually order by topic and by weight (e.g. via Excel)
    doc_topic = model.doc_topic_
    for i in range(len(ids)):
        Content_part1 = ids[i]
        Content_part2 = doc_topic[i].argmax()
        Content_part3 = doc_topic[i][Content_part2]
        LDA_csv.write(str(Content_part1) + ' ' + str(Content_part2) + ' ' + str(Content_part3) + '\n')
    LDA_csv.close()
    #endregion

    #region OrderedIdList
    #Extracting the Top 100 Tweet ID per topic (found by LDA) to be used for Classification
    input("Order the ID List'" + LDACsvFile + "' by topic and by weight and save it as '" + OrderedLDACsv + "'")
    LDA_csv_reader = open(LDADir + OrderedLDACsv)
    LDA_csv_writer1 = open(LDADir + FilteredLDATop10Csv, 'a')
    LDA_csv_writer2 = open(LDADir + FilteredLDATop100Csv, 'a')

    read_count = 0
    topic_id = 0
    for row in LDA_csv_reader:
        line_items = row.replace('\n','').split(',')
        line_items[1] = int(line_items[1])
        read_count += 1
        if read_count <= 100:
            LDA_csv_writer1.write(str(line_items[0]) + '\n')
        if topic_id != line_items[1]:
            topic_id +=1
            read_count = 0
    LDA_csv_writer1.close()

    #Extracting the Top 10 'Tweet ID, Topic ID, Topic Rank' per topic (found by LDA) to be used for manual topic comprehension
    read_count = 0
    topic_id = 0
    for row in LDA_csv_reader:
        line_items = row.replace('\n','').split(',')
        line_items[1] = int(line_items[1])
        read_count += 1
        if read_count <= 10:
            LDA_csv_writer2.write(str(line_items[0]) + '\t' + str(line_items[1]) + '\t' + str(line_items[2]) + '\n')
        if topic_id != line_items[1]:
            topic_id +=1
            read_count = 0
    LDA_csv_writer2.close()
    #endregion

    #region ReadTweets
    #'Topic ID, Original Tweet Text' used for manual topic comprehension
    LDA_csv_reader = open(LDADir + FilteredLDATop10Csv)
    LDA_csv_writer = open(LDADir + 'FilteredLDA_Tweets.csv', 'a')

    for row in LDA_csv_reader:
        line_items = row.replace('\n','').split('\t')
        tweet_id = line_items[0]

        for RawTweet in DistinctStemmedTweets.find({ "id": tweet_id }):
            tweet_text = str(RawTweet['proc_tweet'].encode('utf8'))
            print("Topic id = " + line_items[1] + '\t' + tweet_text)
            LDA_csv_writer.write("Topic id = " + line_items[1] + '\t' + tweet_text + '\n')
    LDA_csv_writer.close()
    #endregion

    WriteLog('Finished successfully\n\n\n')
    print("Press any key to terminate.")

except Exception as e:
    eMessage = 'Main error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n'
    print (str(eMessage))
    saveFile = open(LogDir + 'Topic_Detection_Problems.txt', 'a')
    saveFile.write(eMessage)
    saveFile.close()
#endregion


