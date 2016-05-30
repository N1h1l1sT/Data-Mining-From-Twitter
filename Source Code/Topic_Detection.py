import lda
import sys
import pymongo
import numpy as np
from datetime import datetime
from nltk.tokenize import RegexpTokenizer
from getch import getch, pause, pause_exit

LogDir = "./Source Code/Logs/"

def main():
    WriteLog('.-= New LDA Iteration =-.\n')
    WriteLog('Creating the Client\n')
    client = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
    WriteLog('Connecting to mongorefcon\n')
    db = client['mongorefcon']
    WriteLog('Using ProcessedTweets\n')
    StemmedTweets = db['ProcessedTweets']

    print("Getting the Titles")
    WriteLog('Getting the Titles\n')
    titles = get_titles(StemmedTweets, "stemmed_tweet")
    print("Creating the Vocabulary")
    WriteLog('Creating the Vocabulary\n')
    vocab = get_vocabulary(titles)

    #print(vocab)

    print("Creating the Frequency Table")
    WriteLog('Creating the Frequency Table\n')
    freqtable = get_frequency_table(titles, vocab)

    print("Running the LDA")
    WriteLog('Running the LDA\n')
    runLDA(titles, vocab, freqtable)
    WriteLog('Finished successfully\n\n\n')
    print("Press any key to terminate.")
    getch()

def runLDA(titles, words, freqtable):
    nof_topics = 25
    n_iter=1000
    random_state=1
    WriteLog("nof_topics = " + str(nof_topics) + "\n" + "n_topics = " + str(nof_topics) +  "\n" + "random_state = " + str(random_state) + "\n")

    WriteLog("Creating the Model\n")
    model = lda.LDA(n_topics=nof_topics, n_iter=1000, random_state=1)
    WriteLog("Fitting the Frequency Table\n")
    model.fit(freqtable)  # model.fit_transform(X) is also available
    WriteLog("Getting topic_word\n")
    topic_word = model.topic_word_  # model.components_ also works
    n_top_words = 10
    WriteLog("n_top_words = " + str(n_top_words) + "\n")

    WriteLog("Creating the Vocabulary\n")
    vocab = list(words.keys())

    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
        print(' \n Topic {}: {}'.format(i, ' '.join(topic_words)))
        WriteLog('\n\n Topic {}: {}'.format(i, ' '.join(topic_words)))

    doc_topic = model.doc_topic_
    for i in range(nof_topics):
        print("{} (top topic: {})".format(titles[i], doc_topic[i].argmax()))
        WriteLog("{} (top topic: {})".format(titles[i], doc_topic[i].argmax()))

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

def WriteLog(text):
    LDA_Log_Write = open(LogDir + 'LDA.log', 'a')
    LDA_Log_Write.write(text)
    LDA_Log_Write.close()


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

def get_titles(collection, TweetTextFieldName):
    doc_set = []
    try:
        for RawTweet in collection.find(): #in case we need to continue from a particular place in the collection, add the appropriate skip argument on find()
            try:
                tmpTweet = RawTweet[TweetTextFieldName]
                doc_set.append(tmpTweet)
            except Exception as ex:
                print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
                continue

    except Exception as ex:
        print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')

    return doc_set

main()
