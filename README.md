# Data-Mining-From-Twitter

This project can also be opened by Visual Studio with the Python Tools for VS (https://www.visualstudio.com/en-us/features/python-vs.aspx)

## Title
Refugee Crisis: A Twitter-based Event Summarisation.

## Description
This project was created in the context of the M.Sc Course Data Mining and Information Retrieval on the Web of the Informatics Department of the Aristotle University of Thessaloniki

## Categories
1. Streaming from Twitter by Streaming.py
2. Preprocessing the Data by Processing.py
3. Event Detection (LDA) by TopicDet.py
4. Affective Analysis (Machine Learning Classification) by AffAnalys.py

## Prerequisites
### Python
In order to run this programme one need already have:

* tweepy (pip install tweepy)
* pymongo (pip install pymongo)
* NumPy, Downloadable from http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy (pip install {path_to_the_file})
* SciPy, Downloadable from http://www.edna-site.org/pub/wheelhouse (pip install {path_to_the_file})
* SciKit-Learn (pip install scikit-learn)

### Other
* Your OWN twitter API Consumer Key (API Key), Consumer Secret (API Secret), Access Token, and Access Token Secret https://apps.twitter.com/app/new
* NLTK https://pypi.python.org/pypi/nltk
* Stanford NLTK http://nlp.stanford.edu/software/CRF-NER.shtml#History
  Extracted filed should go to C:\Progs\StanfordNER so that the main .jar is at C:\Progs\StanfordNER\stanford-ner.jar (alternatively, change the path on the actual code to point to whatever other directory)
* After having the NLTK, open python through a console or an IDE and do the following:
```python
  import nltk
  nltk.download()
```
From (Tab) Corpora, go to -> (Row) Stopwords, and download them

* Mongo DB: https://www.mongodb.org
  the folder C:\Data\db should be available (let alone created) at all times
  run "mongod"
* Mongoclient (is recommended, yet not a prerequisite) https://github.com/rsercano/mongoclient/releases
