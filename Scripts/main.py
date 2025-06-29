import sys
# import sel
# from BPlusTree import BPlusTree

# TODO: Implement loading of binary files and dictionary
# TODO: Implement search logic
# TODO: Implement search logic for name, category, tags
# TODO: Call tui.py with results

def main():
    print("""
        █▀▀ ▀█▀ █▀▀ █▀█ █▄█ ▀█▀ █▀█ █▀▀   █▀▀ █▀█ █▀▄ ▀█▀
        ▀▀█  █  █▀▀ █▀█ █ █  █  █ █ █ █   ▀▀█ █ █ █▀▄  █ 
        ▀▀▀  ▀  ▀▀▀ ▀ ▀ ▀ ▀ ▀▀▀ ▀ ▀ ▀▀▀   ▀▀▀ ▀▀▀ ▀ ▀  ▀ 
        """)
    print("Search by: [1] app_id, [2] name, [3] categories, [4] tags")
    choice = input("Enter choice (1-4): ").strip()
    if choice == '1':
        app_id = input("Enter app_id (int): ").strip()
        try:
            app_id = int(app_id)
        except ValueError:
            print("Invalid app_id.")
            sys.exit(1)
        results = search_by_app_id(data, app_id)
    elif choice in {'2', '3', '4'}:
        field_map = {'2': 'name', '3': 'categories', '4': 'tags'}
        field   = field_map[choice]
        value   = input(f"Enter {field}: ").strip()
        results = search_by_field(data, field, value)
    else:
        print("Invalid choice.")
        sys.exit(1)

    # Show results in TUI

if __name__ == "__main__":
    main()