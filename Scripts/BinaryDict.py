import csv
from collections import defaultdict
import pickle
from BPlusTree import BPlusTree, BPlusNode


category_dict = defaultdict(list)


"""

with open("Data/games.csv", "r", newline='', encoding='utf-8') as f,\
    open("Data/games.bin", "wb") as bin:
    reader = csv.DictReader(f)
    for row in reader:
        data = [row["name"]]
        try:
            release = int(row["release_date"])
        except:
            release = 100000000
        try:
            price = int(row["price_overview"])
        except:
            price = 0
        try:
            positive = int(row["positive"])
        except:
            positive = 0
        try:
            negative = int(row["negative"])
        except:
            negative = 0

        data.extend([release,price,positive,negative])
        category_dict[row["app_id"]].extend(data)
    pickle.dump(category_dict,bin)

"""
with open("Data/games.bin", "rb") as f:
    d = pickle.load(f)
    print(d)
