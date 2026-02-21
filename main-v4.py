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
             (221, 170, 34),    # 5
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
            print("Need reread, oops")
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

    return (r + g + b) < 100

# did we win chat?
def won(width):
    dx = int((2 * TILES_X_START + width * GRID_OFFSET + 0.5) / 2) 
    dy = 330
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
        
        if restart_game(width, "not") or dist_to_colors(pyautogui.pixel(dx + 5, dy + 5), LOST) <= 18 :
            print("Bad choice i guess?")
            return False
        
        if num == 0:
            break

        print(f"Clicked, found {num}. Continuing")
    
    print("My job here is done, good luck")
    return True

# valid neighbour
def iter_neighbors(dy, dx, height, width):
    for y in (-1, 0, 1):
        for x in (-1, 0, 1):
            # skip itself
            if y == 0 and x == 0:
                continue

            ny, nx = dy + y, dx + x
            
            if 0 <= ny < height and 0 <= nx < width:
                yield ny, nx

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
def iter_neighbors(dy, dx, height, width):
    for y in (-1, 0, 1):
        for x in (-1, 0, 1):
            if y == 0 and x == 0:
                continue

            ny, nx = dy + y, dx + x

            if 0 <= ny < height and 0 <= nx < width:
                yield ny, nx

def extract_frontier(board, height, width):
    frontier = []

    for dy in range(height):
        for dx in range(width):
            if board[dy][dx] != UNKNOWN:
                continue

            for ny, nx in iter_neighbors(dy, dx, height, width):
                if 1 <= board[ny][nx] < 9:
                    frontier.append((dy, dx))
                    break

    return frontier

def extract_constraints(board, frontier, height, width):
    index_map = {cell: i for i, cell in enumerate(frontier)}
    constraints = []

    for dy in range(height):
        for dx in range(width):
            if not (1 <= board[dy][dx] < 9):
                continue

            unknown_indices = []
            known_mines = 0

            for ny, nx in iter_neighbors(dy, dx, height, width):
                if board[ny][nx] == UNKNOWN and (ny, nx) in index_map:
                    unknown_indices.append(index_map[(ny, nx)])

                elif board[ny][nx] == MINE:
                    known_mines += 1

            if unknown_indices:
                remaining = board[dy][dx] - known_mines
                constraints.append((unknown_indices, remaining))

    return constraints

def split_into_regions(frontier, constraints):
    n = len(frontier)

    # build adj list for frontier indixes
    adjacency = {i: set() for i in range(n)}

    for indices, _ in constraints:
        for i in indices:
            for j in indices:
                if i != j:
                    adjacency[i].add(j)

    visited = set()
    regions = []

    # find connected
    for i in range(n):
        if i in visited:
            continue

        stack = [i]
        component = set()

        while stack:
            node = stack.pop()
            if node in visited:
                continue

            visited.add(node)
            component.add(node)

            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    stack.append(neighbor)

        regions.append(component)

    # build smaller regions
    region_data = []

    for component in regions:
        component = list(component)

        # map old indixes to new local indixes
        local_index = {old_i: new_i for new_i, old_i in enumerate(component)}

        local_frontier = [frontier[i] for i in component]
        local_constraints = []

        for indices, remaining in constraints:
            filtered = [local_index[i] for i in indices if i in local_index]
            if filtered:
                local_constraints.append((filtered, remaining))

        region_data.append((local_frontier, local_constraints))

    return region_data

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
    n = len(frontier)

    if n == 0:
        return False

    state = [0] * n
    valid_states = []

    print(1 << n)

    for _ in range(1 << n):
        valid = True

        for indices, remaining in constraints:
            if sum(state[i] for i in indices) != remaining:
                valid = False
                break

        if valid:
            valid_states.append(state.copy())

        increment_binary_once(state)

    if not valid_states:
        return False

    actions = []

    for i in range(n):
        mine_count = sum(s[i] for s in valid_states)

        if mine_count == 0:
            actions.append((*frontier[i], "left"))

        elif mine_count == len(valid_states):
            actions.append((*frontier[i], "right"))

    if not actions:
        return False

    print("Have possible")
    click(actions)
    return True

# probability
def probability_guess(frontier, constraints):
    length_frontier = len(frontier)
    state = [0] * length_frontier
    valid_states = []

    for _ in range(2 ** length_frontier):
        valid = True

        for indexes, remaining in constraints:
            assume = 0
            for idx in indexes:
                assume += state[idx]

            if assume != remaining:
                valid = False
                break

        if valid:
            valid_states.append(state.copy())

        state = increment_binary_once(state)

    if not valid_states:
        return False

    # compute probability
    probabilities = []

    for i in range(length_frontier):
        mine_count = 0
        for s in valid_states:
            mine_count += s[i]

        prob = mine_count / len(valid_states)
        probabilities.append(prob)

    # choose lowest probability
    best_index = probabilities.index(min(probabilities))
    y, x = frontier[best_index]

    print(f"Guessing with probability {probabilities[best_index]:.3f}")

    click([(y, x, "left")])
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
def play_one_game(height, width):
    if not initial_clicking(height, width):
        return  # failed to click

    board = read_board(height, width)
    print_board(board)

    while True:

        if won(width):
            print("Won")
            return

        # rule based
        if solver(board, height, width):
            board = remap_board(clicked, board, height, width)
            print_board(board)
            print("Solving\n")
            continue

        # brute
        print("Breaking locks")

        frontier = extract_frontier(board, height, width)
        if not frontier:
            print("Nu frontier")
            return

        constraints = extract_constraints(board, frontier, height, width)
        regions = split_into_regions(frontier, constraints)

        any_action = False

        for local_frontier, local_constraints in regions:
            if brute_force(local_frontier, local_constraints):
                any_action = True

        # probability
        if not any_action:
            print("We gamble naw")

            guessed = False

            for local_frontier, local_constraints in regions:
                if probability_guess(local_frontier, local_constraints):
                    guessed = True
                    break

            if not guessed:
                print("No valid states\n")
                return
            
            if lost(width):
                return

        board = remap_board(clicked, board, height, width)
        print_board(board)
        print("Solving\n")

if __name__ == "__main__":
    height, width = detect_board_size()

    while True:
        play_one_game(height, width)
        restart_game(width, "not")