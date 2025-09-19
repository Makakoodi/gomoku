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
	pp.pipeOut("OK")

def brain_restart():
	for x in range(pp.width):
		for y in range(pp.height):
			board[x][y] = 0
	pp.pipeOut("OK")

def isFree(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0



EMPTY, ME, OPP = 0, 1, 2
last_played = None  # (x, y) that tracks the last move

def inside(x, y):
	return 0 <= x < pp.width and 0 <= y < pp.height

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

def manhattan(a, b): ###distance from a to b for move_nearby function
	ax, ay = a; bx, by = b
	return abs(ax - bx) + abs(ay - by)

def moves_nearby(radius=1):
    any_stone = False
    for x in range(pp.width):
        for y in range(pp.height):
            if board[x][y] != EMPTY:
                any_stone = True
                break
        if any_stone:
            break
    
    if not any_stone:
        middle = pp.width // 2
        return [(middle, middle)]
    
    candidates = []
    for x in range(pp.width):
        for y in range(pp.height):
            if board[x][y] != EMPTY:                
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        xx = x + dx
                        yy = y + dy                        
                        if inside(xx, yy) and board[xx][yy] == EMPTY:
                            if (xx, yy) not in candidates:
                                candidates.append((xx, yy))
    
    if last_played is not None:
        target = last_played
    else:
        target = (pp.width // 2, pp.height // 2)
        
    def distance_from_target(move): #move had to be defined here
        return manhattan(move, target)
        
    candidates.sort(key=distance_from_target)
    
    if not candidates:
        for x in range(pp.width):
            for y in range(pp.height):
                if board[x][y] == EMPTY:
                    candidates.append((x, y))

    return candidates

def longest_run_for(who):
	best = 0
	for x in range(pp.width):
		for y in range(pp.height):
			if board[x][y] != who:
				continue
			for dx, dy in ((1,0),(0,1),(1,1),(1,-1)):
				c = 1
				xx, yy = x+dx, y+dy
				while inside(xx,yy) and board[xx][yy] == who:
					c += 1; xx += dx; yy += dy
				xx, yy = x-dx, y-dy
				while inside(xx,yy) and board[xx][yy] == who:
					c += 1; xx -= dx; yy -= dy
				if c > best:
					best = c
	return best

def evaluate():
	w = {0:0, 1:1, 2:10, 3:100, 4:1000, 5:100000}
	return w[longest_run_for(ME)] - w[longest_run_for(OPP)]

def minimax(depth, maximizing):
	if depth == 0 or pp.terminateAI:
		return evaluate(), None
	moves = moves_nearby()
	if not moves:
		return 0, None
	if maximizing:
		best_val, best_move = -10**9, None
		for (x,y) in moves:
			board[x][y] = ME
			if check_five(x,y,ME):
				board[x][y] = EMPTY
				return 100000, (x,y)
			val, _ = minimax(depth-1, False)
			board[x][y] = EMPTY
			if val > best_val:
				best_val, best_move = val, (x,y)
		return best_val, best_move
	else:
		best_val, best_move = 10**9, None
		for (x,y) in moves:
			board[x][y] = OPP
			if check_five(x,y,OPP):
				board[x][y] = EMPTY
				return -100000, (x,y)
			val, _ = minimax(depth-1, True)
			board[x][y] = EMPTY
			if val < best_val:
				best_val, best_move = val, (x,y)
		return best_val, best_move

def immediate_tactic():
	cand = moves_nearby()
	for (x,y) in cand:
		board[x][y] = ME
		if check_five(x,y,ME):
			board[x][y] = EMPTY
			return (x,y)
		board[x][y] = EMPTY
	for (x,y) in cand:
		board[x][y] = OPP
		if check_five(x,y,OPP):
			board[x][y] = EMPTY
			return (x,y)
		board[x][y] = EMPTY
	return None

def choose_move(depth=2):
	move = immediate_tactic()
	if move is not None:
		return move
	score, move = minimax(depth, True)
	if move is not None:
		return move
	for x in range(pp.width):
		for y in range(pp.height):
			if board[x][y] == EMPTY:
				return (x,y)
	return (0,0)



def brain_my(x, y):
	if isFree(x,y):
		board[x][y] = 1
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	if isFree(x,y):
		board[x][y] = 2
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
		return 0
	return 2

def brain_turn():
	if pp.terminateAI:
		return
	# we use the minimax here
	x, y = choose_move(depth=2)
	

	# this is in case it tries to play an invalid move, 
	# and will just play the first available spot from left to right to make a legal move
	if not isFree(x, y):
		for xx in range(pp.width):
			for yy in range(pp.height):
				if isFree(xx, yy):
					x, y = xx, yy
					break
	
	pp.do_mymove(x, y)

def brain_end():
	pass

def brain_about():
	pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
	import win32gui
	def brain_eval(x, y):
		# TODO check if it works as expected
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
