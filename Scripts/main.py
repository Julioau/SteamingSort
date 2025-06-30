import sys
import pickle
import curses
import os
from tui import main as tui_main, load_data
from BPlusTree import BPlusTree, BPlusNode

# Returns a single app_id, for the app_id search
def search_by_app_id(rows, app_id):
    return [row for row in rows if row[0] == str(app_id)]

# Returns a list of rows for the given app_ids
def filter_rows_by_app_ids(rows, app_ids):
    app_ids = set(str(a) for a in app_ids)
    return [row for row in rows if row[0] in app_ids]

def search_by_field(rows, field, value):
    idx_map = {'name': 1, 'categories': None, 'tags': None}
    idx = idx_map.get(field)
    if idx is not None:
        return [row for row in rows if value.lower() in row[idx].lower()]
    return []

def search_by_multiple_keys(rows, tree, prompt, value=None):
    if value is None:
        values = input(prompt).strip().split(',')
    else:
        values = value.strip().split(',')
    chosen_keys = [v.strip() for v in values if v.strip()]
    if not chosen_keys:
        print("No values entered.")
        return []
    first_ids = tree.search(chosen_keys[0])
    if not first_ids:
        print(f"'{chosen_keys[0]}' not found.")
        return []
    app_ids = set(first_ids)
    for key in chosen_keys[1:]:
        ids = tree.search(key)
        if not ids:
            print(f"'{key}' not found.")
            return []
        app_ids &= set(ids)
    return filter_rows_by_app_ids(rows, app_ids)

def main():
    BLINK = "\033[5m"
    BLUE  = "\033[34m"
    RED   = "\033[31m"
    RESET = "\033[0m"

    # Load main data and trees once
    header, rows, error = load_data('../Data/games.bin')
    if error:
        print(error)
        sys.exit(1)
    with open('../Data/categories.bin', 'rb') as f:
        categories_tree = pickle.load(f)
    with open('../Data/tags.bin', 'rb') as f:
        tags_tree = pickle.load(f)

    bad_option, no_results = False, False
    last_input = ""
    last_search = ""

    while True:
        os.system('cls' if os.name == 'nt' else 'clear') # in case curses is ever officially supported on windows, the program is essentially cross-platform
        if bad_option:
            print(f"{BLUE}Invalid option '{last_input}', please try again.{RESET}")
            bad_option = False
        if no_results:
            print(f"{BLUE}That search for '{last_search}' yielded no results {RESET}or {RED}your input was invalid.{RESET}")
            no_results = False
        print(f"""
{BLUE}█▀▀ ▀█▀ █▀▀ █▀█ █▄█{RESET}{BLINK} ▀█▀ █▀█ █▀▀{RESET}{BLUE}   █▀▀ █▀█ █▀▄ ▀█▀
▀▀█  █  █▀▀ █▀█ █ █{RESET}{BLINK}  █  █ █ █ █{RESET}{BLUE}   ▀▀█ █ █ █▀▄  █ 
▀▀▀  ▀  ▀▀▀ ▀ ▀ ▀ ▀{RESET}{BLINK} ▀▀▀ ▀ ▀ ▀▀▀{RESET}{BLUE}   ▀▀▀ ▀▀▀ ▀ ▀  ▀{RESET}
""")
        print(f"""Press {RED}q{RESET} to quit at any time.
Search by: [{BLUE}1{RESET}] app_id, [{BLUE}2{RESET}] name, [{BLUE}3{RESET}] categories, [{BLUE}4{RESET}] tags
Enter choice: """, end="")

        choice = input().strip()
        last_input = choice
        results = []
        match choice:
            case '1':
                app_id = input("Enter app_id (int): ").strip()
                last_search = app_id
                results = search_by_app_id(rows, app_id)
            case '2':
                value = input("Enter name: ").strip()
                last_search = value
                results = search_by_field(rows, 'name', value)
            case '3':
                value = input("Enter categories (comma-separated): ").strip()
                last_search = value
                results = search_by_multiple_keys(rows, categories_tree, "", value)
            case '4':
                value = input("Enter tags (comma-separated): ").strip()
                last_search = value
                results = search_by_multiple_keys(rows, tags_tree, "", value)
            case 'q' | 'Q':
                sys.exit(0)
            case _:
                bad_option = True
                continue

        if not results:
            no_results = True
            continue

        # Show results in TUI
        curses.wrapper(lambda stdscr: tui_main(stdscr, header, results))

if __name__ == "__main__":
    main()