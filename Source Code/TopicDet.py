#region Imports
import lda
import sys
import csv
import pymongo
import numpy as np
from Functions import *
from datetime import datetime
from nltk.tokenize import RegexpTokenizer
#endregion

#region Initialisation
LogDir = "./Source Code/Logs/"
LDADir = "./Source Code/LDA/"
LDALogFile = 'LDA.log'
LDACsvFile = 'LDA.csv'
SortLDACsv = 'SortedLDA.csv'
FilteredLDATop10Csv = 'FilteredLDA_top10.csv'
FilteredLDATop100Csv = 'FilteredLDA_top100.csv'
FilteredLDATweetsCsv = 'FilteredLDA_Tweets.csv'

#Connect to a MongoDB Database
MongoDBCon = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
MongoDBDatabase = MongoDBCon['RefugeeCrisisCon']
DistinctStemmedTweets_coll = MongoDBDatabase['DistinctTweets']
#endregion

#region Functions
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
                distinctwords[word] = i
                i += 1
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


def get_MongoDBFieldContent(collection, FieldName):
    try:
        doc_set = []
        for RawTweet in collection.find(): #.limit(1000): #in case we need to continue from a particular place in the collection, add the appropriate skip argument on find()
            try:
                tmpTweet = RawTweet[FieldName]
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
    WriteLog('.-= New LDA Iteration =-.\n', LDALogFile)

    #region LDAPreProcessessing
    WriteLog('Getting the Titles [Tweets for the Frequency Table]\n', LDALogFile)
    titles = get_MongoDBFieldContent(DistinctStemmedTweets_coll, "stemmed_tweet") #Tweets to be used as documents for the LDA
    WriteLog("Getting the Tweets's IDs\n", LDALogFile)
    ids = get_MongoDBFieldContent(DistinctStemmedTweets_coll, "tweet_id")  #IDs of each tweet

    WriteLog('Creating the Vocabulary [Frequencies of words for each tweet]\n', LDALogFile)
    vocab = get_vocabulary(titles) #Distinct words

    WriteLog('Creating the Frequency Table [Titles times by Vocabulary size array with each tweet as a raw, each word as a column and #word occurrence as value]\n', LDALogFile)
    freqtable = get_frequency_table(titles, vocab) #tweets times by distinct words
    #endregion

    #region LDA
    WriteLog('Running the LDA\n', LDALogFile)
    nof_topics = 25
    n_iter = 1000
    random_state = 1
    WriteLog("nof_topics = " + str(nof_topics) + "\n" + "n_topics = " + str(nof_topics) +  "\n" + "random_state = " + str(random_state) + "\n", LDALogFile)

    WriteLog("Creating the Model\n", LDALogFile)
    model = lda.LDA(n_topics = nof_topics, n_iter = 1000, random_state = 1)

    WriteLog("Fitting the Frequency Table\n", LDALogFile)
    doc_topic = model.fit_transform(freqtable)

    WriteLog("Getting topic_word\n", LDALogFile)
    topic_word = model.topic_word_  # model.components_ also works

    n_top_words = 10
    WriteLog("n_top_words = " + str(n_top_words) + "\n", LDALogFile)

    LDA_csv = open(LDADir + LDACsvFile, 'w')

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
    input("Sort the ID List of the '" + LDACsvFile + "' file by topic and by weight, save it as '" + SortLDACsv + "' and press Enter")
    WriteLog("Extracting the ID of the Top 100 Tweets per Topic for Classification [" + FilteredLDATop100Csv + "]", LDALogFile)
    LDA_csv_reader = open(LDADir + SortLDACsv)
    LDA_csv_writer_Top100 = open(LDADir + FilteredLDATop100Csv, 'w')
    read_count = 0
    topic_id = 0
    for row in LDA_csv_reader:
        line_items = row.replace('\n','').split(',')
        line_items[1] = int(line_items[1])
        read_count += 1
        if read_count <= 100:
            LDA_csv_writer_Top100.write(str(line_items[0]) + '\n')
        if topic_id != line_items[1]:
            topic_id +=1
            read_count = 0
    LDA_csv_writer_Top100.close()

    #Extracting the Top 10 'Tweet ID, Topic ID, Topic Rank' per topic (found by LDA) to be used for manual topic comprehension
    WriteLog("Extracting the Tweet ID, Topic ID and Topic Rank of the Top 10 Tweets per Topic for Observation [" + FilteredLDATop10Csv + "]", LDALogFile)
    LDA_csv_reader = open(LDADir + SortLDACsv)
    LDA_csv_writer_Top10 = open(LDADir + FilteredLDATop10Csv, 'w')
    read_count = 0
    topic_id = 0
    for row in LDA_csv_reader:
        line_items = row.replace('\n','').split(',')
        line_items[1] = int(line_items[1])
        read_count += 1
        if read_count <= 10:
            LDA_csv_writer_Top10.write(str(line_items[0]) + '\t' + str(line_items[1]) + '\t' + str(line_items[2]) + '\n')
        if topic_id != line_items[1]:
            topic_id +=1
            read_count = 0
    LDA_csv_writer_Top10.close()
    #endregion

    #region ReadTweets
    #'Topic ID, Original Tweet Text' used for manual topic comprehension
    WriteLog("Extracting the Topic ID and Original Tweet Text based on the Tweet ID of the Top 10 Tweets per Topic for Observation [" + FilteredLDATweetsCsv + "]", LDALogFile)
    LDA_csv_reader = open(LDADir + FilteredLDATop10Csv)
    LDA_csv_writer = open(LDADir + FilteredLDATweetsCsv, 'w')

    for row in LDA_csv_reader:
        line_items = row.replace('\n','').split('\t')
        tweet_id = line_items[0]

        for RawTweet in DistinctStemmedTweets_coll.find({ "tweet_id": tweet_id }):
            tweet_text = str(RawTweet['proc_tweet'].encode('utf8'))
            print("Topic id = " + line_items[1] + '\t' + tweet_text)
            LDA_csv_writer.write("Topic id = " + line_items[1] + '\t' + tweet_text + '\n')
    LDA_csv_writer.close()
    #endregion

    WriteLog('Finished successfully\n\n\n', LDALogFile)

except Exception as e:
    eMessage = 'Main error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n'
    print (str(eMessage))
    saveFile = open(LogDir + 'Topic_Detection_Problems.txt', 'a')
    saveFile.write(eMessage)
    saveFile.close()
#endregion
