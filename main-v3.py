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

# colors
LOST = (238, 102, 102)
LOST_FACE = (112, 95, 7) # avg of 4
# checking pos: 277, 333

num_color = [(56, 64, 72),      # 0
             (124, 199, 255),   # 1
             (102, 194, 102),   # 2
             (255, 119, 136),   # 3
             (238, 136, 255),   # 4
             (221, 170, 34),    # 5>S
             (102, 204, 204),   # 6
             (152, 152, 152),   # 7
             (247, 83, 83),     # flagged mine -> 9 (*)
             (76, 84, 92)]      # unknow -> map into -1 on matrix (.)

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

# mapping, board logic
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

def remap_board(clicked, board, height, width):
    for pos in clicked:
        i = pos[0]
        j = pos[1]
        num = read_tile(i, j)

        if num == 0:
            board = read_board(height, width)
            return board
        elif num == 9:
            board[i][j] = 9
        else:
            board[i][j] = num

    print("Mapping")
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
def lost(width):
    dx = int((2 * TILES_X_START + width * GRID_OFFSET + 0.5) / 2) 
    dy = 354
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

    return (r + g + b) < 36

# did we win chat?
def won(width):
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
def restart_game(width, bypass):
    if lost(width) or won(width) or bypass == "forced":
        dx = int((2 * TILES_X_START + width * GRID_OFFSET + 0.5) / 2) 
        dy = 324
            
        pyautogui.leftClick(dx, dy)
            
        return True
    
    else:
        return False

def initial_clicking(height, width):
    while True:
        base_x_grid = random.randint(0, width - 1)
        base_y_grid = random.randint(0, height - 1)
        dx = TILES_X_START + base_x_grid * GRID_OFFSET
        dy = TILES_Y_START + base_y_grid * GRID_OFFSET

        pyautogui.click(dx + int(GRID_OFFSET / 2), dy + int(GRID_OFFSET / 2))
        pyautogui.moveTo(TILES_X_START - 20, TILES_Y_START - 20)

        time.sleep(0.35)
        num = read_tile(base_y_grid, base_x_grid)
        
        if restart_game(width, "not"):
            print("Bad choice i guess?")
            return 1
        
        if num == 0:
            break

        print(f"Clicked, found {num}. Continuing")
    
    print("My job here is done, good luck")

# valid neighbour
def iter_neighbors(i, j, height, width):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            # skip itself
            if dy == 0 and dx == 0:
                continue

            ni = i + dy
            nj = j + dx

            # skip out of bounds
            if ni < 0 or ni >= height or nj < 0 or nj >= width:
                continue

            yield ni, nj

# solver
def have_dupe(i, j, clicked):
    for coords in range(len(clicked)):
        if (i, j) == clicked[coords]:
            return True
    
    return False

def click(actions):
    global clicked
    clicked = []
    is_first = True

    for action in actions:
        i = action[0]
        j = action[1]
        base_x, base_y = tiles_location(i, j)
        to_do = action[2]

        if not is_first and have_dupe(i, j, clicked):
            continue

        dx = base_x + int(GRID_OFFSET / 2)
        dy = base_y + int(GRID_OFFSET / 2)
        is_first = False
        clicked.append((i, j))
        pyautogui.click(dx, dy, clicks = 1, interval = 0.0, button = to_do)
        time.sleep(0.02)

    pyautogui.moveTo(TILES_X_START - 20, TILES_Y_START - 20)

def solver(board, height, width):
    # build action boards
    actions = []

    #scan
    for dy in range(0, height):
        for dx in range(0, width):
            unknown_tiles = 0
            remaining_mines = 0
            know_mines = 0
            location = []

            if board[dy][dx] == -1: #skip checking unknow tiles
                continue

            for y in [-1, 0, 1]:
                for x in [-1, 0, 1]:
                    # avoid border
                    if not (0 <= dy + y < height) or not (0 <= dx + x < width):
                        continue

                    # avoid middle
                    if x == 0 and y == 0:
                        continue

                    # count unknow
                    if board[dy + y][dx + x] == -1:
                        unknown_tiles += 1
                        location.append((dy + y, dx + x, "right"))

                    # count know mines
                    if board[dy + y][dx + x] == 9:
                        know_mines += 1
            
            remaining_mines= board[dy][dx] - know_mines
            
            # build action board
            if remaining_mines == unknown_tiles:
                # all mines
                actions += location

            if remaining_mines == 0:
                # all safe
                for y in [-1, 0, 1]:
                    for x in [-1, 0, 1]:
                        if not (0 <= dy + y < height) or not (0 <= dx + x < width):
                            continue
                
                        if board[dy + y][dx + x] == -1:
                            actions.append((dy + y, dx + x, "left"))

    if len(actions) == 0:
        return False # for brute force later
        
    click(actions)
    return True

# brute logics
def touches_constraint_cell(board, dy, dx, height, width):
    for y in [-1, 0, 1]:
        for x in [-1, 0, 1]:
            # avoid border
            if not (0 <= dy + y < height) or not (0 <= dx + x < width):
                continue

            # avoid middle
            if x == 0 and y == 0:
                continue

            if 1 <= board[dy + y][dx + x] < 9:
                return True
            
    return False

