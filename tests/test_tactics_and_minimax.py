def test_immediate_win_me(real_pp, clear_board):
    pp, ai, moves, outs = real_pp
    clear_board(ai)
    for x in [8,9,10,11]:
        ai.board[x][8] = ai.ME
        ai.update_bounds(x,8)
    ai.init_candidate_moves()
    mv = ai.choose_move(depth=3, last_move=(11,8))
    assert mv in [(12,8),(7,8)]

def test_block_opponent_open_four(real_pp, clear_board):
    pp, ai, moves, outs = real_pp
    clear_board(ai)
    for x in [8,9,10,11]:
        ai.board[x][10] = ai.OPP
        ai.update_bounds(x,10)
    ai.init_candidate_moves()
    mv = ai.choose_move(depth=3, last_move=(11,10))
    assert mv in [(12,10),(7,10)]

def test_minimax_prefers_win_over_adjacent(real_pp, clear_board):
    pp, ai, moves, outs = real_pp
    clear_board(ai)
    for x in [8,9,10,11]:
        ai.board[x][5] = ai.ME if x!=8 else ai.EMPTY
    ai.board[8][5] = ai.ME
    for x in [8,9,10,11]:
        ai.update_bounds(x,5)
    ai.init_candidate_moves()
    mv = ai.choose_move(depth=3, last_move=(10,5))
    assert mv in [(7,5),(11,5)]
