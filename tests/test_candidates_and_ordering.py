def test_candidate_maintenance(real_pp):
    pp, ai, moves, outs = real_pp
    cx, cy = pp.width//2, pp.height//2
    ai.brain_my(cx, cy)
    assert (cx, cy) not in ai.candidate_moves
    neigh = set(ai.neighbors(cx, cy, r=ai.RADIUS))
    for n in neigh:
        x,y = n
        if ai.isFree(x,y):
            assert n in ai.candidate_moves

def test_ordering_neighbors_first(real_pp):
    pp, ai, moves, outs = real_pp
    ai.brain_opponents(10,10)
    base = list(ai.candidate_moves)
    ordered = ai.order_candidates(base, last_move=(10,10))
    near = set(ai.neighbors(10,10, r=1))
    head = ordered[:6]
    assert any(m in near for m in head)

def test_build_child_candidates(real_pp):
    pp, ai, moves, outs = real_pp
    cx, cy = pp.width//2, pp.height//2
    ai.brain_my(cx, cy)
    parent = list(ai.candidate_moves)
    child = ai.build_child_candidates(parent, (cx,cy))
    assert (cx,cy) not in child
    for n in ai.neighbors(cx,cy):
        if ai.isFree(*n):
            assert n in child
