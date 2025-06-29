import pickle
from BPlusTree import BPlusTree, BPlusNode
from collections import defaultdict

with open("Data/categories.bin", "rb") as f: 
    tree = pickle.load(f)

with open("Data/games.bin", "rb") as d:
    d = pickle.load(d)



chosen_tags = ["PvP"] #lista das tags escolhidas
all_ids = set(tree.search(chosen_tags[0])) # o set começa possuindo todos os app_ids da primeira tag
for opt in chosen_tags[1:]: #itera pra cada tag da lista
    temp = tree.search(opt) #lista de todos os id's que possuem essa tag
    if (temp == None):
        print(f"There was an error with your tags. The tag {opt} doesn't exist!")
        ##FAZER ALGO QUANDO DER ERRO
        all_ids = None
        break
    all_ids = all_ids.intersection(set(temp)) #faz a intersecção do conjunto antigo com os app_ids da nova tag

#tree = BPlusTree(10)
#for key in d.keys():
#    tree.insert(d[key][0],int(key))
#tree.print_tree()
#print(tree.search("Alpha Prime"))
with open("Data/nametree.bin", "rb") as f:
    tree = pickle.load(f)
print(tree.transverse_tree(all_ids))
    


#tree.print_tree()
#lista = sorted(all_ids)
#for e in lista:
#    x = d[str(e)]