def test_init_adds_center_candidate(real_pp):
    pp, ai, moves, outs = real_pp
    mv = ai.choose_move(depth=3, last_move=None)
    cx, cy = pp.width // 2, pp.height // 2
    assert mv == (cx, cy)
