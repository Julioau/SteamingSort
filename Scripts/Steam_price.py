import requests
import csv

with open("../Data/games.csv", "r", newline='', encoding='utf-8') as old_file, \
    open("../Data/new_games.csv", "w", newline='', encoding='utf-8') as new_file:

    leitor = csv.DictReader(old_file)
    campos = leitor.fieldnames
    escritor = csv.DictWriter(new_file, fieldnames=campos)
    escritor.writeheader()
    for linha in leitor:
        url = "http://store.steampowered.com/api/appdetails?appids="+linha["app_id"]+"&cc=BR&filters=price_overview"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()##[linha["app_id"]]["data"]["price_overview"]["final_formatted"]
            try:
                data = data[linha["app_id"]]["data"]["price_overview"]["final_formatted"].replace("R$ ","")
            except:
                data = "\\N"
        else:
            data = "\\N"
        linha["price_overview"] = data
        escritor.writerow(linha)