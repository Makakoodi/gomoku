import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]

def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    init_candidate_moves()
    pp.pipeOut("OK")

def brain_restart():
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
    init_candidate_moves()
    pp.pipeOut("OK")

def isFree(x, y):
    return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0



EMPTY, ME, OPP = 0, 1, 2
RADIUS = 2
candidate_moves = set()
last_played = None

# return true if x y is inside the board
def inside(x, y):
    return 0 <= x < pp.width and 0 <= y < pp.height

# get the cells around x y within r radius
def neighbors(x, y, r=RADIUS):
    out = []
    for dx in range(-r, r+1):
        for dy in range(-r, r+1):
            if dx == 0 and dy == 0:
                continue
            xx, yy = x+dx, y+dy
            if inside(xx, yy):
                out.append((xx, yy))
    return out

# init candidate moves set
def init_candidate_moves():
    candidate_moves.clear()
    any_stone = False
    for xx in range(pp.width):
        for yy in range(pp.height):
            if board[xx][yy] != EMPTY:
                any_stone = True
                break
        if any_stone:
            break
    if not any_stone:
        mid = (pp.width // 2, pp.height // 2)
        candidate_moves.add(mid)
    else:
        for xx in range(pp.width):
            for yy in range(pp.height):
                if board[xx][yy] != EMPTY:
                    update_candidates_after_place(xx, yy)
    to_drop = {(cx, cy) for (cx, cy) in candidate_moves if board[cx][cy] != EMPTY}
    candidate_moves.difference_update(to_drop)

def update_candidates_after_place(x, y):
    candidate_moves.discard((x, y))
    for (xx, yy) in neighbors(x, y):
        if isFree(xx, yy):
            candidate_moves.add((xx, yy))

# for piskvork manager if we use the takeback command
def update_candidates_after_takeback(x, y):
    near_stone = False
    for (xx, yy) in neighbors(x, y):
        if inside(xx, yy) and board[xx][yy] in (ME, OPP):
            near_stone = True
            break
    if near_stone and isFree(x, y):
        candidate_moves.add((x, y))

# check if we have five in a row vertically, diagonally and horizontally
def check_five(x, y, who):
    for dx, dy in ((1,0),(0,1),(1,1),(1,-1)):
        c = 1
        xx, yy = x+dx, y+dy
        while inside(xx,yy) and board[xx][yy] == who:
            c += 1; xx += dx; yy += dy
        xx, yy = x-dx, y-dy
        while inside(xx,yy) and board[xx][yy] == who:
            c += 1; xx -= dx; yy -= dy
        if c >= 5:
            return True
    return False

# check distance from a to b
def manhattan(a, b):
    ax, ay = a; bx, by = b
    return abs(ax - bx) + abs(ay - by)

# we prio the neighbors of the last move before moving onto other possibilities
def order_candidates(cands, last_move):
    cands_list = list(cands)
    if last_move is None:
        center = (pp.width//2, pp.height//2)
        cands_list.sort(key=lambda mv: manhattan(mv, center))
        return cands_list
    lx, ly = last_move
    near = set(neighbors(lx, ly, r=1))
    first = [m for m in cands_list if m in near]
    rest  = [m for m in cands_list if m not in near]
    return first + rest


# return the total length of the line through (x,y) for player 'who' in one direction
def line_len_from(x, y, dx, dy, who):
    count = 1
    # forward
    nx, ny = x + dx, y + dy
    while inside(nx, ny) and board[nx][ny] == who:
        count += 1
        nx += dx; ny += dy
    # backward
    nx, ny = x - dx, y - dy
    while inside(nx, ny) and board[nx][ny] == who:
        count += 1
        nx -= dx; ny -= dy
    return count

# heuristic that only looks at the 4 lines crossing 'last_move' (LOCAL evaluation)
def evaluate_local(last_move):
    if last_move is None:
        return 0
    lx, ly = last_move
    me_best = 0
    opp_best = 0
    for dx, dy in ((1,0),(0,1),(1,1),(1,-1)):
        me_best  = max(me_best,  line_len_from(lx, ly, dx, dy, ME))
        opp_best = max(opp_best, line_len_from(lx, ly, dx, dy, OPP))
    weights = {0:0, 1:1, 2:10, 3:100, 4:1000, 5:100000}
    return weights.get(me_best, 100000) - weights.get(opp_best, 100000)

# todo: alpha beta pruning
def minimax(depth, maximizing, cands, last_move):    
    if depth == 0 or pp.terminateAI:
        return evaluate_local(last_move), None
    
    if not cands:
        return 0, None
    ordered = order_candidates(cands, last_move)
    if maximizing:
        best_val, best_move = -10**9, None
        for (x, y) in ordered:
            board[x][y] = ME
            if check_five(x, y, ME):
                board[x][y] = EMPTY
                return 100000, (x, y)
            child_cands = set(cands)
            child_cands.discard((x, y))
            for (nx, ny) in neighbors(x, y):
                if isFree(nx, ny):
                    child_cands.add((nx, ny))
            
            val, _ = minimax(depth-1, False, child_cands, (x, y))
            board[x][y] = EMPTY
            if val > best_val:
                best_val, best_move = val, (x, y)
        return best_val, best_move
    else:
        best_val, best_move = 10**9, None
        for (x, y) in ordered:
            board[x][y] = OPP
            if check_five(x, y, OPP):
                board[x][y] = EMPTY
                return -100000, (x, y)
            child_cands = set(cands)
            child_cands.discard((x, y))
            for (nx, ny) in neighbors(x, y):
                if isFree(nx, ny):
                    child_cands.add((nx, ny))
            val, _ = minimax(depth-1, True, child_cands, (x, y))
            board[x][y] = EMPTY
            if val < best_val:
                best_val, best_move = val, (x, y)
        return best_val, best_move

def immediate_tactic(last_move=None):
    cand = order_candidates(candidate_moves, last_move)
    for (x, y) in cand:
        board[x][y] = ME
        if check_five(x, y, ME):
            board[x][y] = EMPTY
            return (x, y)
        board[x][y] = EMPTY
    for (x, y) in cand:
        board[x][y] = OPP
        if check_five(x, y, OPP):
            board[x][y] = EMPTY
            return (x, y)
        board[x][y] = EMPTY
    return None

def choose_move(depth=2, last_move=None):
    mv = immediate_tactic(last_move)
    if mv is not None:
        return mv
    cand = order_candidates(candidate_moves, last_move)
    score, mv = minimax(depth, True, set(cand), last_move)
    if mv is not None:
        return mv
    for x in range(pp.width):
        for y in range(pp.height):
            if board[x][y] == EMPTY:
                return (x, y)
    return (0, 0)

def brain_my(x, y):
    if isFree(x,y):
        board[x][y] = ME
        update_candidates_after_place(x, y)
        global last_played
        last_played = (x, y)
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
    if isFree(x,y):
        board[x][y] = OPP
        update_candidates_after_place(x, y)
        global last_played
        last_played = (x, y)
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
    if isFree(x,y):
        board[x][y] = 3
    else:
        pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
    if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
        board[x][y] = 0
        update_candidates_after_takeback(x, y)
        return 0
    return 2

def brain_turn():
    if pp.terminateAI:
        return
    x, y = choose_move(depth=2, last_move=last_played)
    #this loops the whole board backwards if we pick an occupied cell for some reason
    #(i dont know if this is agains the rules)
    if not isFree(x, y):
        found = False
        for xx in range(pp.width):
            for yy in range(pp.height):
                if isFree(xx, yy):
                    x, y = xx, yy
                    found = True
                    break
            if found: break
    pp.do_mymove(x, y)

def brain_end():
    pass

def brain_about():
    pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
    import win32gui
    def brain_eval(x, y):
        wnd = win32gui.GetForegroundWindow()
        dc = win32gui.GetDC(wnd)
        rc = win32gui.GetClientRect(wnd)
        c = str(board[x][y])
        win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
        win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################
"""
# define a file for logging ...
DEBUG_LOGFILE = "/tmp/pbrain-pyrandom.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
	pass

# define a function for writing messages to the file
def logDebug(msg):
	with open(DEBUG_LOGFILE,"a") as f:
		f.write(msg+"\n")
		f.flush()

# define a function to get exception traceback
def logTraceBack():
	import traceback
	with open(DEBUG_LOGFILE,"a") as f:
		traceback.print_exc(file=f)
		f.flush()
	raise

# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
def brain_turn():
	logDebug("some message 1")
	try:
		logDebug("some message 2")
		1. / 0. # some code raising an exception
		logDebug("some message 3") # not logged, as it is after error
	except:
		logTraceBack()
"""
######################################################################

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval

def main():
	pp.main()

if __name__ == "__main__":
	main()
