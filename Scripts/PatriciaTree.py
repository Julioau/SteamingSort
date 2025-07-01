import csv
import os
import pickle

class Node:
    """
    Node for the PATRICIA Tree.
    Each node contains a key fragment, a dictionary of children,
    and a list of values if it represents the end of a full key.
    """
    def __init__(self, key='', value=None):
        self.key = key
        self.children = {}
        self.values = []  # A key can be associated with multiple original values (app_ids)
        if value is not None:
            self.values.append(value)

class PatriciaTree:
    """
    PATRICIA Tree (Radix Tree) implementation for efficient string storage and retrieval.
    """
    def __init__(self):
        self.root = Node()

    def _find_matching_child(self, node, key):
        """Finds the child that shares a prefix with the key."""
        if not key:
            return None
        child = node.children.get(key[0])
        if not child:
            return None
        
        common_prefix_len = 0
        for i in range(min(len(key), len(child.key))):
            if key[i] != child.key[i]:
                break
            common_prefix_len += 1
        
        return child, common_prefix_len

    def insert(self, key, value):
        """
        Inserts a key-value pair into the tree.
        The value here is the app_id associated with the game name.
        """
        node = self.root
        while True:
            match = self._find_matching_child(node, key)
            if not match:
                # No child shares a prefix, add a new leaf node
                new_node = Node(key, value)
                node.children[key[0]] = new_node
                return

            child, common_prefix_len = match
            
            # If the entire child key is a prefix of our current key
            if common_prefix_len == len(child.key):
                key = key[common_prefix_len:]
                node = child
                # If the key is fully consumed, it means we've reached an existing node.
                # Add the value to this node's list of values.
                if not key:
                    if value not in child.values:
                        child.values.append(value)
                    return
                continue  # Continue insertion with the rest of the key

            # We need to split the child node
            common_prefix = child.key[:common_prefix_len]
            child_remainder = child.key[common_prefix_len:]
            new_key_remainder = key[common_prefix_len:]

            # Create the new internal node for the common part
            internal_node = Node(common_prefix)
            node.children[common_prefix[0]] = internal_node

            # Update the old child to be a child of the new internal node
            child.key = child_remainder
            internal_node.children[child_remainder[0]] = child

            # If the new key has a remaining part, create a new leaf for it
            if new_key_remainder:
                new_leaf = Node(new_key_remainder, value)
                internal_node.children[new_key_remainder[0]] = new_leaf
            else:
                # The new key is a prefix of the existing key, so the internal node gets the value
                if value not in internal_node.values:
                    internal_node.values.append(value)
            return

    def _collect_all_values(self, node, results):
        """Recursively traverse nodes to collect all stored values."""
        if node.values:
            results.extend(node.values)
        for child in node.children.values():
            self._collect_all_values(child, results)

    def find_all_prefixed(self, prefix):
        """Finds all values for keys starting with a given prefix."""
        node = self.root
        key = prefix
        while key:
            match = self._find_matching_child(node, key)
            if not match:
                return []
            
            child, common_prefix_len = match

            # If prefix diverges from child's key, no match
            if common_prefix_len < len(key) and common_prefix_len < len(child.key):
                return []

            if common_prefix_len == len(child.key):
                key = key[common_prefix_len:]
                node = child
            elif common_prefix_len == len(key):  # Prefix is a prefix of child.key
                node = child
                key = ""  # Prefix consumed
                break
        
        if key:  # Prefix not fully found
            return []

        results = []
        self._collect_all_values(node, results)
        return list(set(results))  # Return unique values

class SuffixTree:
    """
    A Suffix Tree implementation using a Patricia Tree to store all suffixes,
    enabling efficient substring search (e.g., .*search_term.*).
    """
    def __init__(self):
        self.patricia_tree = PatriciaTree()

    def insert(self, word_part, app_id):
        """
        Inserts a word part (suffix) into the suffix tree, associating it with an app_id.
        """
        self.patricia_tree.insert(word_part, app_id)

    def search_substring(self, substring):
        """
        Searches for all app_ids associated with game names containing the given substring.
        Returns a list of unique app_ids.
        """
        return self.patricia_tree.find_all_prefixed(substring)

    def save_tree(self, file_path):
        """
        Saves the SuffixTree object to a binary file using pickle.
        """
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_tree(file_path):
        """
        Loads a SuffixTree object from a binary file using pickle.
        """
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def build_from_csv(csv_file_path):
        """
        Builds a SuffixTree from game names and app_ids in a CSV file.
        Assumes app_id is in the first column (index 0) and game name in the second (index 1).
        """
        game_suffix_tree = SuffixTree()
        count = 0
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) > 1:
                    app_id = row[0]  # First column is app_id
                    game_name = row[1] # Second column is game name
                    if game_name and game_name != '\\N':
                        # Insert all suffixes of the game name, associated with its app_id
                        for i in range(len(game_name)):
                            suffix = game_name[i:].lower() # Convert to lowercase for case-insensitive search
                            game_suffix_tree.insert(suffix, app_id)
                        count += 1
        print(f"Built Suffix Tree with {count} game names.")
        return game_suffix_tree
