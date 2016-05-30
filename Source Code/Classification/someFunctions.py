#region Imports
import os
import sys
import time
import json
import pymongo
import encodings
from datetime import datetime
from nltk.corpus import stopwords
#from getch import getch, pause, pause_exit
from nltk.tag.stanford import StanfordNERTagger
from nltk import PorterStemmer
import nltk

#region Functions
#Returns a list of words that starts with the input pattern like "#","http" etc.
#[input: list] [output: list]
def getWordsStartingWith(words, startsWith):
    result = list()
    length = len(startsWith)
    for i in range(0, len(words)):
        word = words[i].strip()
        if word[:length] == startsWith:
            result.append(words[i])
    return result

#Removes the stopwords from a text (warning: the input string must be in lowercase)
#[input: string] [output: string]
def removeStopwords(text):
    result = text
    words = text.strip().split(" ")
    stopwordsList = stopwords.words("english")
    result = ' '.join([word for word in words if word not in stopwordsList])
    return result

#Checks whether the input is in English
#[input: string] [output: boolean]
def isEnglish(text):
    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True
#Removes non English words
#[input: string] [output: list]
def removeNonEnglishText(text):
    result = list()
    words = text.strip().split(" ")

    for i in range(0, len(words)):
        if isEnglish(words[i]) == True:
            result.append(words[i])

    return result

#Removes the list items from a text
#[input: string] [output: string]
def removeListItemsFromText(text, lst):
    words = text.strip().split(" ")
    text = ' '.join([word for word in words if word not in lst])
    return text

#Removes the superfluous space characters
#[input: string] [output: string]

def removeListItemsNew(text, lst):
    words = text.strip().split(" ")
    text = ' '.join([word for word in words if lst not in word])
    return text

def SentenceStringStrip(text):
    words = text.strip().split(" ")
    result = ' '.join(word.strip() for word in words if word.strip())
    return result

#Removes Special Characters from a string
#[input: string] [output: string]
def removeSpecialCharsFromText(text):
    dirtyChars = [',', '.', ';', '?', '/', '\\', '`', '[', ']', '"', ':', '>', '<', '|', '-', '_', '=', '+', '(', ')', '^', '{', '}', '~', '\'', '*', '&', '%', '$', '!', '@', '#']
    for i in range(0, len(dirtyChars)):
        text = str.replace(text, dirtyChars[i], " ")
    result = SentenceStringStrip(text)
    return result

#Replaces all the occurrences of a dictionary's name with the corresponding value
#[input: string, dictionary] [output: string]
def replace_all(text, dic):
    for i, j in iter(dic.items()):
        text = text.replace(i, j)
    return text

#Returns a list of named entities
#[input: text] [output: dictionary]
def getTheNamedEntities(text):
    Clean_Text = ' '.join([word for word in text.split() if not word[:1] == '$'])
    lstTag = st.tag(Clean_Text.split())

    result = {}
    for tag in lstTag:
        result [str(str(tag[0])).replace('.','')] = str(tag[1])
    return result
#endregion

#Classification Functions

