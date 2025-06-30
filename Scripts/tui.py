import curses
import csv
import os
from wcwidth import wcwidth
import pickle


def load_data(bin_path):
    with open(bin_path, "rb") as f:
    #   data: dict of app_id -> [name, release_date, price, positive, negative]
        data = pickle.load(f)
    # Convert to list of rows for TUI
    rows = []
    for app_id, values in data.items():
        row = [app_id] + [str(v) for v in values]
        rows.append(row)
    header = ['app_id', 'name', 'release_date', 'price', 'positive', 'negative']
    return header, rows, None

def draw_tui(stdscr, scroll_pos, rows, header, max_y, max_x, is_inverted, sort_key):
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
    rows_to_display = rows[scroll_pos : scroll_pos + displayable_rows]

    for i, row in enumerate(rows_to_display):
        if i + 1 >= max_y - 1:
            break

        price_raw = row[3]
        if price_raw == '\\N':
            formatted_price = ""
        else:
            try:
                price_float = int(price_raw) / 100
                formatted_price = f"R$ {price_float:.2f}".replace('.', ',')
            except (ValueError, IndexError):
                formatted_price = price_raw

        # Format release_date as yyyy/mm/dd and check for our invalid format
        if len(row[2]) == 8:
            release_date = f"{row[2][:4]}/{row[2][4:6]}/{row[2][6:]}"
        else:
            release_date = ""
        # Calculate score and total
        try:
            pos = int(row[4])
            neg = int(row[5])
            total = pos + neg
            score = f"{(pos / total * 100):.1f}%" if total > 0 else "-"
            total_str = str(total)
        except Exception:
            score = "-"
            total_str = "-"

        row_data = (
            fit_to_display_width(row[0], fixed_widths['app_id']) + separator +
            fit_to_display_width(row[1], name_width) + separator +
            fit_to_display_width(release_date, fixed_widths['release_date']) + separator +
            fit_to_display_width(formatted_price, fixed_widths['price']) + separator +
            fit_to_display_width(row[4], fixed_widths['positive']) + separator +
            fit_to_display_width(row[5], fixed_widths['negative']) + separator +
            fit_to_display_width(score, fixed_widths['score']) + separator +
            fit_to_display_width(total_str, fixed_widths['total'])
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
        f"Rows {scroll_pos+1}-{scroll_pos+len(rows)} of {len(rows)} | "
        f"Sort: {' '.join(key_display)} | Invert ({sort_order})"
    )
    right_text = "[q/esc] Quit"

    # Calculate padding
    total_length = len(left_text) + len(right_text)
    if total_length < max_x:
        padding = " " * (max_x - total_length - 1)
    else:
        # In the edge case that the terminal is too small
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


def sort_rows(rows, sort_key, is_inverted):
    if sort_key == 'app_id':
        return rows  # The data is already sorted by app_id, we do nothing.
    key_map = {
        'name': 1,
        'price': 3,
        'release_date': 2,
        'score': lambda row: (int(row[4]) / (int(row[4]) + int(row[5]))) if (row[4].isdigit() and row[5].isdigit() and int(row[4]) + int(row[5]) > 0) else 0,
    }
    key_func = key_map.get(sort_key, 1)
    return sorted(rows, key=key_func if callable(key_func) else lambda row: row[key_func], reverse=is_inverted)

def main(stdscr, header, rows):
    """Main function to run the TUI event loop."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    stdscr.nodelay(True)
    
    scroll_pos = 0
    is_inverted = False
    sort_key = 'app_id'
    sorted_rows = sort_rows(rows, sort_key, is_inverted)

    try:
        max_y, max_x = stdscr.getmaxyx()
        draw_tui(stdscr, scroll_pos, sorted_rows, header, max_y, max_x, is_inverted, sort_key)
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
                sorted_rows = sort_rows(rows, sort_key, is_inverted)
                scroll_pos = 0
            elif key == ord('a'):
                sort_key = 'app_id'
                sorted_rows = sort_rows(rows, sort_key, is_inverted)
                scroll_pos = 0
            elif key == ord('d'):
                sort_key = 'release_date'
                sorted_rows = sort_rows(rows, sort_key, is_inverted)
                scroll_pos = 0
            elif key == ord('n'):
                sort_key = 'name'
                sorted_rows = sort_rows(rows, sort_key, is_inverted)
                scroll_pos = 0
            elif key == ord('p'):
                sort_key = 'price'
                sorted_rows = sort_rows(rows, sort_key, is_inverted)
                scroll_pos = 0
            elif key == ord('s'):
                sort_key = 'score'
                sorted_rows = sort_rows(rows, sort_key, is_inverted)
                scroll_pos = 0
            elif key in [curses.KEY_DOWN, ord('j')]:
                max_y, _ = stdscr.getmaxyx()
                displayable_rows = max(1, max_y - 2)
                if scroll_pos < len(sorted_rows) - displayable_rows:
                    scroll_pos += 1
            elif key in [curses.KEY_UP, ord('k')]:
                if scroll_pos > 0:
                    scroll_pos -= 1

            try:
                max_y, max_x = stdscr.getmaxyx()
                draw_tui(stdscr, scroll_pos, sorted_rows, header, max_y, max_x, is_inverted, sort_key)
            except curses.error:
                pass

        curses.napms(10)


def filter_rows_by_app_ids(rows, app_ids):
    app_ids_set = set(str(a) for a in app_ids)
    return [row for row in rows if row[0] in app_ids_set]


if __name__ == "__main__":
    curses.wrapper(main)
