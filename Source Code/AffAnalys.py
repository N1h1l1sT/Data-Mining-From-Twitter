#region Imports
import os
import sys
import csv
import time
import json
import nltk
import pymongo
import encodings
from Functions import *
from datetime import datetime
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordNERTagger
from nltk import PorterStemmer
from collections import Counter
from nltk.classify import SklearnClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
#endregion

#region Initialisation
CrossValidationNumFolds = 3
CurDir = "./Source Code/"
FilteredLDAtop100Csv = CurDir + "LDA/FilteredLDA_top100.csv"
topicTweetsLDATxt = CurDir + "AffectiveAnalysis/topicTweetsLDA.txt"
NBtopicResultsTxt = CurDir + "AffectiveAnalysis/NB_topicResults.txt"
DTtopicResultsTxt = CurDir + "AffectiveAnalysis/DT_topicResults.txt"
SVMtopicResultsTxt = CurDir + "AffectiveAnalysis/SVM_topicResults.txt"
AnnotationsTxt = CurDir + "AffectiveAnalysis/Annotations.txt"
AnnotationsProcessedTxt = CurDir + "AffectiveAnalysis/AnnotationsProcessed.txt"
AnnotationsStemmedTxt = CurDir + "AffectiveAnalysis/AnnotationsStemmed.txt"
ClassificationLogFile = 'Classification.log'
stemmer = PorterStemmer()
bigList = list()

#Connect to a MongoDB Database
MongoDBCon = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
MongoDBDatabase = MongoDBCon['RefugeeCrisisCon']
ProcessedTweets_coll = MongoDBDatabase['ProcessedTweets']
#endregion

#region Functions
#Classification Pre-processing
def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
        all_words.extend(words)
    return all_words

#Unique Words
def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

#Classifying all the tweets of each event and assigning a sentiment to it
def DoClassify(CurClassifier, topicResultsTxt, topicTweetsLDATxt):
    counter = 0
    topicSentiments = dict()
    topicResult = open(topicResultsTxt, 'w')
    with open(topicTweetsLDATxt) as topicFile:
        for line in topicFile:
            if counter != 100:
                tSentiment = CurClassifier.classify(extract_features(line.split()))

                if tSentiment in topicSentiments.keys():
                    topicSentiments[tSentiment] += 1
                else:
                    topicSentiments[tSentiment] = 1

                counter += 1

            else:
                majorSentiment = 'Dummy'
                topicSentiments[majorSentiment] = 1
                for sentiKey in topicSentiments.keys():
                    if topicSentiments[majorSentiment] < topicSentiments[sentiKey]:
                        majorSentiment = sentiKey

                topicResult.write(majorSentiment +'\n')
                topicSentiments.clear()
                counter = 0

    topicResult.close()

#Extracting the features of the tweet without term frequencies with the format as needed by the classifier
def extract_features(document):
    document_words = set(document)
    features = {}
    for word in wordFeatures:
        features['contains(%s)' % word] = (word in document_words)
    return features

#Extracting the features of the tweet with term frequencies with the format as needed by the classifier
def extract_featuresFreq(document):
	document_words = set(document)
	freqs = Counter(document)
	features = {}
	for word in wordFeatures:
		if word in document_words:
			    features['contains(%s)' % word] = freqs[word]
		else:
				features['contains(%s)' % word] = 0
	return features
#endregion

