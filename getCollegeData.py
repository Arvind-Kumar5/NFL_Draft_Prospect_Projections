import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

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

dfs = []
rateLimit = False
for year in range(2010, 2022):
    
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

if rateLimit == False:
    college_stats_df = pd.concat(dfs)
    # changeTrainColNames(college_stats_df)
    # removeStarFromName(college_stats_df)
    print(college_stats_df)
    print(len(college_stats_df))