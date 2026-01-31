import pyautogui
import time
import random
import keyboard

# override
pyautogui.PAUSE = 0

# Local vars

TILES_X_START = 43 #671
TILES_Y_START = 370 #394
GRID_OFFSET = 24

CHECK_GRID_X_START = TILES_X_START + 15
CHECK_GRID_Y_START = TILES_Y_START + 18

# Colors and mapping
UNKNOWN = -1
MINE = 9

LOST = (238, 102, 102)

# watever flags, change later
clicked = []
cnt = 0
changed = False

num_color = [(56, 64, 72),      # 0
             (124, 199, 255),   # 1
             (102, 194, 102),   # 2
             (255, 119, 136),   # 3
             (238, 136, 255),   # 4
             (221, 170, 34),    # 5
             (102, 204, 204),   # 6
             (152, 152, 152),   # 7
             (247, 83, 83),     # flagged mine -> 9 (*)
             (76, 84, 92)]      # unknow -> map into -1 on matrix

# check for 2x2 square (x + 23, y + 23 -> x + 24, y + 24), 3 distinct -> continue, 2 -> stop

# checking for number, check 2x3 grid -> avg -> calc distance & compare, min -> choose

# winnin conditions (1030, 348 - 30x30) -> change to darker + mine detected (sum rgb < 100) x, y dependent, (850, 348) for 15x15

# get tile pos
def tiles_location(i, j):
    x = TILES_X_START + j * GRID_OFFSET
    y = TILES_Y_START + i * GRID_OFFSET
    return x, y

# check for number
def dist_to_colors(color1, color2):
    dist = 0
    for i in range(3):
        dist += (color2[i] - color1[i]) ** 2

    return dist
 
def closest_num(color_at_pixel):
    best_match = 0
    best_distance = dist_to_colors(color_at_pixel, num_color[0])

    for i in range(7): # 0 - 6
        distance = dist_to_colors(color_at_pixel, num_color[i])
        
        if distance < best_distance:
            best_distance = distance
            best_match = i
        
    return best_match

# mapping logic
def avg_color(colors):
    r = g = b = 0
    for c in colors:
        r += (c[0] / len(colors))
        g += (c[1] / len(colors))
        b += (c[2] / len(colors))

    return (int(r), int(g), int(b))

def read_tile(i, j):
    # mine check
    dx, dy = tiles_location(i, j)

    flag_px = pyautogui.pixel(dx + 13, dy + 8)
    if dist_to_colors(flag_px, num_color[8]) < 80:
        return MINE

    # 2x2 rec cheecking -> avg
    area = []
    for dy in range(2):
        for dx in range(2):
            px = CHECK_GRID_X_START + j * GRID_OFFSET + dx
            py = CHECK_GRID_Y_START + i * GRID_OFFSET + dy
            area.append(pyautogui.pixel(px, py))

    # take avg rgb value in that location
    color = avg_color(area)

    # unknown check
    if dist_to_colors(color, num_color[9]) < 10:
        return UNKNOWN

    # number check
    num = closest_num(color)

    # 7 last cause multiple pixel in the checking area
    if num not in [0,1,2,3,4,5,6]:
        return 7

    return num

def read_board(height, width):
    print("Mapping")
    board = [[UNKNOWN for _ in range(width)] for _ in range(height)]

    for i in range(height):
        for j in range(width):
            board[i][j] = read_tile(i, j)

    return board

def print_board(board):
    for row in board:
        print(" ".join(
            "." if x == UNKNOWN else
            "*" if x == MINE else
            " " if x == 0 else
            str(x) for x in row
        ))

# check for end
def distinct_colors(x, y):
    base_x, base_y = x + 23, y + 23
    prev = [pyautogui.pixel(base_x, base_y)]
    distinctCnt = 1
    
    for dy in range(2):
        for dx in range(2):
            check_x = base_x + dx
            check_y = base_y + dy
            color = pyautogui.pixel(check_x, check_y)
            new = True

            if dy == 0 and dx == 0:
                continue

            for k in range(len(prev)):
                if color == prev[k]:
                    new = False
                    break
            if new:
                distinctCnt += 1
                prev.append(color)
    return distinctCnt

def detect_board_size():
    width = 0
    while True:
        base_dx, base_dy = tiles_location(0, width)
        dx = base_dx + 24
        dy = base_dy + 23
        if pyautogui.pixel(dx, dy) == pyautogui.pixel(dx, dy + 1):
            break
        width += 1

    height = 0
    while True:
        base_dx, base_dy = tiles_location(height, width)
        dx = base_dx + 24
        dy = base_dy + 23
        if pyautogui.pixel(dx, dy) == pyautogui.pixel(dx - 1, dy + 1):
            break
        height += 1
        
    height += 1
    width += 1
    
    return height, width

