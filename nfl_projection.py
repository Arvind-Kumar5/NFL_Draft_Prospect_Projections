#MAIN FILE
import csv
import pandas as pd
import os
import sys

# need new column names to differentiate passing and rushing yards
def changeTrainColNames(df):
    cols = []
    for colName in df.iloc[0,:]:
        cols.append(colName)

    passingStatsIndicies = range(5,14)
    rushingStatsIndicies = range(14,18)

    newCols = []
    for i in range(len(cols)):
        if i in passingStatsIndicies:
            newCols.append("Passing_"+str(cols[i]))
        elif i in rushingStatsIndicies:
            newCols.append("Rushing_"+str(cols[i])) 
        else:
            newCols.append(cols[i])

    df.columns = newCols
    return newCols

# some names have "*" next to them which needs to be removed
def removeStarFromName(df):
    index = 0
    for name in df['Player']:
        if "*" in name:
            newName = name.split("*")[0]
            df['Player'].values[index] = newName
        index += 1

def getTrainData(path):
    dirs = os.listdir(path)
    dfs = []
    print("dirs: ", dirs)
    for file in dirs:
        if ".csv" in str(file):
            try:
                df = pd.read_csv(path+"/"+file) # read specfic csv file
                df = df.drop("-additional", axis='columns') # drop unused column
                changeTrainColNames(df) # specfic col names needed such as "Passing_Yds" and "Rushing_yds"
                df = df.drop(0) # need to drop the column header row since we made new column header
                removeStarFromName(df) # some names have a "*" next to them, need to remove the "*"

                # drop unused column
                df = df.drop("School", axis='columns') 
                df = df.drop("Conf", axis='columns')
                dfs.append(df)
            except:
                print(str(file) + " : CSV FILE ERROR")
                continue
           
    bigDf = pd.concat(dfs)
    return bigDf

# 2010 data is 102 rows × 16 columns

df = getTrainData("train_data")
print(len(df))