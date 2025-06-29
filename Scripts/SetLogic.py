import pickle
from BPlusTree import BPlusTree, BPlusNode
from collections import defaultdict

with open("Data/tags.bin", "rb") as f: 
    tree = pickle.load(f)

with open("Data/games.bin", "rb") as d:
    d = pickle.load(d)



chosen_tags = ["Action"]
all_ids = set(tree.search(chosen_tags[0]))
for opt in chosen_tags[1:]:
    temp = tree.search(opt)
    if (temp == None):
        print(f"There was an error with your tags. The tag {opt} doesn't exist!")
        ##FAZER ALGO QUANDO DER ERRO
        all_ids = None
        break
    all_ids = all_ids.intersection(set(temp))
#tree.print_tree()
lista = sorted(all_ids)
for e in lista:
    x = d[str(e)]