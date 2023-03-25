import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

dfs = []
for year in range(2010, 2022):
    
    url = "https://www.pro-football-reference.com/years/{}/probowl.htm"
    url_year = url.format(year)
    data = requests.get(url_year)

    with open("proBowl{}.html".format(year), "w+") as f:
        f.write(data.text)
    with open("proBowl{}.html".format(year)) as f:

        html_page = f.read()

    soup = BeautifulSoup(html_page, "html.parser")

    pro_bowlers = soup.find(id="pro_bowl")
    print(pro_bowlers)

    pro_bowlers = pd.read_html(str(pro_bowlers))[0]

    dfs.append(pro_bowlers)

    os.remove("proBowl{}.html".format(year))

pro_bowl = pd.concat(dfs)
pro_bowl.drop(pro_bowl.loc[pro_bowl['Pos']!="QB"].index, inplace=True)
print(pro_bowl)