# did we lost chat
def lost(i, j):
    dx, dy = tiles_location(i, j)
    color = pyautogui.pixel(dx + 2, dy + 2)

    if dist_to_colors(color, LOST) < 8:
        dx = int((2 * TILES_X_START + width * GRID_OFFSET + 0.5) / 2) 
        dy = 324
        pyautogui.leftClick(dx, dy)
        return True

    return False

# did we win chat?
def is_won(width):
    dx = int((2 * TILES_X_START + width * GRID_OFFSET + 0.5) / 2) 
    dy = 324
    r = g = b = 0

    for offset in [-1, 0, 1]:
        px = dx + offset
        rx, gx, bx = pyautogui.pixel(px, dy)
        r += rx
        g += gx
        b += bx
    # take avg
    r //= 3
    g //= 3
    b //= 3

    return (r + g + b) < 100

# opening clicking
def initial_clicking(height, width):
    while True:
        base_x_grid = random.randint(0, width - 1)
        base_y_grid = random.randint(0, height - 1)
        dx = TILES_X_START + base_x_grid * GRID_OFFSET
        dy = TILES_Y_START + base_y_grid * GRID_OFFSET

        pyautogui.click(dx + int(GRID_OFFSET / 2), dy + int(GRID_OFFSET / 2))
        pyautogui.moveTo(TILES_X_START - 20, TILES_Y_START - 20)

        time.sleep(0.1)
        num = read_tile(base_y_grid, base_x_grid)
        if lost(base_y_grid, base_x_grid):
            print("Bad choice i guess?")
            return 1
        if num == 0:
            break

        print(f"Clicked, found {num}. Continuing")

# solver

# board[i][j]
# if remaining_mines = unknow_neighbours -> click
# edit that pos inside the matrix -> 9 or mine
def click(actions):
    global clicked, cnt, changed
    changed = False
    for action in actions:
        base_x, base_y = tiles_location(action[0], action[1])
        to_do = action[2]
        clicked.append((action[0], action[1]))
        ok = True
        is_first = True

        for x in range(len(clicked)):
            if (action[0], action[1]) == clicked[x] and not is_first:
                ok = False
                is_first = False
                break
        
        if not ok:
            continue

        if cnt == len(actions):
            continue

        cnt = len(actions)
        dx = base_x + int(GRID_OFFSET / 2)
        dy = base_y + int(GRID_OFFSET / 2)
        pyautogui.click(dx, dy, clicks = 1, interval = 0.0, button = to_do)
        cnt += 1
        changed = True
        time.sleep(0.1)

    pyautogui.moveTo(TILES_X_START - 20, TILES_Y_START - 20)

def solver(board, height, width):
    # build action boards
    actions = []

    #scan
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            unknown_tiles = 0
            remaining_mines = 0
            know_mines = 0
            location = []

            if board[i][j] == -1: #skip checking unknow tiles
                continue

            for y in [-1, 0, 1]:
                for x in [-1, 0, 1]:
                    # avoid middle
                    if x == 0 and y == 0:
                        continue
                    # count unknow
                    if board[i + y][j + x] == -1:
                        unknown_tiles += 1
                        location.append((i + y, j + x, "right"))

                    # count know mines
                    if board[i + y][j + x] == 9:
                        know_mines += 1
            
            remaining_mines= board[i][j] - know_mines
            
            if remaining_mines == unknown_tiles:
                # all mines
                actions += location
            if remaining_mines == 0:
                # all safe
                for y in [-1, 0, 1]:
                    for x in [-1, 0, 1]:
                        if board[i + y][j + x] == -1:
                            actions.append((i + y, j + x, "left"))
    click(actions)
    if not changed:
        return

# hotkey
def map_hotkey():
    print()
    board = read_board(height, width)
    print_board(board)
    print()

def paused():
    global pause
    pause = True

def resume():
    global pause
    pause = False

def stop():
    global stop
    stop = True

#keyboard.add_hotkey("a", map_hotkey)
#keyboard.add_hotkey("p", paused)
#keyboard.add_hotkey("r", resume)
#keyboard.add_hotkey("esc", stop)

# main
if __name__ == "__main__":
#    time.sleep(2)  # time to alt-tab

    height, width = detect_board_size()
    pause = False
    stop = False

    if not initial_clicking(height, width):
        board = read_board(height, width)
        print_board(board)
        while True:
            if is_won(width):
                print ("won")
                break
            elif pause:
                print("Pausing")
                while pause:
                    if stop:
                        print("Stopped")
                        break
                    time.sleep(1)

            elif stop:
                print("Stopped")
                break

            else:
                solver(board, height, width)
                board = read_board(height, width)
                print_board(board)
                if not changed:
                    break
