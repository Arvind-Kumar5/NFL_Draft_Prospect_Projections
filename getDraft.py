import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import pickle

import time
import sys

draftUrl = "https://www.pro-football-reference.com/years/{}/draft.htm"
draftHtmlFile = "draft{}.html"
draftId = "drafts"

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

def getDraftDf(rateLimit, dfs):
    if rateLimit == False:
        df = pd.concat(dfs)
        df = df.reset_index(drop=True) # needed so that each row has unique index
        return df
    return None


choose = input("Enter 1 for scraping\nEnter 2 for making drafted QB dictionary:\n")
if choose == '1':
    # drafted QBs from 2009 to 2021
    draftRateLimit, draftDfs = scrapeSite(draftUrl, draftHtmlFile, draftId, 2009, 2022) 
    draftDf = getDraftDf(draftRateLimit, draftDfs)
    print("----------- draftDf")
    print(draftDf)
    draftDf.to_csv('draftedPlayers.csv')
if choose == '2':
    draftDf = pd.read_csv('draftedPLayers.csv')
    # draftDf.drop(draftDf.columns[draftDf.columns.str.contains('unnamed',case = False)], axis = 1, inplace = True)
    draftDf.drop(index=draftDf.loc[draftDf['Pos']!='QB'].index, inplace=True)

    print("------------ draftDf")
    print(draftDf)

    regex = re.compile('[^a-zA-Z\s]')
    playerNamesExctract = draftDf.Player.tolist()
    playerNames = {}

    for name in playerNamesExctract:
        playerNames[regex.sub('', name)] = True

    print("------- players")
    print(playerNames)
    print("len(playerNames): ", len(playerNames))

    with open('draftedQbs.pkl', 'wb') as fp:
        pickle.dump(playerNames, fp)
        print('QB dictionary saved successfully to file draftedQbs.pkl')


