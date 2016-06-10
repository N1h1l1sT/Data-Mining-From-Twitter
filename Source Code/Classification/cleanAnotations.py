import pdb

sentDict = dict()

emoFile = open('emoticonsIn.txt', 'a')
with open('Anotations.txt') as data:
	for line in data:
		#linesplit = line.split('\t')
		#linesplit.pop(0)
		line = line.replace(':)', ' happy smile ')
		line = line.replace('(:', ' happy smile ')
		line = line.replace(':-)', ' happy smile ')
		line = line.replace('(-:', ' happy smile ')

		line = line.replace(':D', ' happy excited ')
		line = line.replace(':-D', ' happy excited ')	

		line = line.replace(':(', ' sad ')
		line = line.replace('):', ' sad ')
		line = line.replace(')-:', ' sad ')
		line = line.replace(':-(', ' sad ')

		line = line.replace(':\'(', ' cry sad ')
		line = line.replace(')\':', ' cry sad ')	

		line = line.replace(' XD ', ' laugh happy ')
		line = line.replace(' xD ', ' laugh happy ')

		line = line.replace(':p', ' playful happy ')
		line = line.replace(':-p', ' playful happy ')	

		line = line.replace(';)', ' wink smile ')
		line = line.replace('(;', ' wink smile ')
		line = line.replace(';-)', ' wink smile ')	
		line = line.replace('(-;', ' wink smile ')	

		line = line.replace(' <3 ', ' love ')	

		emoFile.write(line)
		


	emoFile.close()

