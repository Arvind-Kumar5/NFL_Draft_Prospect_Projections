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
    for i in tqdm(range(10)):
        # fill score column
        for x, row in  trainDf.iterrows():
            if row['Player'] == 'Player':
                continue
            try:
                row['Score'] = getScore(row)

            except ValueError:
                print("error on this row: \n", row)
                break

        time.sleep(0.5)

def getDuplicates(duplicateDf):
    duplicates = {}

    for x, row in duplicateDf.iterrows():
        if row['Player'] == 'Player':
            continue
        elif row['Player'] not in duplicates:
            duplicates[row['Player']] = dict(row)
        else:
            if row['Score'] > duplicates[row['Player']]['Score']:
                duplicates[row['Player']] = dict(row)
    
    return duplicates

# update df such that only duplicates with the best scores are used 
def updateDfNoDuplicates(trainDf, duplicates):
    bestScoreDuplicates = []

    for player in duplicates:
        trainDf.drop(trainDf.loc[trainDf['Player']==player].index, inplace=True)
        bestScoreDuplicates.append(pd.DataFrame([duplicates[player]]))

    trainDf = pd.concat(bestScoreDuplicates, ignore_index = True)

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