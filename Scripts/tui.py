import curses
# import csv
# import os
from wcwidth import wcwidth
import pickle
from collections import defaultdict



def draw_tui(stdscr, scroll_pos, app_ids, games_data, max_y, max_x, is_inverted, sort_key):
    stdscr.erase()

    # Fixed widths for columns
    fixed_widths = {
        'app_id': 8,
        'release_date': 12,
        'price': 11,
        'positive': 11,
        'negative': 11,
        'score': 6,
        'total': 11,
    }
    separator = " | "
    used_space = (
        fixed_widths['app_id'] +
        fixed_widths['release_date'] +
        fixed_widths['price'] +
        fixed_widths['positive'] +
        fixed_widths['negative'] +
        fixed_widths['score'] +
        fixed_widths['total'] +
        7 * len(separator)
    )
    name_width = max(10, max_x - used_space - 1)

    # --- Display Header ---
    header_template = (
        f"{{:<{fixed_widths['app_id']}}}{separator}"
        f"{{:<{name_width}}}{separator}"
        f"{{:<{fixed_widths['release_date']}}}{separator}"
        f"{{:<{fixed_widths['price']}}}{separator}"
        f"{{:<{fixed_widths['positive']}}}{separator}"
        f"{{:<{fixed_widths['negative']}}}{separator}"
        f"{{:<{fixed_widths['score']}}}{separator}"
        f"{{:<{fixed_widths['total']}}}"
    )
    header_text = header_template.format('app_id', 'name', 'release_date', 'price', 'positive', 'negative', 'score', 'total')
    if len(header_text) > max_x:
        header_text = header_text[:max_x]
    stdscr.addstr(0, 0, header_text, curses.A_REVERSE)

    # --- Display Data Rows ---
    displayable_rows = max_y - 2 # For header and footer
    ids_to_display = app_ids[scroll_pos : scroll_pos + displayable_rows]

    for i, app_id in enumerate(ids_to_display):
        if i + 1 >= max_y - 1:
            break
        
        row = games_data.get(str(app_id))
        if not row:
            continue

        price_raw = row[2]
        if price_raw == r'\N':
            formatted_price = ""
        else:
            try:
                price_float = int(price_raw) / 100
                formatted_price = f"R$ {price_float:.2f}".replace('.', ',')
            except (ValueError, IndexError):
                formatted_price = price_raw

        release_date_str = str(row[1])
        if len(release_date_str) == 8:
            release_date = f"{release_date_str[:4]}/{release_date_str[4:6]}/{release_date_str[6:]}"
        else:
            release_date = ""

        try:
            pos = int(row[3])
            neg = int(row[4])
            total = pos + neg
            score = f"{(pos / total * 100):.1f}%" if total > 0 else "-"
            total_str = str(total)
        except Exception:
            score = "-"
            total_str = "-"

        row_data = (
            fit_to_display_width(str(app_id), fixed_widths['app_id']) + separator +
            fit_to_display_width(str(row[0]), name_width) + separator +
            fit_to_display_width(str(release_date), fixed_widths['release_date']) + separator +
            fit_to_display_width(str(formatted_price), fixed_widths['price']) + separator +
            fit_to_display_width(str(row[3]), fixed_widths['positive']) + separator +
            fit_to_display_width(str(row[4]), fixed_widths['negative']) + separator +
            fit_to_display_width(str(score), fixed_widths['score']) + separator +
            fit_to_display_width(str(total_str), fixed_widths['total'])
        )

        if len(row_data) > max_x:
            row_data = row_data[:max_x - 1]

        try:
            stdscr.addstr(i + 1, 0, row_data)
        except curses.error:
            pass

    # --- Display Footer/Status Bar ---
    sort_order = "DESCENDING" if is_inverted else "ASCENDING"

    sort_keys = {
        'a': 'AppID',
        'n': 'Name',
        'p': 'Price',
        'd': 'Date',
        's': 'Score'
    }
    key_display = []
    for k, label in sort_keys.items():
        if (
            (k == 'a' and sort_key == 'app_id') or
            (k == 'n' and sort_key == 'name') or
            (k == 'p' and sort_key == 'price') or
            (k == 'd' and sort_key == 'release_date') or
            (k == 's' and sort_key == 'score')
        ):
            key_display.append(f"[{label.upper()}]")
        else:
            key_display.append(f"{label}")

    left_text = (
        f"Rows {scroll_pos+1}-{scroll_pos+len(app_ids)} of {len(app_ids)} | "
        f"Sort: {' '.join(key_display)} | Invert ({sort_order})"
    )
    right_text = "[q/esc] Quit"

    total_length = len(left_text) + len(right_text)
    if total_length < max_x:
        padding = " " * (max_x - total_length - 1)
    else:
        left_text = left_text[:max_x - len(right_text) - 1]
        padding = ""

    status_text = f"{left_text}{padding}{right_text}"

    try:
        stdscr.addstr(max_y - 1, 0, status_text, curses.A_REVERSE)
    except curses.error:
        pass

    stdscr.refresh()