#region Main
try:
    WriteLog('.-= New Classification Iteration =-.\n', ClassificationLogFile)

    #region TrainingPreProcessing
    WriteLog("Beginning new Classification Iteration", ClassificationLogFile)

    ##Reads and saves each topic's top 100 tweets
    #WriteLog("Reading and processing the topics' tweets", ClassificationLogFile)
    #LDA_csv_reader = open(FilteredLDAtop100Csv)
    #procTweetsLDA = open(topicTweetsLDATxt, 'w')
    #for tweet_id in LDA_csv_reader:
    #    tweet_id = tweet_id.replace("\n", "")
    #    TweetJSON = ProcessedTweets_coll.find_one({ "tweet_id": tweet_id })
    #    procTweetsLDA.write(str(TweetJSON["proc_tweet"]).replace("\n", " ") + '\n')
    #procTweetsLDA.close()

    #Reading the ground-truth file

    WriteLog("Reading the processed ground-truth file", ClassificationLogFile)
    with open(AnnotationsProcessedTxt, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            bigList.append((row[0].split(' '), row[1]))

    #WriteLog("Reading the ground-truth file", ClassificationLogFile)
    #ProcessedAnnotations = open(AnnotationsProcessedTxt, 'w')
    #with open(AnnotationsTxt) as anoFile:
    #    for line in anoFile:
    #        textList = line.split('\t')
    #        textList.pop(0)
    #        tweetLowercase = textList[-2].lower()

		  #  #Cleaning the tweets
    #        tweetCleaned = removeTextFromText(tweetLowercase, "rt")
    #        tweetCleaned = removeTextFromText(tweetCleaned, "#")
    #        tweetCleaned = removeTextFromText(tweetCleaned, "http")
    #        tweetCleaned = removeTextFromText(tweetCleaned, "@")
    #        tweetCleaned = removeSpecialCharsFromText(tweetCleaned)
    #        tweetCleaned = removeStopwords(tweetCleaned, stopwords.words("english"))
    #        tweetCleaned = tweetCleaned.strip()
    #        tweetLowerList = tweetCleaned.split(' ')

    #        ##Stemming (Accuracy seems to drop with stemming on!)
    #        #StemmedTweetWords = [stemmer.stem(stemTweet) for stemTweet in tweetLowerList]
    #        #stemmedString = ''
    #        #for word in StemmedTweetWords:
    #        #	stemmedString += word + ' '

    #        sentiment = textList[-1][:-1]
    #        bigList.append((tweetLowerList, sentiment))
    #        #For the stemmer (if used)
    #        #bigList.append((StemmedTweetWords, sentiment))
    #        ProcessedAnnotations.write('"' + tweetCleaned + '", ' + sentiment + '\n')
    #ProcessedAnnotations.close()

    #Splitting the set into train and test
    train_data = bigList[:int(len(bigList) * 0.75)]
    test_data = bigList[int(len(bigList) * 0.75):]

    WriteLog("Getting Word Features", ClassificationLogFile)
    wordFeatures = get_word_features(get_words_in_tweets(train_data))

    WriteLog("Creating Training and Testing sets", ClassificationLogFile)
    training_set = nltk.classify.apply_features(extract_features, train_data)
    testing_set = nltk.classify.apply_features(extract_features, test_data)
    #endregion

    #region Classifying

    #region SVMClassifier
    WriteLog("\nEntering SVM", ClassificationLogFile)
    trainD = list()
    testD = list()
    gTruth = list()

    #Formatting the Data
    for dictPair in training_set:
        trainD.append(dictPair)
    for dictPair in testing_set:
        testD.append(dictPair[0])
        gTruth.append(dictPair[1])

    WriteLog("Starting SVM Training", ClassificationLogFile)
    SVMClassifier = SklearnClassifier(SVC(), sparse=False).train(trainD)
    SVMPredictions = SVMClassifier.classify_many(testD)

    WriteLog("SVM Training Set Accuracy:", ClassificationLogFile)
    WriteLog(str(accuracy_score(gTruth, SVMPredictions, normalize=True, sample_weight=None)), ClassificationLogFile)

    #SVM Classification
    WriteLog("SVM Classification", ClassificationLogFile)
    DoClassify(SVMClassifier, SVMtopicResultsTxt, topicTweetsLDATxt)

    #SVM Predictions
    WriteLog("SVM Predictions:", ClassificationLogFile)
    WriteLog(SVMPredictions, ClassificationLogFile)
    #endregion

    #region NaiveBayes
    WriteLog("\nNaive Bayes Training", ClassificationLogFile)
    NaiveBayesClassifier = nltk.NaiveBayesClassifier.train(training_set)
    WriteLog(NaiveBayesClassifier.show_most_informative_features(32), ClassificationLogFile) #Shows Statistics (High Valued Features)

    #Naive Bayes Accuracy
    WriteLog("Naive Bayes Training Set Accuracy:", ClassificationLogFile)
    WriteLog(str(nltk.classify.util.accuracy(NaiveBayesClassifier, testing_set)), ClassificationLogFile)

    #Naive Bayes Classification
    WriteLog("Naive Bayes Classification", ClassificationLogFile)
    DoClassify(NaiveBayesClassifier, NBtopicResultsTxt, topicTweetsLDATxt)

    #Naive Bayes Predictions
    testD = list()
    for dictPair in testing_set:
    	testD.append(dictPair[0])

    NBPredictions = NaiveBayesClassifier.classify_many(testD)
    WriteLog("Naive Bayes Predictions:", ClassificationLogFile)
    WriteLog(NBPredictions, ClassificationLogFile)
    #endregion

    #region DecisionTrees
    #The Decision Trees part, whilst working in principle, takes an enormous amount of time and is hence commented out
    WriteLog("\nDecision Trees Training", ClassificationLogFile)
    DecisionTreesClassifier = nltk.classify.DecisionTreeClassifier.train(training_set, entropy_cutoff=0, support_cutoff=0)

    #Decision Trees Accuracy
    WriteLog("Decision Trees Training Set Accuracy:", ClassificationLogFile)
    print(nltk.classify.util.accuracy(DecisionTreesClassifier, testing_set))

    #Decision Trees Classification
    WriteLog("Decision Trees Classification", ClassificationLogFile)
    DoClassify(DecisionTreesClassifier, DTtopicResultsTxt, topicTweetsLDATxt)

    #Decision Trees Predictions
    testD = list()
    for dictPair in testing_set:
    	testD.append(dictPair[0])

    DTPredictions = DecisionTreesClassifier.classify_many(testD)
    WriteLog("Decision Trees Predictions:", ClassificationLogFile)
    WriteLog(DTPredictions, ClassificationLogFile)
    #endregion

    #region Cross Validation
    #The Cross Validation part, whilst working in principle, takes an enormous amount of time and is hence commented out
    subset_size = int(len(training_set) / CrossValidationNumFolds)

    WriteLog("\nNaive Bayes Cross Validation Accuracy", ClassificationLogFile)
    accuracy_sum = 0
    for i in range(CrossValidationNumFolds):
        training_this_round = training_set[:i*subset_size] + training_set[(i+1)*subset_size:]
        testing_this_round = training_set[i*subset_size:][:subset_size]
        classifier = nltk.NaiveBayesClassifier.train(training_this_round)
        accuracy_sum += nltk.classify.util.accuracy(classifier, testing_this_round)
    WriteLog(str(CrossValidationNumFolds) + "-fold Cross Validation Accuracy: " + str(accuracy_sum / CrossValidationNumFolds), ClassificationLogFile)

    WriteLog("SVM Cross Validation Accuracy", ClassificationLogFile)
    accuracy_sum = 0
    for i in range(CrossValidationNumFolds):
        training_this_round = training_set[:i*subset_size] + training_set[(i+1)*subset_size:]
        testing_this_round = training_set[i*subset_size:][:subset_size]
        classifier = SklearnClassifier(SVC(), sparse=False).train(training_this_round)
        SVMPredictions = classifier.classify_many(testing_this_round)
        accuracy_sum += accuracy_score(gTruth, SVMPredictions, normalize=True, sample_weight=None)
    WriteLog(str(CrossValidationNumFolds) + "-fold Cross Validation Accuracy: " + str(accuracy_sum / CrossValidationNumFolds), ClassificationLogFile)

    WriteLog("Decision Trees Cross Validation Accuracy:", ClassificationLogFile)
    accuracy_sum = 0
    for i in range(CrossValidationNumFolds):
        training_this_round = training_set[:i*subset_size] + training_set[(i+1)*subset_size:]
        testing_this_round = training_set[i*subset_size:][:subset_size]
        classifier = nltk.classify.DecisionTreeClassifier.train(training_this_round, entropy_cutoff=0, support_cutoff=0)
        accuracy_sum += nltk.classify.util.accuracy(classifier, testing_this_round)
    WriteLog(str(CrossValidationNumFolds) + "-fold Cross Validation Accuracy: " + str(accuracy_sum / CrossValidationNumFolds), ClassificationLogFile)
    #endregion

    WriteLog("\nFinished Successfully!\n\n\n", ClassificationLogFile)
    #endregion

except Exception as e:
    eMessage = 'Main error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n'
    print (str(eMessage))
    saveFile = open(LogDir + 'AffectiveAnalysis_Problems.txt', 'a')
    saveFile.write(eMessage)
    saveFile.close()
#endregion
