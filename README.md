# Data-Mining-From-Twitter
Written in Python 3 format.
This project can also be opened by Visual Studio with the Python Tools for VS (https://www.visualstudio.com/en-us/features/python-vs.aspx)

## Title
Refugee Crisis: A Twitter-based Event Summarisation.

## Description
This project was created in the context of the M.Sc Course Data Mining and Information Retrieval on the Web of the Informatics Department of the Aristotle University of Thessaloniki

## Categories
This project is divided into 3 Main Categories
  1) Streaming from Twitter by Tweets_Streaming.py
  2) Preprocessing of Data by Tweets_Processing.py 
  3) Event Summarisation by Topic_Detection.py

## Prerequisites

### Python
In order to run this programme one need already have:
twitter-text-python (pip install twitter-text-python)
tweepy (pip install tweepy)
pymongo (pip install pymongo)
py-getch (pip install py-getch) - Not really needed - safe to just comment out the getch lines if one can't install this prerequisite

### Other
Your OWN twitter API Consumer Key (API Key), Consumer Secret (API Secret), Access Token, and Access Token Secret https://apps.twitter.com/app/new
NLTK https://pypi.python.org/pypi/nltk
Stanford NLTK http://nlp.stanford.edu/software/stanford-ner-2015-12-09.zip
  Extracted filed should go to C:\Progs\StanfordNER so that the main .jar is at C:\Progs\StanfordNER\stanford-ner.jar (alternatively, change the path on the actual code to point to whatever other directory)
After having the NLTK, open python through a console or an IDE and do the following:
```python
  import nltk
  nltk.download()
  (Tab) Corpora -> (Row) Stopwords
```
Mongo DB: https://www.mongodb.org
  the folder C:\Data\db should be available (let alone created) at all times
Mongoclient (is recommended, yet not a prerequisite) https://github.com/rsercano/mongoclient/releases/tag/1.0.0
