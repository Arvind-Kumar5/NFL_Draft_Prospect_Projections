import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import pickle

import time
import sys

probowlUrl = "https://www.pro-football-reference.com/years/{}/probowl.htm"
probowlHtmlFile = "proBowl{}.html"
probowlId = "pro_bowl" 

collegeStatsUrl = "https://www.sports-reference.com/cfb/years/{}-passing.html"
collegeStatsHtmlFile = "collegeStats{}.html"
collegeStatsId = "div_passing"

combineUrl = "https://www.pro-football-reference.com/draft/{}-combine.htm"
combineHtmlFile = "combineStats{}.html"
combineId = "div_combine" 

def dots(i):
    return "."*i

def scrapeSite(url, htmlFileName, idName, startYear, endYear):
    dfs = []
    rateLimit = False
    i = 1
    for year in range(startYear, endYear+1):
        url_year = url.format(year)
        data = requests.get(url_year)

        with open(htmlFileName.format(year), "w+") as f:
            f.write(data.text)
        with open(htmlFileName.format(year)) as f:

            html_page = f.read()

        soup = BeautifulSoup(html_page, "html.parser")

        try:
            df = soup.find(id=idName)
            df = pd.read_html(str(df))[0]
            dfs.append(df)

            if i == 4:
                print("")
                i = 1
            print("Collecting Data Vate (ve are not blocked)", dots(i), end='\r')
            i = i + 1

        except ValueError:
            print("Rate Limit: Too many requests ve are blocked")
            rateLimit = True

        os.remove(htmlFileName.format(year))

    return rateLimit, dfs 

def getProbowl(rateLimit, dfs):
    if rateLimit == False:
        #append all pro bowl years together into dataframe
        df = pd.concat(dfs)

        df = df.reset_index(drop=True) # needed so that each row has unique index

        # Drop all other positions except qb
        df.drop(df.loc[df['Pos']!="QB"].index, inplace=True)
        # print("only qb df: ", df)

        #Clean data names and add to dict
        regex = re.compile('[^a-zA-Z\s]')
        playerNamesExctract = df.Player.tolist()
        playerNames = {}
        for name in playerNamesExctract:
            playerNames[regex.sub('', name)] = True

        return playerNames
    return None

# need new column names to differentiate passing and rushing yards
def changeTrainColNames(college_stats_df):
    new_cols = []

    for i in range(len(college_stats_df.columns.values)):
        col = college_stats_df.columns.values[i]
        if i in range(0,5):
            new_cols.append(col[len(col)-1])
        else:
            new_cols.append('_'.join(col))

    college_stats_df.columns = new_cols

# some names have "*" next to them which needs to be removed
def removeStarFromName(df):
    index = 0
    for name in df['Player']:
        if "*" in name:
            newName = name.split("*")[0]
            df['Player'].values[index] = newName
        index += 1

def getCollegeStatsDf(rateLimit, dfs):
    if rateLimit == False:
        df = pd.concat(dfs)
        df = df.reset_index(drop=True) # needed so that each row has unique index
        changeTrainColNames(df)
        removeStarFromName(df)
        return df
    return None

def getCombineDf(rateLimit, dfs):
    if rateLimit == False:
        df = pd.concat(dfs)
        df = df.reset_index(drop=True) # needed so that each row has unique index
        df.drop(index=df.loc[df['Pos']!='QB'].index, inplace=True)
        df = df.drop(columns=['School', 'College', 'Drafted (tm/rnd/yr)'])
        return df
    return None

# for training 2008 to 2022
rateLimit, probowlDfs = scrapeSite(probowlUrl, probowlHtmlFile, probowlId, 1980, 2022)
probowl = getProbowl(rateLimit, probowlDfs)

print("\n")
print("Pro-Bowlers:")
print(probowl)
print(len(probowl))

with open('probowlers.pkl', 'wb') as fp:
    pickle.dump(probowl, fp)
    print('probowl dictionary saved successfully to file probowlers.pkl')
print()

# for training 2008 to 2017
trainRateLimit, trainDfsStats = scrapeSite(collegeStatsUrl, collegeStatsHtmlFile, collegeStatsId, 1980, 2019) 
# for testing 2020 to 2021
testRateLimit, testDfsStats = scrapeSite(collegeStatsUrl, collegeStatsHtmlFile, collegeStatsId, 2020, 2021) 

trainDf = getCollegeStatsDf(trainRateLimit, trainDfsStats)
testDf = getCollegeStatsDf(testRateLimit, testDfsStats)

# for training combine 2009 to 2018
trainLimit, trainDfsCombine = scrapeSite(combineUrl,combineHtmlFile,combineId,1981,2020)
# for testing combine 2021 to 2022
testLimit, testDfsCombine = scrapeSite(combineUrl,combineHtmlFile,combineId,2021,2022)

combineTrainDf = getCombineDf(trainLimit, trainDfsCombine)
combineTestDf = getCombineDf(trainLimit, trainDfsCombine)

trainDf.to_csv('TrainData/trainDf.csv')
testDf.to_csv('TestData/testDf.csv')

combineTrainDf.to_csv('TrainData/combineTrainDf.csv')
combineTestDf.to_csv('TestData/combineTestDf.csv')
