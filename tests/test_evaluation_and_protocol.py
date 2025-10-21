def test_evaluate_area_monotonic(real_pp, clear_board):
    pp, ai, moves, outs = real_pp
    clear_board(ai)
    for x in [5,6]:
        ai.board[x][7] = ai.ME; ai.update_bounds(x,7)
    ai.init_candidate_moves()
    v2 = ai.evaluate_area()

    ai.board[7][7] = ai.ME; ai.update_bounds(7,7)
    ai.init_candidate_moves()
    v3 = ai.evaluate_area()

    ai.board[8][7] = ai.ME; ai.update_bounds(8,7)
    ai.init_candidate_moves()
    v4 = ai.evaluate_area()

    assert v2 < v3 < v4

def test_protocol_like_begin_turn(real_pp):
    pp, ai, moves, outs = real_pp
    start_len = len(moves)
    ai.brain_turn()
    assert len(moves) == start_len + 1
    x, y = moves[-1]    
    assert 0 <= x < pp.width and 0 <= y < pp.height
