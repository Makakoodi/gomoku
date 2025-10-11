import random
import pisqpipe as pp
import re
from pisqpipe import DEBUG_EVAL, DEBUG

MAX_BOARD = 100
board = [[0 for _ in range(MAX_BOARD)] for _ in range(MAX_BOARD)]

def brain_init():
    pp.pipeOut("DEBUG brain_init start")
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    init_candidate_moves()
    reset_bounds()
    pp.pipeOut("OK")
    pp.pipeOut("DEBUG brain_init OK")

def brain_restart():
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
    move_stack.clear()
    init_candidate_moves()
    reset_bounds()
    pp.pipeOut("OK")

def isFree(x, y):
    return 0 <= x < pp.width and 0 <= y < pp.height and board[x][y] == 0

EMPTY, ME, OPP = 0, 1, 2
RADIUS = 2
INF = 1_000_000_000

candidate_moves = []  # list
is_candidate = []
for i in range(MAX_BOARD):
    row = []
    for j in range(MAX_BOARD):
        row.append(False)
    is_candidate.append(row)

last_played = None
move_stack = []  

min_x = min_y = INF
max_x = max_y = -INF

def update_bounds(x, y):
    global min_x, min_y, max_x, max_y
    if x < min_x: min_x = x
    if x > max_x: max_x = x
    if y < min_y: min_y = y
    if y > max_y: max_y = y

def reset_bounds():
    global min_x, min_y, max_x, max_y
    min_x = min_y = INF
    max_x = max_y = -INF
    for x in range(pp.width):
        for y in range(pp.height):
            if board[x][y] != EMPTY:
                update_bounds(x, y)

def inside(x, y):
    return 0 <= x < pp.width and 0 <= y < pp.height

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

def add_candidate(x, y):
    if isFree(x, y) and not is_candidate[x][y]:
        is_candidate[x][y] = True
        candidate_moves.append((x, y))

def remove_candidate(x, y):
    if is_candidate[x][y]:
        is_candidate[x][y] = False
        for i, (cx, cy) in enumerate(candidate_moves):
            if cx == x and cy == y:
                candidate_moves.pop(i)
                break

