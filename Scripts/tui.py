import curses
import csv
import os
from wcwidth import wcwidth

# just for testing
def load_data(file_path):
    script_dir = os.path.dirname(__file__) if __file__ else '.'
    absolute_path = os.path.join(script_dir, file_path)
    
    if not os.path.exists(absolute_path):
        return None, None, f"Error: File not found at '{absolute_path}'"

    try:
        with open(absolute_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
            return header, rows, None
    except Exception as e:
        return None, None, f"Error reading file: {e}"

def draw_tui(stdscr, scroll_pos, rows, header, max_y, max_x, is_inverted):
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

        # Format release_date as yyyy/mm/dd
        release_date = f"{row[2][:4]}/{row[2][4:6]}/{row[2][6:]}"

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
    sort_order = "Desc" if is_inverted else "Asc"
    status_text = f"Rows {scroll_pos+1}-{scroll_pos+len(rows_to_display)} of {len(rows)} | [i] Invert ({sort_order}) | [q/esc] Quit"
    if len(status_text) > max_x:
        status_text = status_text[:max_x-1]
    
    try:
        stdscr.addstr(max_y - 1, 0, status_text)
    except curses.error:
        pass

    stdscr.refresh()


def fit_to_display_width(text, max_width):
    """Truncate text so its display width does not exceed max_width."""
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


def main(stdscr):
    """Main function to run the TUI event loop."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    stdscr.nodelay(True)
    
    header, rows, error = load_data('../Data/games.csv')

    if error:
        stdscr.clear()
        stdscr.addstr(0, 0, error)
        stdscr.addstr(2, 0, "Press any key to exit.")
        stdscr.nodelay(False)
        stdscr.getch()
        return

    scroll_pos = 0
    is_inverted = False

    # Initial draw
    try:
        max_y, max_x = stdscr.getmaxyx()
        draw_tui(stdscr, scroll_pos, rows, header, max_y, max_x, is_inverted)
    except curses.error:
        pass

    while True:
        key = stdscr.getch()

        if key != -1:
            # Check for resize event first
            if key == curses.KEY_RESIZE:
                # Let the loop handle the redraw with new dimensions
                pass
            elif key == ord('q') or key == 27:
                break
            elif key == ord('i'):
                is_inverted = not is_inverted
                rows.reverse()
                scroll_pos = 0
            elif key in [curses.KEY_DOWN, ord('j'), ord('s')]:
                max_y, _ = stdscr.getmaxyx()
                displayable_rows = max(1, max_y - 2)
                if scroll_pos < len(rows) - displayable_rows:
                    scroll_pos += 1
            elif key in [curses.KEY_UP, ord('k'), ord('w')]:
                if scroll_pos > 0:
                    scroll_pos -= 1
            
            # Redraw on any action
            try:
                max_y, max_x = stdscr.getmaxyx()
                draw_tui(stdscr, scroll_pos, rows, header, max_y, max_x, is_inverted)
            except curses.error:
                pass
        
        curses.napms(10)


if __name__ == "__main__":
    curses.wrapper(main)
