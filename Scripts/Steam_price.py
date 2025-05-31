import requests
import csv
import time

with open("Data/new_games.csv", "r", newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    last_row = None
    for row in reader:
        last_row = row

with open("Data/games.csv", "r", newline='', encoding='utf-8') as old_file, \
    open("Data/new_games.csv", "a", newline='', encoding='utf-8') as new_file:

    leitor = csv.DictReader(old_file)
    campos = leitor.fieldnames
    escritor = csv.DictWriter(new_file, fieldnames=campos)
    for linha in leitor:
        if(int(linha["app_id"]) <= int(last_row["app_id"])):
            continue
        url = "http://store.steampowered.com/api/appdetails?appids="+linha["app_id"]+"&cc=BR&filters=price_overview"
        response = requests.get(url)
        while(response.status_code != 200):
            time.sleep(300)
            response = requests.get(url)
        data = response.json()##[linha["app_id"]]["data"]["price_overview"]["final_formatted"]
        try:
            data = data[linha["app_id"]]["data"]["price_overview"]["final_formatted"].replace("R$ ","")
        except:
            data = "\\N"
        linha["price_overview"] = data
        escritor.writerow(linha)
