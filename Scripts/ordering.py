import pickle
from BPlusTree import BPlusTree, BPlusNode
from collections import defaultdict


with open("Data/games.bin", "rb") as d:
    d = pickle.load(d)

tree = BPlusTree(200)
for key in d.keys():
    try:
        chave = d[key][3] / (d[key][3] + d[key][4])
    except:
        chave = 0
    tree.insert(chave,int(key))


with open("Data/reviewtree.bin", "wb") as f:
    pickle.dump(tree,f)

'''
with open("Data/reviewtree.bin", "rb") as f:
    a = pickle.load(f)
    print(a.search(0))
#tree.print_tree()
#print(tree.search("Alpha Prime")
#set = (10,2590)
#print(tree.transverse_tree(set))
'''
