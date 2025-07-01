class BPlusNode:
    def __init__(self, t, leaf = False):
        self.t = t                              # grau mínimo
        self.keys = []                          # chaves (strings) ordenadas
        self.children = []                      # ponteiros p/ filhos (só existe nos nós não folha)
        self.values = []                        # listas de listas de inteiros (lista dos app_ids que cada tag/categoria possu)
        self.leaf = leaf                        # booleano se e ou não uma folha
        self.next = None                        # ponteiro que liga uma folha na outra (vazio por padrão)

    # num máximo de chaves == 2t -1, retorna true se cheio
    def is_full(self):
        return len(self.keys) == 2 * self.t - 1


class BPlusTree:
    def __init__(self, t):
        self.t = t
        self.root = BPlusNode(t, leaf=True)     # como no comço só tem root, ela já começa sendo uma folha

    def search(self, key, node = None): # key é uma string, node é assumido como None inicialmente, depois a recursão usa outro valor
        if node is None:
            node = self.root

        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if node.leaf:
            # se folha, procura a chave
            if i < len(node.keys) and key == node.keys[i]:
                return node.values[i]
            return None
        else:
            #print(i,len(node.keys))
            if i < len(node.keys) and key == node.keys[i]:
                # estamos em um nó interno, mas já achamos a key.
                # como o valor intermediário fica sempre no nodo à direita, precisamos adicionar 1 para que se dirija ao nodo correto
                # isso vem de como eu implementei a divisão dos filhos
                
                i += 1

            # nó interno, então desce no filho correto
            return self.search(key, node.children[i])

    def insert(self, key, value_list): # insere na árvore, se existir dá um append
        root = self.root
        if root.is_full():
            new_root = BPlusNode(self.t, leaf=False)
            new_root.children.append(root) # o filho 0 da nova raiz é a raiz antiga
            self._split_child(new_root, 0, root)
            self.root = new_root
            self._insert_non_full(new_root, key, value_list)
        else:
            self._insert_non_full(root, key, value_list)

    def _insert_non_full(self, node, key, value_list):
        i = len(node.keys) - 1

        if node.leaf:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            idx = i + 1

            if idx < len(node.keys) and node.keys[idx] == key:
                node.values[idx].append(value_list)
                return

            node.keys.insert(idx, key)
            node.values.insert(idx, value_list)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            if node.children[i].is_full():
                self._split_child(node, i, node.children[i])
                if key > node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key, value_list)

    def _split_child(self, parent, idx, full_child):
        t = self.t
        new_child = BPlusNode(t, leaf=full_child.leaf)

        if full_child.leaf: # metade direita vai pra new_child, metade esquerda continua em full_child
            new_child.keys   = full_child.keys[t:]           
            new_child.values = full_child.values[t:]
            full_child.keys   = full_child.keys[:t]          
            full_child.values = full_child.values[:t]

            new_child.next = full_child.next # aqui ocorre a encadeação das folhas
            full_child.next = new_child

            parent.keys.insert(idx, new_child.keys[0]) # a primeira chave a direita é copiada para o pai, assim na busca ainda é possível acessar o valor dela como folha
            parent.children.insert(idx + 1, new_child)

        else: #como não e folha é preciso fazer split do nodo intermediário
            promoted = full_child.keys[t - 1]

            new_child.keys     = full_child.keys[t:]     
            full_child.keys    = full_child.keys[:t - 1] 

            new_child.children = full_child.children[t:]
            full_child.children= full_child.children[:t]

            parent.keys.insert(idx, promoted)
            parent.children.insert(idx + 1, new_child)

    def print_tree(self, node= None, lvl= 0):
        if node is None:
            node = self.root
        indent = "    " * lvl

        if node.leaf:
            for k, v in zip(node.keys, node.values):
                if v is list:  # mostra pares (key, len(lista)) se for uma lista de inteiros
                    debug = [f"{k}:{len(v)}" for k, v in zip(node.keys, node.values)]
                else: # mostra pares (key, int) se for apenas um int(value) por key 
                    debug = [f"{k}:{v}" for k, v in zip(node.keys, node.values)]
            print(f"{indent}{debug}")
        else:
            print(f"{indent}{node.keys}")
            for child in node.children:
                self.print_tree(child, lvl + 1)
    
    def transverse_tree(self, app_id_set):
        ordered_ids = []
        node = self.root
        while not node.leaf:
            node = node.children[0]
        
        while node is not None:
            for value in node.values:
                # The value can be a list of IDs or a single ID.
                # We need to handle both cases to avoid a TypeError.
                if isinstance(value, list):
                    for app_id in value:
                        if app_id in app_id_set:
                            ordered_ids.append(app_id)
                elif isinstance(value, int):
                    if value in app_id_set:
                        ordered_ids.append(value)
            node = node.next
        return ordered_ids