import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

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

def getCollegeStats(startYear, endYear):
    dfs = []
    rateLimit = False
    for year in range(startYear, endYear+1):
        
        url = "https://www.sports-reference.com/cfb/years/{}-passing.html"
        url_year = url.format(year)
        data = requests.get(url_year)

        with open("collegeStats{}.html".format(year), "w+") as f:
            f.write(data.text)
        with open("collegeStats{}.html".format(year)) as f:
            html_page = f.read()

        soup = BeautifulSoup(html_page, "html.parser")

        try:
            college_stats = soup.find(id="div_passing")

            college_stats = pd.read_html(str(college_stats))[0]

            dfs.append(college_stats)

        except ValueError:
            print("Rate Limit: Too many requests ve are blocked")
            rateLimit = True

        os.remove("collegeStats{}.html".format(year))

    return rateLimit, dfs

def toCsv(rateLimit, dfs, csvFileName):
    if rateLimit == False:
        df = pd.concat(dfs)
        df = df.reset_index(drop=True) # needed so that each row has unique index
        changeTrainColNames(df)
        removeStarFromName(df)
        print(df)
        print(len(df))
        print()
        df.to_csv(csvFileName) 


# for training 2010 to 2018
trainRateLimit, trainDfs = getCollegeStats(2010, 2018)

# for validation 2019 to 2020
valRateLimit, valDfs = getCollegeStats(2019, 2020)

# for testing 2021 to 2022
testRateLimit, testDfs = getCollegeStats(2021, 2022)

toCsv(trainRateLimit, trainDfs, 'TrainData/TrainCollegeStats.csv')
toCsv(valRateLimit, valDfs, 'ValidationData/ValCollegeStats.csv')
toCsv(testRateLimit, testDfs, 'TestData/TestCollegeStats.csv')
    