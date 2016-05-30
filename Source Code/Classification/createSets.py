#region Imports
import os
import sys
import time
import json
import encodings
from someFunctions import *
from datetime import datetime
from nltk.corpus import stopwords
#from getch import getch, pause, pause_exit
from nltk.tag.stanford import StanfordNERTagger
from nltk import PorterStemmer


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



#Initializing the stemmer
stemmer = PorterStemmer()
bigList = list()

count = 0
#Reading the groundtruth file
with open("anotations.txt") as anoFile:
	for line in anoFile:
		textList = line.split('\t')
		
		textList.pop(0)
		#print(textList[-1])

		tweetLowercase = textList[-2].lower()
		
		tweetCleaned = removeListItemsNew(tweetLowercase, "rt")
		tweetCleaned = removeListItemsNew(tweetCleaned, "#")
		tweetCleaned = removeListItemsNew(tweetCleaned, "http")
		tweetCleaned = removeListItemsNew(tweetCleaned, "@")
		#tweetCleaned = removeListItemsNew(tweet_cleaned, other_possible_user_mentions)
        
		tweetCleaned = removeSpecialCharsFromText(tweetCleaned)
		tweetCleaned = removeStopwords(tweetCleaned)
		tweetCleaned = tweetCleaned.strip()
		tweetLowerList = tweetCleaned.split(' ')

		#singles = [stemmer.stem(stemTweet) for stemTweet in tweetLowerList]

		#stemmedString = ''


		#for word in singles:
		#	stemmedString += word + ' '

		
		smallList = list()

		#smallList.append((singles, textList[-1]))
		sentiment = textList[-1][:-1]
		bigList.append((tweetLowerList, sentiment))
		#print(bigList)	
		#inpp = input('Pause')
		#if inpp == 'stop':
		#	sys.exit()
		




wordFeatures = get_word_features(get_words_in_tweets(bigList))
#print(wordFeatures)

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in wordFeatures:
        features['contains(%s)' % word] = (word in document_words)
    return features

training_set = nltk.classify.apply_features(extract_features, bigList)
classifier = nltk.NaiveBayesClassifier.train(training_set)
print (classifier.show_most_informative_features(32))
print('Accuracy:')
print (nltk.classify.util.accuracy(classifier, training_set))

tweet = 'i am very happy and joyfull. I love it and i am pleased'
#stemmedTweet = [stemmer.stem(stemTweet) for stemTweet in tweet]

#stemmedStringg = ''
#for word in stemmedStringg:
#	stemmedStringg += word + ' '

print (classifier.classify(extract_features(tweet.split())))


	

