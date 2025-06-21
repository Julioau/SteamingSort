import csv
from collections import defaultdict
import pickle

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t                 # Grau da árvore
        self.keys = []             # Lista das chaves (tuplas(string,int))
        self.children = []         # Lista de filhos (BtreeNode)
        self.leaf = leaf           # Booleano para saber se o nodo é folha


    def is_full(self):
        return len(self.keys) == 2 * self.t - 1 #true se o nodo (chaves) está cheio

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(t, True) # A raiz da árvore é um nodo
        self.t = t  # Grau da árvore

    def insert(self, k):
        root = self.root # Facilita referenciar a raiz assim
        if root.is_full():
            # Se a raiz estiver cheia
            new_root = BTreeNode(self.t, False) # Cria nova raiz
            new_root.children.append(root) # Anexa a raiz como o filho 0 da nova raiz
            self.split_child(new_root, 0, root) # Chama a função que divide os filhos em torno do valor médio
            self.root = new_root # New_root se torna a root
            self._insert_non_full(new_root, k) # Agora que tem espaço, insere a chave
        else:
            self._insert_non_full(root, k) # Como não tá cheio, é só inserir a chave

    def _insert_non_full(self, node, k):
        i = len(node.keys) - 1

        if node.leaf:
            # Insere chave na posição correta se o nodo for folha
            node.keys.append(None)  # Aumenta a lista em 1
            while i >= 0 and k < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = k
        else:
            # Procura em qual filho percorrer
            while i >= 0 and k < node.keys[i]:
                i -= 1
            i += 1

            # Divide o filho se ele estiver cheio
            if node.children[i].is_full():
                self.split_child(node, i, node.children[i])
                if k > node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], k)

    def split_child(self, parent, i, full_child):
        t = self.t
        new_child = BTreeNode(t, full_child.leaf)

        # A chave de valor médio sobe para o pai
        parent.keys.insert(i, full_child.keys[t - 1])

        # A metade menor fica em full_child, a metade maior em new_child
        new_child.keys = full_child.keys[t:] # De t até o maior valor
        full_child.keys = full_child.keys[:t - 1] # De 0 até t-2

        if not full_child.leaf: # Se full_child não for folha, é preciso redistribuir os filhos
            new_child.children = full_child.children[t:]
            full_child.children = full_child.children[:t]

        parent.children.insert(i + 1, new_child) # Insere new_child como filho do nodo pai
    
    def search_key(self, key, node=None):
        if node is None: # Começa pela raiz
            node = self.root

        i = 0 # Percorre a lista de chaves comparando o valor esperado com o primeiro campo da tupla
        while i < len(node.keys) and key > node.keys[i][0]:
            i += 1

        if i < len(node.keys) and key == node.keys[i][0]:
            return node.keys[i][1] # Retorna o valor para pesquisar na lista de app_id

        if node.leaf:
            return -1 # Retorna -1 se a tag/genre/category não existe

        return self.search_key(key, node.children[i])

    def print_tree(self, node=None, level=0): # Só para possibilitar a visualização da árvore
        if node is None:    # Se não especificar, começar pela raiz
            node = self.root

        print("    " * level + str(node.keys))  # Python permite multiplicar strings, bizarro! (chatgpt me salvou aqui)

        for child in node.children: # Recursivamente imprime o resto da árvore
            self.print_tree(child, level + 1)
        

# Dicionário temporário onde as tags/categorias são chaves e os valores são listas de app_ids
category_dict = defaultdict(list)

with open("Data/categories.csv", "r", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        app_id = row["app_id"]
        category = row["category"]
        category_dict[category].append(app_id)
    chaves = (list(sorted(category_dict.keys()))) #lista de todas as tags em ordem crescente alfanumérica
    lista = [] #lista de listas que armazena os app_id de cada tag separadamente
    tree = BTree(t=10) #inicia uma árvore de grau 10
    num = 0     #Faz referência à posição da tag/categoria/genero na lista do arquivo invertido`
    for key in chaves:
        tree.insert((key,num))
        num+=1
        lista.append(category_dict[key])
    
with open("Data/categoriestree.bin", "wb") as f:
    pickle.dump(tree,f)

with open("Data/categories.bin", "wb") as f:
    pickle.dump(lista,f)

with open("Data/categoriestree.bin", "rb") as f:
    arvi = pickle.load(f)
arvi.print_tree()

""" carrega dados na memória
with open("Data/tags.bin", "rb") as f:
    lista = pickle.load(f)

    guarda memória em disco
with open("Data/tags.bin", "wb") as f:
    pickle.dump(f)
"""

