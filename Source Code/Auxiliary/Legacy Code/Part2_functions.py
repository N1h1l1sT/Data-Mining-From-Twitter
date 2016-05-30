import os
import sys
import nltk
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordNERTagger
from urllib.request import urlopen

java_path = "C:/Program Files/Java/jdk1.8.0_92/bin"
os.environ['JAVAHOME'] = java_path

#Converts the input to lowercase characters
#string.lower()

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

#Returns a list of words that starts with the input pattern like "#","http" etc
#[input: list] [output: list]
def getWordsStartingWith(words, startsWith):
    result = list()
    length = len(startsWith)

    for i in range(0, len(words)):
        word = words[i].strip()

        if word[:length] == startsWith:
            result.append(words[i])
    
    return result

#Returns a list of named entities
#[input: text] [output: list]
def getTheNamedEntities(text):
    st = StanfordNERTagger('C:\Progs\stanfordNER\classifiers\english.all.3class.distsim.crf.ser.gz', 'C:\Progs\stanfordNER\stanford-ner.jar') 
    result = st.tag(text.split())

    return result

#Returns the expanded URL from links such as bit.ly
#[input: string] [output: string]
def getFullLink(URL):
    try:
        resp = urlopen(URL)
        result = resp.url
    except Exception:
        result = URL

    return result

#Removes the list items from a text
#[input: string] [output: string]
def removeListItemsFromText(text, lst):
    words = text.strip().split(" ")
    text = ' '.join([word for word in words if word not in lst])
    return text


def main():
    #-------   This is a test for the stopword removal   -------
    testString = input('Give a string for [removeStopwords] test: ')
    print("Result: " + removeStopwords(testString))
    print("")
    #-----------------------------------------------------------

    #-------   This is a test for the isEnglish function   -------
    testString = input('Give a string for [isEnglish] test: ')
    print("Result: " + str(isEnglish(testString)))
    print("")
    #-------------------------------------------------------------

    ##-------   This is a test for the removeNonEnglishText function   -------
    testString = input('Give a string for [removeNonEnglishText] test: ')
    print("Result: " + str(removeNonEnglishText(testString)))
    print("")
    #-------------------------------------------------------------------------

    ##-------   This is a test for the getTheNamedEntities function   -------
    testString = input('Give a string for [getTheNamedEntities] test: ')
    print("Result: " + str(getTheNamedEntities(testString)))
    print("")
    #------------------------------------------------------------------------

    ##-------   This is a test for the getFullLink function   -------
    testString = input('Give a string for [getFullLink] test: ')
    print("Result: " + str(getFullLink(testString)))
    print("")
    #----------------------------------------------------------------

    #-------   These are some tests for the getWordsStartingWith function   -------
    testList = ['This', '#is', 'a', '#test', 'which', 'contains', 'hashtags']
    print("Results for the hashtags")
    print("Result: " + str(getWordsStartingWith(testList, "#")))
    print("")
    
    testList = ['These', 'are', 'some', 'URLs', 'http://www.wikipedia.org', 'http://www.google.com/']
    print("Results for the URLs")
    print("Result: " + str(getWordsStartingWith(testList, "http://")))
    print("")

    testList = ['This', '@is', 'a', 'test', 'which', '@contains', 'mentions']
    print("Results for the mentions")
    print("Result: " + str(getWordsStartingWith(testList, "@")))
    print("")
    #------------------------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(int(main() or 0))