def init_candidate_moves():
    candidate_moves.clear()    
    for x in range(pp.width):
        for y in range(pp.height):
            is_candidate[x][y] = False
    any_stone = False
    for xx in range(pp.width):
        for yy in range(pp.height):
            if board[xx][yy] != EMPTY:
                any_stone = True
                break
        if any_stone:
            break
    if not any_stone:
        mx, my = (pp.width // 2, pp.height // 2)
        add_candidate(mx, my)
    else:
        for xx in range(pp.width):
            for yy in range(pp.height):
                if board[xx][yy] != EMPTY:
                    for (nx, ny) in neighbors(xx, yy):
                        add_candidate(nx, ny)
        
        to_drop = []
        for (cx, cy) in candidate_moves:
            if board[cx][cy] != EMPTY:
                to_drop.append((cx, cy))
        for (cx, cy) in to_drop:
            remove_candidate(cx, cy)

def update_candidates_after_place(x, y):
    remove_candidate(x, y)
    for (xx, yy) in neighbors(x, y):
        add_candidate(xx, yy)

def update_candidates_after_takeback(x, y):
    near_stone = False
    for (xx, yy) in neighbors(x, y):
        if inside(xx, yy) and board[xx][yy] in (ME, OPP):
            near_stone = True
            break
    if near_stone and isFree(x, y):
        add_candidate(x, y)

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

def manhattan(a, b):
    ax, ay = a; bx, by = b
    return abs(ax - bx) + abs(ay - by)

def order_candidates(cands, last_move):
    if not cands:
        return []
    if last_move is None:
        center = (pp.width//2, pp.height//2)
        near, far = [], []
        for mv in cands:
            if manhattan(mv, center) <= 2:
                near.append(mv)
            else:
                far.append(mv)
        near.sort(key=lambda mv: manhattan(mv, center))
        return near + far

    lx, ly = last_move
    nset = set(neighbors(lx, ly, r=1))
    near, rest = [], []
    for mv in cands:
        if mv in nset:
            near.append(mv)
        else:
            rest.append(mv)
    return near + rest

def evaluate_area():
    if max_x < min_x or max_y < min_y:
        return 0
    weights = {0:0, 1:1, 2:10, 3:100, 4:1000, 5:100000}
    my_best = 0
    opp_best = 0
    sx = max(0, min_x - 2); ex = min(pp.width - 1, max_x + 2)
    sy = max(0, min_y - 2); ey = min(pp.height - 1, max_y + 2)
    for x in range(sx, ex+1):
        for y in range(sy, ey+1):           
            if board[x][y] not in (ME, OPP):
                continue
            who = board[x][y]
            for dx, dy in ((1,0),(0,1),(1,1),(1,-1)):
                bx, by = x - dx, y - dy
                if inside(bx, by) and board[bx][by] == who:
                    continue
                cnt = 0
                nx, ny = x, y
                while inside(nx, ny) and board[nx][ny] == who:
                    cnt += 1
                    nx += dx; ny += dy
                if who == ME:
                    if cnt > my_best: my_best = cnt
                else:
                    if cnt > opp_best: opp_best = cnt
    return weights.get(my_best, 100000) - weights.get(opp_best, 100000)

def _line_values(x, y, dx, dy, n=9):
    vals, coords = [], []
    for i in range(-n//2, n//2 + 1):
        xx, yy = x + i*dx, y + i*dy
        if inside(xx, yy):
            vals.append(board[xx][yy])
            coords.append((xx, yy))
        else:
            vals.append(3)
            coords.append((xx, yy))
    return vals, coords

def _encode(vals, who):
    return ''.join('1' if v == who else ('0' if v == 0 else ('3' if v == 3 else '2')) for v in vals)

#1 is our stone and 0 is empty cell
_OPEN4 = re.compile(r'011110')
_OPEN3 = re.compile(r'01110|010110')

def _collect_by_pattern(who):
    open4, open3 = set(), set()
    for x, y in candidate_moves:
        if pp.terminateAI:
            break
        for dx, dy in ((1,0),(0,1),(1,1),(1,-1)):
            if pp.terminateAI:
                break
            vals, coords = _line_values(x, y, dx, dy, n=9)
            for i, (cx, cy) in enumerate(coords):
                if cx == x and cy == y and vals[i] == EMPTY:
                    vals[i] = who
                    break
            s = _encode(vals, who)
            if '11111' in s or _OPEN4.search(s):
                open4.add((x, y))
            elif _OPEN3.search(s):
                open3.add((x, y))
    return open4, open3

def _collect_critical_blocks(who_targets):
    crit = set()
    for x, y in candidate_moves:
        if pp.terminateAI:
            break
        for dx, dy in ((1,0),(0,1),(1,1),(1,-1)):
            if pp.terminateAI:
                break
            vals, coords = _line_values(x, y, dx, dy, n=9)

            for i, (cx, cy) in enumerate(coords):
                if cx == x and cy == y and vals[i] == EMPTY:
                    vals[i] = who_targets
                    break

            s = _encode(vals, who_targets)

            if '11111' in s or _OPEN4.search(s):
                crit.add((x, y))
                continue

            if _OPEN3.search(s):
                crit.add((x, y))
    return crit

def _sort_pref(moves, ref=None):
    if not moves:
        return []
    if ref is None:
        ref = (pp.width // 2, pp.height // 2)
    return sorted(moves, key=lambda mv: manhattan(mv, ref))

def _cap_candidates(cands, ref=None, cap=60):
    if len(cands) <= cap:
        return cands
    return _sort_pref(cands, ref)[:cap]

def tactical_move():
    if pp.terminateAI:
        return None
    mv = immediate_tactic(last_move=None)
    if mv is not None or pp.terminateAI:
        return mv

    me4, me3 = _collect_by_pattern(ME)
    if pp.terminateAI:
        return None
    op4, op3 = _collect_by_pattern(OPP)
    if pp.terminateAI:
        return None
    ref = last_played if last_played is not None else (pp.width // 2, pp.height // 2)

    for m in _sort_pref(op4, ref):
        return m
    for m in _sort_pref(me4, ref):
        return m
    for m in _sort_pref(op3, ref):
        return m
    for m in _sort_pref(me3, ref):
        return m

    return None

def alphabeta(depth, alpha, beta, is_max, candidates, last_move):    
    if depth == 0 or pp.terminateAI:
        return evaluate_area(), None
    if not candidates:
        return 0, None

    ordered = order_candidates(candidates, last_move)
    WIN_SCORE = 100000

    if is_max:
        best_move = None
        for (mx, my) in ordered:
            if pp.terminateAI:
                break
            board[mx][my] = ME
            update_bounds(mx, my)

            if check_five(mx, my, ME):
                board[mx][my] = EMPTY
                reset_bounds()
                return WIN_SCORE, (mx, my)

            child_cands = build_child_candidates(candidates, (mx, my))
            score, _ = alphabeta(depth-1, alpha, beta, False, child_cands, (mx, my))

            board[mx][my] = EMPTY
            reset_bounds()

            if score > alpha:
                alpha = score
                best_move = (mx, my)

            if beta <= alpha:
                break
        return alpha, best_move

    else:
        best_move = None
        for (mx, my) in ordered:
            if pp.terminateAI:
                break
            board[mx][my] = OPP
            update_bounds(mx, my)
           
            if check_five(mx, my, OPP):
                board[mx][my] = EMPTY
                reset_bounds()
                return -WIN_SCORE, (mx, my)

            child_cands = build_child_candidates(candidates, (mx, my))
            score, _ = alphabeta(depth-1, alpha, beta, True, child_cands, (mx, my))

            board[mx][my] = EMPTY
            reset_bounds()

            if score < beta:
                beta = score
                best_move = (mx, my)

            if beta <= alpha:
                break
        return beta, best_move

def build_child_candidates(cands, played_xy):
    child = list(cands)
    if played_xy in child:
        child.remove(played_xy)
    px, py = played_xy
    for (nx, ny) in neighbors(px, py):
        if isFree(nx, ny) and (nx, ny) not in child:
            child.append((nx, ny))
    return child

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

def choose_move(depth=3, last_move=None):
    #chooses the best move, tactic first then alpha beta
    if not candidate_moves:
        return (pp.width // 2, pp.height // 2)

    mv = tactical_move()
    if mv is not None:
        return mv

    if pp.terminateAI:
        ref = last_move if last_move else (pp.width//2, pp.height//2)
        for (x, y) in _sort_pref(candidate_moves, ref):
            if isFree(x, y):
                return (x, y)
        for x in range(pp.width):
            for y in range(pp.height):
                if isFree(x, y):
                    return (x, y)
        return (0, 0)

    base = order_candidates(candidate_moves, last_move)

    me4, me3 = _collect_by_pattern(ME)
    op4, op3 = _collect_by_pattern(OPP)
    threat_first = list(dict.fromkeys(
        _sort_pref(op4, last_move) +
        _sort_pref(me4, last_move) +
        _sort_pref(op3, last_move) +
        _sort_pref(me3, last_move) +
        base
    ))

    ref = last_move if last_move else (pp.width//2, pp.height//2)
    threat_first = _cap_candidates(threat_first, ref, cap=60)

    if pp.terminateAI:
        for (x, y) in threat_first:
            if isFree(x, y):
                return (x, y)
        return (pp.width // 2, pp.height // 2)

    score, mv = alphabeta(depth, -INF, INF, True, threat_first, last_move)
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
        move_stack.append((x, y, ME))
        update_candidates_after_place(x, y)
        update_bounds(x, y)
        global last_played
        last_played = (x, y)
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
    if isFree(x,y):
        board[x][y] = OPP
        move_stack.append((x, y, OPP))
        update_candidates_after_place(x, y)
        update_bounds(x, y)
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
    if 0 <= x < pp.width and 0 <= y < pp.height and board[x][y] != 0:
        board[x][y] = 0
        update_candidates_after_takeback(x, y)
        if move_stack and move_stack[-1][0] == x and move_stack[-1][1] == y:
            move_stack.pop()
        global last_played
        last_played = (move_stack[-1][0], move_stack[-1][1]) if move_stack else None
        reset_bounds()
        return 0
    return 2

def brain_turn():
    if pp.terminateAI:
        return
    if not candidate_moves:
        init_candidate_moves()
    pp.pipeOut(f"DEBUG candidates={len(candidate_moves)}")
    x, y = choose_move(depth=3, last_move=last_played) 
    pp.pipeOut(f"DEBUG move=({x},{y})")
    if not isFree(x, y):        
        placed = False
        for xx in range(pp.width):
            for yy in range(pp.height):
                if isFree(xx, yy):
                    x, y = xx, yy
                    placed = True
                    break
            if placed:
                break
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
