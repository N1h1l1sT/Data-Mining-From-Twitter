import pdb
from random import randint

tweetsWithSent = dict()

sentiments = ['anger', 'anxiety', 'calm', 'disgust', 'enthusiasm', 'fear', 'interested', 'joy', 'nervous', 'neutral', 'rejection', 'sadness', 'shame', 'surprise', 'unknown']



stringList = list()	

countTweets = 0
with open("AnotationsNorm.txt") as anoFile:
	for line in anoFile:
		countTweets += 1

		textList = line.split('\t')
		textList.pop(0)

		sentiment = textList[-1][:-1]

		text = ''.join(textList)

		stringList.append(line)
		#tweetsWithSent[sentiment].append(textList)

		
normFile = open("Normalized.txt", "w")

while(len(stringList) != 0):
	randNumber = randint(0, len(stringList) - 1)
	normFile.write(stringList.pop(randNumber))

normFile.close()	
	



		


