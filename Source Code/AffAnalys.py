#region Imports
import os
import sys
import time
import json
import encodings
from Functions import *
from datetime import datetime
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordNERTagger
from nltk import PorterStemmer
from collections import Counter
import pdb
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
AnotationsTxt = CurDir + "AffectiveAnalysis/Anotations.txt"
ClassificationLogFile = 'Classification.log'
stemmer = PorterStemmer()
bigList = list()

#Connect to a MongoDB Database
client = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
db = client['mongorefcon']
StemmedTweets = db['StemmedTweets']
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
    topicResult = open(topicResultstxt, 'w')
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

#Extracting the features of the tweet without term frequencies
def extract_features(document):
    document_words = set(document)
    features = {}
    for word in wordFeatures:
        features['contains(%s)' % word] = (word in document_words)
    return features

#Extracting the features of the tweet with term frequencies
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

#region TrainingPreProcessing

#Reads and processes the topics' tweets
print("Reading and processing the topics' tweets")
LDA_csv_reader = open(FilteredLDAtop100Csv)
procTweetsLDA = open(topicTweetsLDATxt, 'w')
for row in LDA_csv_reader:
    tweetID = row.replace('\n','')

    for RawTweet in StemmedTweets.find({ "id": tweetID }):

        tweet_text = RawTweet['proc_tweet']
        tweet_text = tweet_text.replace('\n', '')
        tweet_text = tweet_text.replace('&gt;', '')
        tweet_text = tweet_text.replace('&lt;', '')
        tweet_text = tweet_text.replace('&amp;', '')
        tweet_text = removeSpecialCharsFromText(tweet_text)

        tweet_text = removeTextFromText(tweet_text, "rt")
        tweet_text = removeTextFromText(tweet_text, "#")
        tweet_text = removeTextFromText(tweet_text, "http")
        tweet_text = removeTextFromText(tweet_text, "@")

        try:
            procTweetsLDA.write(tweet_text + '\n')
        except:
            procTweetsLDA.write('dummy text\n')

count = 0
#Reading the ground-truth file
print("Reading the ground-truth file")
with open(AnotationsTxt) as anoFile:
	for line in anoFile:
		textList = line.split('\t')
		textList.pop(0)
		tweetLowercase = textList[-2].lower()

		#Cleaning the tweets
		tweetCleaned = removeTextFromText(tweetLowercase, "rt")
		tweetCleaned = removeTextFromText(tweetCleaned, "#")
		tweetCleaned = removeTextFromText(tweetCleaned, "http")
		tweetCleaned = removeTextFromText(tweetCleaned, "@")
		tweetCleaned = removeSpecialCharsFromText(tweetCleaned)
		tweetCleaned = removeStopwords(tweetCleaned)
		tweetCleaned = tweetCleaned.strip()
		tweetLowerList = tweetCleaned.split(' ')

		#Stemming (Accuracy seems to drop with stemming on!)
		#StemmedTweetWords = [stemmer.stem(stemTweet) for stemTweet in tweetLowerList]
		#stemmedString = ''
		#for word in StemmedTweetWords:
		#	stemmedString += word + ' '
		#smallList = list()

		sentiment = textList[-1][:-1]
		bigList.append((tweetLowerList, sentiment))
        #For the stemmer (if used)
		#bigList.append((StemmedTweetWords, sentiment))
		#smallList.append((StemmedTweetWords, sentiment))

#Splitting the set into train and test
train_data = bigList[:int(len(bigList) * 0.75)]
test_data = bigList[int(len(bigList) * 0.75):]

print("Getting Word Features")
wordFeatures = get_word_features(get_words_in_tweets(train_data))
#endregion

#region Classifying

#Naive Bayes
WriteLog("\nNaive Bayes Training\n", ClassificationLogFile)
NaiveBayesClassifier = nltk.NaiveBayesClassifier.train(training_set)
WriteLog(NaiveBayesClassifier.show_most_informative_features(32), ClassificationLogFile) #Shows Statistics (High Valued Features)

#Naive Bayes Accuracy
WriteLog("\nNaive Bayes Training Set Accuracy:" + str(nltk.classify.util.accuracy(NaiveBayesClassifier, testing_set)), ClassificationLogFile)

#Naive Bayes Classification
WriteLog("\nNaive Bayes Classification", ClassificationLogFile)
DoClassify(NaiveBayesClassifier, NBtopicResultsTxt, topicTweetsLDATxt)

#SVM Classifier
WriteLog("\nEntering SVM", ClassificationLogFile)
testD = list()
for dictPair in testing_set:
	testD.append(dictPair[0])

trainD = list()
gTruth = list()

#Formatting the Data
for dictPair in training_set:
	trainD.append(dictPair)

for dictPair in testing_set:
	testD.append(dictPair[0])
	gTruth.append(dictPair[1])

WriteLog("Starting SVM Training", ClassificationLogFile)
SVMClassifier = SklearnClassifier(SVC(), sparse=False).train(trainD)
predictions = SVMClassifier.classify_many(testD)

WriteLog("\nSVM Predictions:", ClassificationLogFile)
print(predictions)
WriteLog("\nSVM Training Set Accuracy:", ClassificationLogFile)
print(accuracy_score(gTruth, predictions, normalize=True, sample_weight=None))

#SVM Classification
WriteLog("\nSVM Classification", ClassificationLogFile)
DoClassify(SVMClassifier, SVMtopicResultsTxt, topicTweetsLDATxt)

#Decision Trees
WriteLog("\nDecision Trees Training", ClassificationLogFile)
DecisionTreesClassifier = nltk.classify.DecisionTreeClassifier.train(training_set, entropy_cutoff=0, support_cutoff=0)

#Decision Trees Accuracy
WriteLog("\nDecision Trees Training Set Accuracy:", ClassificationLogFile)
print(nltk.classify.util.accuracy(DecisionTreesClassifier, testing_set))

#Decision Trees Classification
WriteLog("\nDecision Trees Classification", ClassificationLogFile)
DoClassify(DecisionTreesClassifier, DTtopicResultsTxt, topicTweetsLDATxt)

#region Cross Validation
#Cross Validation (Caution! Cross Validation takes a relatively very long time to be completed!)
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
    predictions = classifier.classify_many(testing_this_round)
    accuracy_sum += accuracy_score(gTruth, predictions, normalize=True, sample_weight=None)
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

#endregion
