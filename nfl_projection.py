import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import math
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

    #combineParticipantsDf = pd.DataFrame()
    #allParticipants = []

    # for x, row in trainDf.iterrows():

    #     if row['Player'] in combineParticipants:
    #         allParticipants.append(pd.DataFrame([dict(row)]))

    #combineParticipantsDf = pd.concat(allParticipants, ignore_index=True)

    #Add combine columns
    currList = list(trainDf)

    for colName in list(combineTrainDf.columns):
        
        if colName not in currList:
            #combineParticipantsDf[colName] = None

            #If we want all players use this and comment that ^
            trainDf[colName] = None

    for x, row in trainDf.iterrows():
        #Add Ht from combine participants dict to dataframe
        #print("Adding rows: ", row)

        try:
            trainDf.loc[x, ['Pos']] = [combineParticipants[row['Player']]['Pos']]
            trainDf.loc[x, ['Ht']] = [combineParticipants[row['Player']]['Ht']]
            trainDf.loc[x, ['Wt']] = [combineParticipants[row['Player']]['Wt']]
            trainDf.loc[x, ['40yd']] = [combineParticipants[row['Player']]['40yd']]
            trainDf.loc[x, ['Vertical']] = [combineParticipants[row['Player']]['Vertical']]
            trainDf.loc[x, ['Bench']] = [combineParticipants[row['Player']]['Bench']]
            trainDf.loc[x, ['Broad Jump']] = [combineParticipants[row['Player']]['Broad Jump']]
            trainDf.loc[x, ['3Cone']] = [combineParticipants[row['Player']]['3Cone']]
            trainDf.loc[x, ['Shuttle']] = [combineParticipants[row['Player']]['Shuttle']]

        except:

            trainDf.loc[x, ['Pos']] = float('nan')
            trainDf.loc[x, ['Ht']] = float('nan')
            trainDf.loc[x, ['Wt']] = float('nan')
            trainDf.loc[x, ['40yd']] = float('nan')
            trainDf.loc[x, ['Vertical']] = float('nan')
            trainDf.loc[x, ['Bench']] = float('nan')
            trainDf.loc[x, ['Broad Jump']] = float('nan')
            trainDf.loc[x, ['3Cone']] = float('nan')
            trainDf.loc[x, ['Shuttle']] = float('nan')

    return trainDf

def getOnlyDraftedQbs(trainDf):
    indiciesToDrop = {}
    for index,row in trainDf.iterrows():
        if row['Player'] not in draftedQbs.keys():
            indiciesToDrop[index] = index

    trainDf.drop(index=indiciesToDrop.values(), inplace=True)
    trainDf = trainDf.reset_index()
    trainDf.drop(columns=['index'], inplace=True) 

    return trainDf




print("\nVe are never getting blocked again")

# read from the csv files and create a df
trainDf = pd.read_csv('TrainData/trainDf.csv') #, index_col=0) -> ignore for now
combineTrainDf = pd.read_csv('TrainData/combineTrainDf.csv') #, index_col=0) -> ignore for now

print()
# needed for some formatting issues when reading csv
trainDf.drop(trainDf.columns[trainDf.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
print("----------- trainDf:")
print(trainDf)
print(trainDf['Player'].values)
x = "Matthew Stafford" in trainDf['Player'].values
print("Matthew Stafford in? ", x)
print()

# needed for some formatting issues when reading csv
combineTrainDf.drop(combineTrainDf.columns[combineTrainDf.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
print("----------- combineTrainDf:")
print(combineTrainDf)
x = "Matthew Stafford" in trainDf['Player'].values
print("Matthew Stafford in? ", x)
print()
print()

probowlers = {}
with open('probowlers.pkl', 'rb') as fp:
    probowlers = pickle.load(fp)

if not probowlers:
    print("ve are in a bit of trouble")

# add score column with everything preset to None
trainDf['Score'] = None

# calculate the score for each row and add it to the row
fillDfWithScores(trainDf)

# get the duplicate players (players with multiple college season stats)
# duplicateDf = trainDf[trainDf.Player.duplicated(keep=False)].sort_values("Player")
# duplicates = getDuplicates(duplicateDf)
duplicates = getDuplicates(trainDf)
print("----------- len(duplicates): ", len(duplicates))

# x = "Matthew Stafford" in duplicateDf['Player'].values
# print("Matthew Stafford in duplicateDf? ", x)

x = "Matthew Stafford" in duplicates.keys()
print("Matthew Stafford in duplicates? ", x)
print()

# create trainDf with no duplicates 
trainDf = updateDfNoDuplicates(trainDf, duplicates)
print("----------- No duplicates train df")
print(trainDf)
x = "Matthew Stafford" in trainDf['Player'].values
print("Matthew Stafford in? ", x)
print()
print()

# update traindf with combine data and get back players who attended the combine 
#TODO: May need to figure out whether we want to only use players who attended combine or not
combineParticipantsDf = addCombineData(trainDf, combineTrainDf)
trainDf = combineParticipantsDf
print("----------- trainDf combined with combineTraindf")
print(trainDf)
x = "Matthew Stafford" in trainDf['Player'].values
print("Matthew Stafford in? ", x)
print()
print()

draftedQbs = {}
with open('draftedQbs.pkl', 'rb') as fp:
    draftedQbs = pickle.load(fp)

if not draftedQbs:
    print("ve are in a bit of trouble")

# print("----------- drafted Qbs")
# print("len(draftedQbs): ", len(draftedQbs))
# print()

# allPlayersBefore = trainDf['Player'].values

# counter = 1
# for player in draftedQbs.keys():
#     if player not in allPlayersBefore:
#         print(str(counter) + ") " + str(player))
#         counter += 1

trainDf = getOnlyDraftedQbs(trainDf)
print("----------- trainDf")
print(trainDf)
x = "Matthew Stafford" in trainDf['Player'].values
print("Matthew Stafford in? ", x)
print()


    

    




