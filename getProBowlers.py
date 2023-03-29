import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re

def getProBowlers(startYear, endYear):
    dfs = []
    rateLimit = False
    for year in range(startYear, endYear+1):
        
        url = "https://www.pro-football-reference.com/years/{}/probowl.htm"
        url_year = url.format(year)
        data = requests.get(url_year)

        with open("proBowl{}.html".format(year), "w+") as f:
            f.write(data.text)
        with open("proBowl{}.html".format(year)) as f:

            html_page = f.read()

        soup = BeautifulSoup(html_page, "html.parser")

        try:
            pro_bowlers = soup.find(id="pro_bowl")

            pro_bowlers = pd.read_html(str(pro_bowlers))[0]

            dfs.append(pro_bowlers)

        except ValueError:
            print("Rate Limit: Too many requests ve are blocked")
            rateLimit = True

        os.remove("proBowl{}.html".format(year))

    return rateLimit, dfs

def toCsv(rateLimit, dfs, csvFileName):
    if rateLimit == False:
        df = pd.concat(dfs)
        df = df.reset_index(drop=True) # needed so that each row has unique index
        #Clean data names and add to dict
        regex = re.compile('[^a-zA-Z\s]')
        playerNamesExctract = df.Player.tolist()
        newNames = []
        for name in playerNamesExctract:
            newNames.append(regex.sub('', name))

        df.Player = newNames 

        print(df)
        print(len(df))
        print()

        df.to_csv(csvFileName) 

# for training 2010 to 2018
trainRateLimit, trainDfs = getProBowlers(2010, 2018)

# for validation 2019 to 2020
valRateLimit, valDfs = getProBowlers(2019, 2020)

# for testing 2021 to 2022
testRateLimit, testDfs = getProBowlers(2021, 2022)

toCsv(trainRateLimit, trainDfs, 'TrainData/TrainProbowl.csv')
toCsv(valRateLimit, valDfs, 'ValidationData/ValProbowl.csv')
toCsv(testRateLimit, testDfs, 'TestData/TestProbowl.csv')