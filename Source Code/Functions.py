LogDir = "./Source Code/Logs/"

#region Functions
def WriteLog(text, LogFileName):
    LDA_Log_Write = open(LogDir + LogFileName, 'a')
    LDA_Log_Write.write(text)
    LDA_Log_Write.close()
    print(text)

#Removes the TextToRemove from a text
#[input: string] [output: string]
def removeTextFromText(text, TextToRemove):
    words = text.strip().split(" ")
    text = ' '.join([word for word in words if TextToRemove not in word])
    return text

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
def removeStopwords(text, StopwordsList):
    words = SentenceStringStrip(text).split(" ")
    result = ' '.join([word for word in words if word not in StopwordsList])
    return result

#Checks whether the input is in English
#[input: string] [output: boolean]
def isEnglish(text):
    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        if hasNumbers(text):
            return False
        else:
            return True

#Removes non English words
#[input: string] [output: list]
def removeNonEnglishText(text):
    result = list()
    words = SentenceStringStrip(text).split(" ")

    for i in range(0, len(words)):
        if isEnglish(words[i]) == True:
            result.append(words[i])

    return result

#Removes the list items from a text
#[input: string] [output: string]
def removeListItemsFromText(text, lst):
    words = SentenceStringStrip(text).split(" ")
    text = ' '.join([word for word in words if word not in lst])
    return text

#Removes the superfluous space characters
#[input: string] [output: string]
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
def getTheNamedEntities(text, NamedEntityRecogn):
    Clean_Text = ' '.join([word for word in text.split() if not word[:1] == '$'])
    lstTag = NamedEntityRecogn.tag(Clean_Text.split())

    result = {}
    for tag in lstTag:
        result [str(str(tag[0])).replace('.','')] = str(tag[1])
    return result

def hasNumbers(String):
    return any(char.isdigit() for char in String)

def getRetweetedFromScreenname(TweetText):
    result = None
    Tweet = TweetText
    TweetWithoutRT = Tweet[3:]

    if Tweet[:3].lower() == "rt ":
        iStart = TweetWithoutRT.find("@")
        iEnd = TweetWithoutRT.find(":")

        if ((iStart == 0) and (iEnd != -1)):
            result = TweetWithoutRT[iStart:(iStart+iEnd)]
    return result
#endregion
