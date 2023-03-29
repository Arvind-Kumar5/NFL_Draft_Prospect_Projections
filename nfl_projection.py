import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

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

def printCollectingData():
    pass

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
            #print("request gord. ve are not blocked")
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

# for training 2008 to 2017
trainRateLimit, trainDfsProbowl = scrapeSite(probowlUrl, probowlHtmlFile, probowlId, 2008, 2017)
# for validation 2018 to 2019
#valRateLimit, valDfsProbowl = scrapeSite(probowlUrl, probowlHtmlFile, probowlId, 2018, 2019)
# for testing 2020 to 2021
#testRateLimit, testDfsProbowl =  scrapeSite(probowlUrl, probowlHtmlFile, probowlId, 2020, 2021)

trainProbowl = getProbowl(trainRateLimit, trainDfsProbowl)
#valProbowl= getProbowl(valRateLimit, valDfsProbowl)
#testProbowl = getProbowl(testRateLimit, testDfsProbowl)

print("Pro-Bowlers: \n")
print(trainProbowl)
print(len(trainProbowl))


# for training 2008 to 2017
trainRateLimit, trainDfsStats = scrapeSite(collegeStatsUrl, collegeStatsHtmlFile, collegeStatsId, 2008, 2017) 
# for validation 2018 to 2019
#valRateLimit, valDfsStats = scrapeSite(collegeStatsUrl, collegeStatsHtmlFile, collegeStatsId, 2018, 2019) 
# for testing 2020 to 2021
#testRateLimit, testDfsStats = scrapeSite(collegeStatsUrl, collegeStatsHtmlFile, collegeStatsId, 2020, 2021) 

trainDf = getCollegeStatsDf(trainRateLimit, trainDfsStats)
#valDf = getCollegeStatsDf(valRateLimit, valDfsStats)
#testDf = getCollegeStatsDf(testRateLimit, testDfsStats)


# for training combine 2009 to 2018
trainLimit, trainDfsCombine = scrapeSite(combineUrl,combineHtmlFile,combineId,2009,2018)
# for validation combine 2019 to 2020
## TODO
# for testing combine 2021 to 2022
## TODO
combineTrainDf = getCombineDf(trainLimit, trainDfsCombine)

# add score column with everything preset to 0
trainDf['Score'] = None
score = 0

for i in tqdm(range(10)):

    # fill score column
    for x, row in  trainDf.iterrows():
        if row['Player'] == 'Player':
            continue
        try:
            score = ((((int(row["Passing_Cmp"])/int(row["Passing_Att"]))*100)) + (int(row["Passing_Yds"])/25) + (int(row["Passing_TD"])*4) + (int(row["Rushing_Yds"])/10) + (float(row["Passing_Rate"])/10.0) + (int(row["Rushing_TD"])*6)) - (int(row["Passing_Int"])*2)
            row['Score'] = score

        except ValueError:
            print("error on this row: \n", row)
            break

    time.sleep(0.5)

duplicateDf = trainDf[trainDf.Player.duplicated(keep=False)].sort_values("Player")

duplicates = {}

for x, row in duplicateDf.iterrows():

    if row['Player'] == 'Player':
        continue

    elif row['Player'] not in duplicates:
        duplicates[row['Player']] = dict(row)

    else:

        if row['Score'] > duplicates[row['Player']]['Score']:

            duplicates[row['Player']] = dict(row)

print(duplicates["Derek Carr"])
bestScoreDuplicates = []
for player in duplicates:
    trainDf.drop(trainDf.loc[trainDf['Player']==player].index, inplace=True)
    bestScoreDuplicates.append(pd.DataFrame([duplicates[player]]))
    # trainDf = trainDf.append(duplicates[player], ignore_index = True)

trainDf = pd.concat(bestScoreDuplicates, ignore_index = True)
print("No duplicates \n")
print(trainDf)

time.sleep(60)