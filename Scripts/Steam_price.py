import requests
import csv

i = 3

with open("../Data/games.csv", newline='', encoding='utf-8') as f:
    leitor = csv.DictReader(f)
    for linha in leitor:
        linha["price_overview"] = "R$ 16,99"
        print(list(linha.values()))
        if i > 0: i=i-1
        else: break

"""

## "http://store.steampowered.com/api/appdetails?appids=[game_id]]&cc=BR&filters=price_overview"
url = "http://store.steampowered.com/api/appdetails?appids=20&cc=BR"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
              ##20 vai mudar dinamicamente
    print(data)
    ##print(data["20"]["data"]["price_overview"]["final_formatted"])
else:
    print("erro")

"""