def extract_frontier(board, height, width):
    frontier = []

    for dy in range(height):
        for dx in range(width):
            if board[dy][dx] == UNKNOWN and touches_constraint_cell(board, dy, dx, height, width):
                frontier.append((dy, dx))

    return frontier

def numbered_frontier_neighbours(board, dy, dx, height, width):
    neighbors = []

    for y in [-1, 0, 1]:
        for x in [-1, 0, 1]:
            # avoid border
            if not (0 <= dy + y < height) or not (0 <= dx + x < width):
                continue

            # avoid middle
            if x == 0 and y == 0:
                continue

            if 1 <= board[dy + y][dx + x] < 9:
                neighbors.append((dy + y, dx + x))

    return neighbors

def check_board_for_constraint(board, height, width):
    numbered_cells = []
    numbered_cells_w_frontier = []
    
    for dy in range(height):
        for dx in range(width):
            if 1 <= board[dy][dx]< 9:
                numbered_cells.append((dy, dx))

    for i in range(len(numbered_cells)):
        # check neighbors
        dy = numbered_cells[i][0]
        dx = numbered_cells[i][1]
        temp = []
        know_mines = 0

        for y in [-1, 0, 1]:
            for x in [-1, 0, 1]:
                # avoid border
                if not (0 <= dy + y < height) or not (0 <= dx + x < width):
                    continue

                # avoid middle
                if x == 0 and y == 0:
                    continue

                if board[dy + y][dx + x] == -1:
                    temp.append((dy + y, dx + x))
                    
                if board[dy + y][dx + x] == 9:
                    know_mines += 1
        
        remaining_mines = board[dy][dx] - know_mines
        numbered_cells_w_frontier.append(((dy, dx), temp, remaining_mines))

    return numbered_cells_w_frontier

def extract_constraints(board, frontier, height, width):
    index = {cell: idx for idx, cell in (frontier)}
    constraints = []

    for dy in range(height):
        for dx in range(width):
            # take only numbered cells
            if not (1 <= board[dy][dx] < 9):
                continue

            unknowns = []
            know_mines = 0

            for y in [-1, 0, 1]:
                for x in [-1, 0, 1]:
                    # avoid border
                    if not (0 <= dy + y < height) or not (0 <= dx + x < width):
                        continue

                    # avoid middle
                    if x == 0 and y == 0:
                        continue

                    if board[dy + y][dx + x] == UNKNOWN and (dy + y, dx + x) in index:
                        unknowns.append(index[(dy + y, dx + x)])
                    elif board[dy + y][dx + x] == MINE:
                        know_mines += 1

            # add only when not empty
            if unknowns:
                remaining_mines = board[dy][dx] - know_mines
                constraints.append((unknowns, remaining_mines))

    return constraints

def increment_binary_once(arr):
    i = len(arr) - 1
    
    while i >= 0:
        if arr[i] == 0:
            arr[i] = 1
            break
        else:
            arr[i] = 0
            i -= 1
        
    return arr

def brute_force(frontier, constraints):
    length_frontier = len(frontier)
    state = []
    valid_state = []

    for _ in range(length_frontier):
        state.append(0)

    print(2 ** len(state))

    for _ in range(2 ** len(state)):
        valid = True

        for indexes, remaining_mines in constraints:
            assume_mine_count = 0

            for idx in indexes:
                assume_mine_count += state[idx]

            if assume_mine_count != remaining_mines:
                valid = False
                break
        
        if valid:
            valid_state.append(state.copy())

        state = increment_binary_once(state)

    if not valid_state:
        return False
    
    # build action list
    actions = []

    for i in range(length_frontier):
        assume_mine_count = 0
        for state in valid_state:
            assume_mine_count += state[i]

        if assume_mine_count == 0:
            actions.append((*frontier[i], "left"))
        elif assume_mine_count == len(valid_state):
            actions.append((*frontier[i], "right"))

    if len(actions) == 0:
        return False
    
    click(actions)
    return True

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

def should_stop():
    global stop
    stop = True

keyboard.add_hotkey("a", map_hotkey)
keyboard.add_hotkey("p", paused)
keyboard.add_hotkey("r", resume)
keyboard.add_hotkey("esc", should_stop)

# main
if __name__ == "__main__":
#    time.sleep(2)  # time to alt-tab

    height, width = detect_board_size()
    pause = False
    stop = False

    while True:
        if not initial_clicking(height, width):
            board = read_board(height, width)
            print_board(board)
                
            while True:
                if won(width):
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
                    if solver(board, height, width):
                        if won(width):
                            print ("won")
                            break

                        board = remap_board(clicked, board, height, width)
                        print_board(board)

                    else:
                        print("Brute-forcing")
                        frontier = extract_frontier(board, height, width)
                        constraints = extract_constraints(board, frontier, height, width)
                            
                        if not brute_force(frontier, constraints):
                            print("Can't solve more.")
                            restart_game(width, "forced")
                            break
                            
                        board = remap_board(clicked, board, height, width)
                
                    restart_game(width, "not")

            restart_game(width, "not")

            if stop:
                print("Stopped")
                break
