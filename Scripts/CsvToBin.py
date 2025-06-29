import csv
from collections import defaultdict
import pickle
from BPlusTree import BPlusTree, BPlusNode
        

# Dicionário temporário onde as tags/categorias são chaves e os valores são listas de app_ids
category_dict = defaultdict(list)
"""
with open("Data/tags.csv", "r", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        app_id = row["app_id"]
        category = row["tag"]
        category_dict[category].append(int(app_id))
    chaves = list(category_dict.keys()) #lista de todas as tags
    tree = BPlusTree(t=7) #inicia uma árvore de grau 7 e ordem 8, assim tem um máximo de 3 níveis
    for key in chaves:
        tree.insert(key,category_dict[key])
    
with open("Data/tags.bin", "wb") as f:
    pickle.dump(tree,f)

"""
with open("Data/categories.bin", "rb") as f:
    arvi = pickle.load(f)
arvi.print_tree()
val = arvi.search("PvP")
print(val)

"""
 carrega dados na memória
with open("Data/tags.bin", "rb") as f:
    lista = pickle.load(f)

    guarda memória em disco
with open("Data/tags.bin", "wb") as f:
    pickle.dump(f)
"""

