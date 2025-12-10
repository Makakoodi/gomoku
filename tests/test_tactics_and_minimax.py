WIN_SCORE = 100000
WIN_THRESHOLD = 900

#AI should play the immediate winning move when four-in-a-row exists.
def test_immediate_win_me(real_pp, clear_board):
    pp, ai, moves, outs = real_pp
    clear_board(ai)

    for x in [8, 9, 10, 11]:
        ai.board[x][8] = ai.ME
        ai.update_bounds(x, 8)

    ai.init_candidate_moves()
    mv = ai.choose_move(depth=3, last_move=(11, 8))

    assert mv in [(12, 8), (7, 8)]

#AI should block the opponent's open four immediately.
def test_block_opponent_open_four(real_pp, clear_board):
    pp, ai, moves, outs = real_pp
    clear_board(ai)

    for x in [8, 9, 10, 11]:
        ai.board[x][10] = ai.OPP
        ai.update_bounds(x, 10)

    ai.init_candidate_moves()
    mv = ai.choose_move(depth=3, last_move=(11, 10))

    assert mv in [(12, 10), (7, 10)]

#AI should prefer a winning move over just a good adjacent move.
def test_minimax_prefers_win_over_adjacent(real_pp, clear_board):
    pp, ai, moves, outs = real_pp
    clear_board(ai)

    for x in [8, 9, 10, 11]:
        ai.board[x][5] = ai.ME if x != 8 else ai.EMPTY
    ai.board[8][5] = ai.ME

    for x in [8, 9, 10, 11]:
        ai.update_bounds(x, 5)

    ai.init_candidate_moves()
    mv = ai.choose_move(depth=3, last_move=(10, 5))

    assert mv in [(7, 5), (11, 5)]

#Creates a strong attacking cross-shape for "ME".
def _setup_forced_win_cross(ai):
    coords = [(9, 10), (10, 10), (11, 10), (10, 9), (10, 11)]
    for (x, y) in coords:
        ai.board[x][y] = ai.ME
        ai.update_bounds(x, y)

#Returns limited nearby candidates to keep the test search relatively mall.
def _cross_base_candidates(ai):
    around = [
        (8, 10), (12, 10),
        (10, 8), (10, 12),
        (9, 9), (11, 9),
        (9, 11), (11, 11),
    ]
    return [(x, y) for (x, y) in around if ai.board[x][y] == ai.EMPTY]

#Minimax should evaluate the root position as winning at depth 5.
def test_minimax_forced_win_depth5_root_sees_win(real_pp, clear_board, monkeypatch):
    pp, ai, moves, outs = real_pp
    clear_board(ai)
    _setup_forced_win_cross(ai)

    base_candidates = _cross_base_candidates(ai)

    def limited_child_candidates(cands, played_xy):
        return [(x, y) for (x, y) in base_candidates if (x, y) != played_xy and ai.board[x][y] == ai.EMPTY]

    monkeypatch.setattr(ai, "build_child_candidates", limited_child_candidates)

    score, best_move = ai.alphabeta(5, -ai.INF, ai.INF, True, list(base_candidates), None)

    assert score >= WIN_THRESHOLD
    assert best_move in base_candidates

#Minimax should maintain a winning evaluation across multiple ME turns.
def test_minimax_forced_win_depth5_every_step_sees_win(real_pp, clear_board, monkeypatch):
    pp, ai, moves, outs = real_pp
    clear_board(ai)
    _setup_forced_win_cross(ai)

    base_candidates = _cross_base_candidates(ai)

    def limited_child_candidates(cands, played_xy):
        return [(x, y) for (x, y) in base_candidates if (x, y) != played_xy and ai.board[x][y] == ai.EMPTY]

    monkeypatch.setattr(ai, "build_child_candidates", limited_child_candidates)

    last_move = None

    # ME first move
    score1, mv1 = ai.alphabeta(5, -ai.INF, ai.INF, True, list(base_candidates), last_move)
    assert score1 >= WIN_THRESHOLD
    assert mv1 in base_candidates

    x1, y1 = mv1
    ai.board[x1][y1] = ai.ME
    ai.update_bounds(x1, y1)
    ai.update_candidates_after_place(x1, y1)
    last_move = mv1

    # Opponent reply
    score_opp, mv_opp = ai.alphabeta(5, -ai.INF, ai.INF, False, list(base_candidates), last_move)
    ox, oy = mv_opp
    ai.board[ox][oy] = ai.OPP
    ai.update_bounds(ox, oy)
    ai.update_candidates_after_place(ox, oy)
    last_move = mv_opp

    # ME second move
    score2, mv2 = ai.alphabeta(5, -ai.INF, ai.INF, True, list(base_candidates), last_move)
    assert score2 >= WIN_THRESHOLD
    assert mv2 in base_candidates

    x2, y2 = mv2
    ai.board[x2][y2] = ai.ME
    ai.update_bounds(x2, y2)
    ai.update_candidates_after_place(x2, y2)