def fit_to_display_width(text, max_width):
    # In the edge case that the terminal is too small
    acc = 0
    result = ''
    
    for ch in text:
        w = wcwidth(ch)
        if w < 0:
            w = 0
        if acc + w > max_width:
            break
        result += ch
        acc += w
    # Pad if needed
    if acc < max_width:
        result += ' ' * (max_width - acc)
    return result

def sort_rows(app_ids, sort_key, is_inverted, trees):
    # Standardize app_ids to integers for reliable sorting and lookups
    int_app_ids = [int(a) for a in app_ids]

    if sort_key == 'app_id':
        sorted_ids = sorted(int_app_ids, reverse=is_inverted)
        return [str(i) for i in sorted_ids]

    tree_map = {
        'name': trees['name'],
        'price': trees['price'],
        'release_date': trees['release'],
        'score': trees['review']  # Note: This sorts by review count, not score %
    }

    if sort_key in tree_map:
        tree = tree_map[sort_key]
        # Use the tree to get the correctly ordered list of app_ids
        sorted_ids = tree.transverse_tree(set(int_app_ids))
        
        if is_inverted:
            sorted_ids.reverse()
        
        return [str(i) for i in sorted_ids]

    # As a final fallback, sort by app_id if the key is somehow invalid
    sorted_ids = sorted(int_app_ids, reverse=is_inverted)
    return [str(i) for i in sorted_ids]

def main(stdscr, games_data, app_ids, trees):
    """Main function to run the TUI event loop."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    stdscr.nodelay(True)
    
    scroll_pos = 0
    is_inverted = False
    sort_key = 'app_id'
    
    # Initial sort based on the default key
    sorted_app_ids = sort_rows(app_ids, sort_key, is_inverted, trees)

    try:
        max_y, max_x = stdscr.getmaxyx()
        draw_tui(stdscr, scroll_pos, sorted_app_ids, games_data, max_y, max_x, is_inverted, sort_key)
    except curses.error:
        pass

    while True:
        key = stdscr.getch()

        if key != -1:
            if key == curses.KEY_RESIZE:
                pass
            elif key == ord('q') or key == 27:
                break
            elif key == ord('i'):
                is_inverted = not is_inverted
                sorted_app_ids = sort_rows(app_ids, sort_key, is_inverted, trees)
                scroll_pos = 0
            elif key in [ord('a'), ord('n'), ord('p'), ord('d'), ord('s')]:
                key_map = {
                    ord('a'): 'app_id',
                    ord('n'): 'name',
                    ord('p'): 'price',
                    ord('d'): 'release_date',
                    ord('s'): 'score'
                }
                sort_key = key_map[key]
                sorted_app_ids = sort_rows(app_ids, sort_key, is_inverted, trees)
                scroll_pos = 0
            elif key in [curses.KEY_DOWN, ord('j')]:
                max_y, _ = stdscr.getmaxyx()
                displayable_rows = max(1, max_y - 2)
                if scroll_pos < len(sorted_app_ids) - displayable_rows:
                    scroll_pos += 1
            elif key in [curses.KEY_UP, ord('k')]:
                if scroll_pos > 0:
                    scroll_pos -= 1

            try:
                max_y, max_x = stdscr.getmaxyx()
                draw_tui(stdscr, scroll_pos, sorted_app_ids, games_data, max_y, max_x, is_inverted, sort_key)
            except curses.error:
                pass

        curses.napms(10)
