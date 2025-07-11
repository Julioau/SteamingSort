import sys
import pickle
import curses
import os
from tui import main as tui_main
from BPlusTree import BPlusTree, BPlusNode
from collections import defaultdict
from PatriciaTree import SuffixTree

# We only load the csv in case we need to rebuild the tree
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data', 'games.csv')

# We were using hard coded relative paths before, this made the code not run when being called from different folders.
# This is an ugly fix, but at least now it works from anywhere, which is not required, but good.
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')
GAMES_BIN_PATH = os.path.join(DATA_DIR, 'games.bin')
CATEGORIES_BIN_PATH = os.path.join(DATA_DIR, 'categories.bin')
TAGS_BIN_PATH = os.path.join(DATA_DIR, 'tags.bin')
NAMETREE_BIN_PATH = os.path.join(DATA_DIR, 'nametree.bin')
PRICETREE_BIN_PATH = os.path.join(DATA_DIR, 'pricetree.bin')
RELEASETREE_BIN_PATH = os.path.join(DATA_DIR, 'releasetree.bin')
REVIEWTREE_BIN_PATH = os.path.join(DATA_DIR, 'reviewtree.bin')
PATRICIA_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data', 'patricia.bin')

def display_menu(bad_option, no_results, last_input, last_search, BLINK, BLUE, RED, RESET):
    os.system('cls' if os.name == 'nt' else 'clear') # Clear screen before displaying menu
    if bad_option:
        print(f"{BLUE}Invalid option '{last_input}', please try again.{RESET}")
    if no_results:
        print(f"{BLUE}That search for '{last_search}' yielded no results {RESET}or {RED}your input was invalid.{RESET}")
    print(f"""
{BLUE}█▀▀ ▀█▀ █▀▀ █▀█ █▄█{RESET}{BLINK} ▀█▀ █▀█ █▀▀{RESET}{BLUE}   █▀▀ █▀█ █▀▄ ▀█▀
▀▀█  █  █▀▀ █▀█ █ █{RESET}{BLINK}  █  █ █ █ █{RESET}{BLUE}   ▀▀█ █ █ █▀▄  █ 
▀▀▀  ▀  ▀▀▀ ▀ ▀ ▀ ▀{RESET}{BLINK} ▀▀▀ ▀ ▀ ▀▀▀{RESET}{BLUE}   ▀▀█ ▀▀▀ ▀ ▀  ▀{RESET}
""")
    print(f"""Press {RED}q{RESET} to quit at any time.
Search by: [{BLUE}1{RESET}] app_id, [{BLUE}2{RESET}] name, [{BLUE}3{RESET}] categories, [{BLUE}4{RESET}] tags
Enter choice: """, end="")

# Returns a single app_id if it exists in games_data
def search_by_app_id(app_id, games_data):
    if str(app_id) in games_data:
        return [app_id]
    return []

# Returns a list of app_ids for the given name
def search_by_name(name_tree, name):
    result = name_tree.search(name)
    return result if result is not None else []

def search_by_multiple_keys(tree, value):
    values = value.strip().split(',')
    chosen_keys = [v.strip() for v in values if v.strip()]
    if not chosen_keys:
        print("No values entered.")
        return []
    
    # Get initial set of IDs from the first key
    first_ids = tree.search(chosen_keys[0])
    if not first_ids:
        print(f"'{chosen_keys[0]}' not found.")
        return []
    
    app_ids = set(first_ids)
    
    # Intersect with IDs from the remaining keys
    for key in chosen_keys[1:]:
        ids = tree.search(key)
        if not ids:
            print(f"'{key}' not found.")
            return []
        app_ids &= set(ids)
        
    return list(app_ids)

def main():
    BLINK = "\033[5m"
    BLUE  = "\033[34m"
    RED   = "\033[31m"
    RESET = "\033[0m"

    # Display menu immediately
    display_menu(False, False, "", "", BLINK, BLUE, RED, RESET)
    print(f"{BLUE}Loading data...{RESET}")

    # Load main data and trees once
    games_data = None
    categories_tree = None
    tags_tree = None
    name_tree = None
    price_tree = None
    release_tree = None
    review_tree = None
    patricia = None

    try:
        with open(GAMES_BIN_PATH, 'rb') as f:
            games_data = pickle.load(f)
        with open(CATEGORIES_BIN_PATH, 'rb') as f:
            categories_tree = pickle.load(f)
        with open(TAGS_BIN_PATH, 'rb') as f:
            tags_tree = pickle.load(f)
        with open(NAMETREE_BIN_PATH, 'rb') as f:
            name_tree = pickle.load(f)
        with open(PRICETREE_BIN_PATH, 'rb') as f:
            price_tree = pickle.load(f)
        with open(RELEASETREE_BIN_PATH, 'rb') as f:
            release_tree = pickle.load(f)
        with open(REVIEWTREE_BIN_PATH, 'rb') as f:
            review_tree = pickle.load(f)

        # Load or build the SuffixTree
        try:
            # Load
            patricia = SuffixTree.load_tree(PATRICIA_PATH)
        except FileNotFoundError:
            # Build
            patricia = SuffixTree.build_from_csv(CSV_FILE_PATH)
            patricia.save_tree(PATRICIA_PATH)
        except Exception as e:
            patricia = SuffixTree.build_from_csv(CSV_FILE_PATH)
            patricia.save_tree(PATRICIA_PATH)

    except FileNotFoundError as e:
        print(f"{RED}Error: Required data file not found: {e.filename}. Please ensure all .bin files are in the Data directory.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}An unexpected error occurred during data loading: {e}{RESET}")
        sys.exit(1)

    trees = {
        'categories': categories_tree,
        'tags': tags_tree,
        'name': name_tree,
        'price': price_tree,
        'release': release_tree,
        'review': review_tree
    }

    bad_option, no_results = False, False
    last_input = ""
    last_search = ""

    while True:
        display_menu(bad_option, no_results, last_input, last_search, BLINK, BLUE, RED, RESET)

        choice = input().strip()
        last_input = choice
        results = []
        match choice:
            case '1':
                app_id = input("Enter app_id (int): ").strip()
                last_search = app_id
                results = search_by_app_id(app_id, games_data)
            case '2':
                value = input("Enter name (substring search): ").strip()
                last_search = value
                results = patricia.search_substring(value.lower())
            case '3':
                value = input("Enter categories (comma-separated): ").strip()
                last_search = value
                results = search_by_multiple_keys(categories_tree, value)
            case '4':
                value = input("Enter tags (comma-separated): ").strip()
                last_search = value
                results = search_by_multiple_keys(tags_tree, value)
            case 'q' | 'Q':
                sys.exit(0)
            case _:
                bad_option = True
                continue

        if not results:
            no_results = True
            continue

        # Show results in TUI, passing all necessary data
        curses.wrapper(lambda stdscr: tui_main(stdscr, games_data, results, trees))

if __name__ == "__main__":
    main()
