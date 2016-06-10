#region Imports
import os
import sys
import time
import json
import encodings
from someFunctions import *
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


def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
        all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)

    #for i in wordlist:
    #    print(i + ' ' + str(wordlist[i]))
    word_features = wordlist.keys()
    return word_features

#-----------------------------------------------------------------------------------------------
def cross_validation(training_set, num_folds):
    accuracy_sum = 0
    subset_size = int(len(training_set) / num_folds)

    for i in range(num_folds):
        training_this_round = training_set[:i*subset_size] + training_set[(i+1)*subset_size:]
        testing_this_round = training_set[i*subset_size:][:subset_size]

        classifier = nltk.NaiveBayesClassifier.train(training_this_round)
        accuracy_sum += nltk.classify.util.accuracy(classifier, testing_this_round)

    return accuracy_sum / num_folds
#-----------------------------------------------------------------------------------------------

#Initializing the stemmer
stemmer = PorterStemmer()
bigList = list()

#Reads and procesing the tweets of the topics
#readTweets()

count = 0
#Reading the groundtruth file
with open("Anotations.txt") as anoFile:
	for line in anoFile:

		textList = line.split('\t')

		textList.pop(0)

		tweetLowercase = textList[-2].lower()

		#Cleaning the tweets
		tweetCleaned = removeListItemsNew(tweetLowercase, "rt")
		tweetCleaned = removeListItemsNew(tweetCleaned, "#")
		tweetCleaned = removeListItemsNew(tweetCleaned, "http")
		tweetCleaned = removeListItemsNew(tweetCleaned, "@")

		#tweetCleaned = removeListItemsNew(tweet_cleaned, other_possible_user_mentions)

		tweetCleaned = removeSpecialCharsFromText(tweetCleaned)
		tweetCleaned = removeStopwords(tweetCleaned)
		tweetCleaned = tweetCleaned.strip()
		tweetLowerList = tweetCleaned.split(' ')

		#Stemming code
		#singles = [stemmer.stem(stemTweet) for stemTweet in tweetLowerList]
		#stemmedString = ''
		#for word in singles:
		#	stemmedString += word + ' '
		#smallList = list()

		sentiment = textList[-1][:-1]
		bigList.append((tweetLowerList, sentiment))
		#bigList.append((singles, sentiment))
		#smallList.append((singles, sentiment))

#Spliting the set into train and test
train_data = bigList[:int(len(bigList) * 0.75)]
test_data = bigList[int(len(bigList) * 0.75):]


wordFeatures = get_word_features(get_words_in_tweets(train_data))
#print(wordFeatures)

#Extracting the features of the tweet without term frequencies
def extract_features(document):
    document_words = set(document)
    features = {}
    for word in wordFeatures:
        features['contains(%s)' % word] = (word in document_words)

    #print(features)
    #inppp = input("Pause:")
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

training_set = nltk.classify.apply_features(extract_features, train_data)
testing_set = nltk.classify.apply_features(extract_features, test_data)

#Naive Bayes code
print('Training')
classifier = nltk.NaiveBayesClassifier.train(training_set)
#print (classifier.show_most_informative_features(32))

#Decision trees Code
#classifier = nltk.classify.DecisionTreeClassifier.train(training_set, entropy_cutoff=0, support_cutoff=0)

#Accuracy
print('Accuracy')
print (nltk.classify.util.accuracy(classifier, testing_set))

#testD = list()
#for dictPair in testing_set:
#	testD.append(dictPair[0])

#print(classifier.classify_many(testD))

#SVM classifier

#trainD = list()
#testD = list()
#gTruth = list()

##Setting the data in the correct format
#for dictPair in training_set:
#	trainD.append(dictPair)

#for dictPair in testing_set:
#	testD.append(dictPair[0])
#	gTruth.append(dictPair[1])

#print('Starting Training.')
#classifier = SklearnClassifier(SVC(), sparse=False).train(trainD)
#predictions = classifier.classify_many(testD)

##print(predictions)
##print('Accuracy:')

##SKlearn Accuracy
#print(accuracy_score(gTruth, predictions, normalize=True, sample_weight=None))


# Clasifying all the tweets of each event and assigning sentiment to it
counter = 0
topicSentiments = dict()
topicResult = open('topicResults.txt', 'w')
with open("topicTweetsLDA.txt") as topicFile:
	for line in topicFile:
		if counter != 100:
			tSentiment = classifier.classify(extract_features(line.split()))

			if tSentiment in topicSentiments.keys():
				topicSentiments[tSentiment] += 1
			else:
				topicSentiments[tSentiment] = 1
			counter += 1
			counter2 +=1
		else:
			majorSentiment = 'joy'
			topicSentiments[majorSentiment] = 1
			for sentiKey in topicSentiments.keys():
				if topicSentiments[majorSentiment] < topicSentiments[sentiKey]:
					majorSentiment = sentiKey
			
			print(counter2)
			sett += 1
			topicResult.write(majorSentiment +'\n')
			topicSentiments.clear()
			counter = 0

topicResult.close()


#Cross Validation code
#-----------------------------------------------------------------------------------------------
#num_folds = 10
#cross_validation_accuracy = cross_validation(training_set, num_folds)

#print('Cross validation accuracy:')
#print(cross_validation_accuracy)
#-----------------------------------------------------------------------------------------------
