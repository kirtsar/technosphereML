import pandas as pd
from collections import defaultdict
import os
import pymorphy2


#%%
morph = pymorphy2.MorphAnalyzer()

def getInfinitiveList(word):
    infinitiveWordTag = morph.parse(word)
    if (infinitiveWordTag[0].score < 0.8) and (len(infinitiveWordTag) > 1):
        infinitiveList = [infinitiveWordTag[0].normal_form, infinitiveWordTag[1].normal_form]        
    else:
        infinitiveList = [infinitiveWordTag[0].normal_form]
    return infinitiveList


#%%
def processWord(word):
    word = word.lower()
    skipNext = False
    if word[-1] in [',', ':', ';', ')','?','!']:
        skipNext = True
    word = word.rstrip(',.:;"\'[0123456789]?!()')
    word = word.lstrip('"()')
    return (word, skipNext)

def noWordsInLine(line):
    lineList = line.split()
    n = len(lineList)
    if n <= 1:
        return True
    word1 = processWord(lineList[0])
    word2 = processWord(lineList[1])
    if word1 == '' or word2 == '':
        return True
    return False
    

#%%
def findMostCommonKey(dic, keyPrefix, recursive):
    searchArea = dic.keys()
    lenPrefix = len(keyPrefix)
    candidates = []
    for elem in searchArea:
        if elem[:lenPrefix] == keyPrefix:
            candidates.append(elem)
            
    if (candidates == []) and not (recursive):
        resWord = findMostCommonKey(frequencyDict, keyPrefix, recursive = True)
    elif (candidates == []) and (recursive):
        return 'она'
    else:
        maxCount = -1
        for key in candidates:
            if dic[key] > maxCount:
                maxKey = key
                maxCount = dic[key]
        resWord = maxKey

    return resWord
        
#%%
# reading and processing train data 

df = pd.read_csv('train.csv')
df = df.drop(['Id'], axis='columns')

trainData = dict()
frequencyDict = defaultdict(int)


for collocation in df['Prediction']:
    word1, word2 = collocation.split()
    if word1 not in trainData.keys():
        trainData[word1] = defaultdict(int)
        trainData[word1][word2] = 1
    else:
        trainData[word1][word2] += 1
    frequencyDict[word1] += 1
    frequencyDict[word2] += 1



#%%
# reading and processing corpus

corpus = open('2grams-3.txt', 'r')
for line in corpus:
    lineList = line.split()
    if (len(lineList[1]) < 3) or (len(lineList[2]) < 3):
        continue
    else:
        word1 = lineList[1]
        word2 = lineList[2]
        if word1 not in trainData.keys():
            trainData[word1] = defaultdict(int)
            trainData[word1][word2] += (int(lineList[0])) // 65 + 3
        else:
            trainData[word1][word2] += (int(lineList[0])) // 65 + 3
        frequencyDict[word1] += (int(lineList[0])) // 65 + 2
        frequencyDict[word2] += (int(lineList[0])) // 65 + 2
    

#%%
# reading and processing more train data
fileList = os.listdir(path="literature")
for fileName in fileList:
    try:
        inputFile = open('literature/' + fileName, 'r')
        for line in inputFile:
            if (line == '\n') or noWordsInLine(line):
                continue
            else:
                lineList = line.split()
                n = len(lineList)
                for i in range(n - 1):
                    word1 = lineList[i]
                    word2 = lineList[i + 1]
                    (word1, skipNext) = processWord(word1)
                    if skipNext:
                        continue
                    (word2, skipPair) = processWord(word2)
                    if (len(word1) < 3) or (len(word2) < 3) :
                        continue
                    else:
                        if word1 not in trainData.keys():
                            trainData[word1] = defaultdict(int)
                            trainData[word1][word2] = 1
                        else:
                            trainData[word1][word2] += 1
                        frequencyDict[word1] += 1
                        frequencyDict[word2] += 1
    except UnicodeDecodeError:
        print(fileName)
    
    inputFile.close()


#%%
# processing test data


df2 = pd.read_csv('test.csv')

outputFile = open('res.csv', 'w')  
outputFile.write('Id,Prediction\n')
uniqueWord = 0

for i in range(len(df2)):
    collocation = df2['Sample'][i]
    keyWord, completeWord = collocation.split()
    if keyWord in trainData.keys():
        res = findMostCommonKey(trainData[keyWord], completeWord, recursive = False)
        resPair = keyWord + ' ' + res
    else:
        resPair = keyWord + ' ' + 'она'
        uniqueWord += 1
    outputFile.write('%s,%s\n' % (df2['Id'][i], resPair))

outputFile.close()
print('numb of unique:', uniqueWord)

