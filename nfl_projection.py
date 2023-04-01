import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import pickle

import time
import sys

def getScore(row):
    return ((((int(row["Passing_Cmp"])/int(row["Passing_Att"]))*100)) 
            + (int(row["Passing_Yds"])/25) + (int(row["Passing_TD"])*4) 
            + (int(row["Rushing_Yds"])/10) + (float(row["Passing_Rate"])/10.0) 
            + (int(row["Rushing_TD"])*6)) - (int(row["Passing_Int"])*2)

def fillDfWithScores(trainDf):
    for x, row in  tqdm(trainDf.iterrows(), total=trainDf.shape[0], desc="Calculating scores: "):
        if row['Player'] == 'Player':
            continue
        try:
            row['Score'] = getScore(row)

        except ValueError:
            print("error on this row: \n", row)
            break

        #time.sleep(0.0000001)

def getDuplicates(duplicateDf):
    duplicates = {}

    for x, row in tqdm(duplicateDf.iterrows(), total=duplicateDf.shape[0], desc="Finding duplicates: "):
        if row['Player'] == 'Player':
            continue
        elif row['Player'] not in duplicates:
            duplicates[row['Player']] = dict(row)
        else:
            if row['Score'] > duplicates[row['Player']]['Score']:
                duplicates[row['Player']] = dict(row)

        #time.sleep(0.0000001)
    
    return duplicates

# update df such that only duplicates with the best scores are used 
def updateDfNoDuplicates(trainDf, duplicates):
    bestScoreDuplicates = []

    for player in duplicates:
        trainDf.drop(trainDf.loc[trainDf['Player']==player].index, inplace=True)
        bestScoreDuplicates.append(pd.DataFrame([duplicates[player]]))

    trainDf = pd.concat(bestScoreDuplicates, ignore_index = True)

    return trainDf

def addCombineData(trainDf, combineTrainDf):

    eligiblePlayers = len(dict(combineTrainDf)['Player'])
    combineParticipants = {}
    for i in range(eligiblePlayers):

        combineParticipants[dict(combineTrainDf)['Player'][i]] = dict(combineTrainDf.loc[i])

    combineParticipantsDf = pd.DataFrame()
    allParticipants = []

    for x, row in trainDf.iterrows():

        if row['Player'] in combineParticipants:
            allParticipants.append(pd.DataFrame([dict(row)]))

    combineParticipantsDf = pd.concat(allParticipants, ignore_index=True)

    #Add combine columns
    currList = list(trainDf)

    for colName in list(combineTrainDf.columns):
        
        if colName not in currList:
            combineParticipantsDf[colName] = None

    for x, row in combineParticipantsDf.iterrows():
        #Add Ht from combine participants dict to dataframe
        #print("Adding rows: ", row)
        combineParticipantsDf.loc[x, ['Pos']] = [combineParticipants[row['Player']]['Pos']]
        combineParticipantsDf.loc[x, ['Ht']] = [combineParticipants[row['Player']]['Ht']]
        combineParticipantsDf.loc[x, ['Wt']] = [combineParticipants[row['Player']]['Wt']]
        combineParticipantsDf.loc[x, ['40yd']] = [combineParticipants[row['Player']]['40yd']]
        combineParticipantsDf.loc[x, ['Vertical']] = [combineParticipants[row['Player']]['Vertical']]
        combineParticipantsDf.loc[x, ['Bench']] = [combineParticipants[row['Player']]['Bench']]
        combineParticipantsDf.loc[x, ['Broad Jump']] = [combineParticipants[row['Player']]['Broad Jump']]
        combineParticipantsDf.loc[x, ['3Cone']] = [combineParticipants[row['Player']]['3Cone']]
        combineParticipantsDf.loc[x, ['Shuttle']] = [combineParticipants[row['Player']]['Shuttle']]

    return combineParticipantsDf





print("\nVe are never getting blocked again")

# read from the csv files and create a df
trainDf = pd.read_csv('TrainData/trainDf.csv') #, index_col=0) -> ignore for now
combineTrainDf = pd.read_csv('TrainData/combineTrainDf.csv') #, index_col=0) -> ignore for now

print()
# needed for some formatting issues when reading csv
trainDf.drop(trainDf.columns[trainDf.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
print("----------- trainDf:")
print(trainDf)
print()

# needed for some formatting issues when reading csv
combineTrainDf.drop(combineTrainDf.columns[combineTrainDf.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
print("----------- combineTrainDf:")
print(combineTrainDf)
print()

probowlers = {}
with open('probowlers.pkl', 'rb') as fp:
    probowlers = pickle.load(fp)

if not probowlers:
    print("ve are in a bit of trouble")
print("----------- probowlers: ", probowlers)
print("----------- probowlers len: ", len(probowlers))
print()

# add score column with everything preset to None
trainDf['Score'] = None

# calculate the score for each row and add it to the row
fillDfWithScores(trainDf)

# get the duplicate players (players with multiple college season stats)
duplicateDf = trainDf[trainDf.Player.duplicated(keep=False)].sort_values("Player")
duplicates = getDuplicates(duplicateDf)
print("----------- duplicates[\"Derek Carr\"]: ")
print(duplicates["Derek Carr"])
print()

# create trainDf with no duplicates 
trainDf = updateDfNoDuplicates(trainDf, duplicates)
print("----------- No duplicates train df")
print(trainDf)
print()

# update traindf with combine data and get back players who attended the combine 
#TODO: May need to figure out whether we want to only use players who attended combine or not

combineParticipantsDf = addCombineData(trainDf, combineTrainDf)
print("----------- CombineDF df")
print(combineParticipantsDf)
print()


    

    




