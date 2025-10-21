import sys
import os
import types
import importlib
import pytest

#we assume that pisqpipe.py and myBrain.py are in the pbrain folder
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PBRAIN_DIR = os.path.join(ROOT, "pbrain")
assert os.path.isdir(PBRAIN_DIR), f"Pbrain-dir not found at {PBRAIN_DIR}"
if PBRAIN_DIR not in sys.path:
    sys.path.insert(0, PBRAIN_DIR)

@pytest.fixture
def real_pp(monkeypatch):
    import pisqpipe as pp
    """
    we use pisqpipe.py with a monkeypatch on pipeOut and do_mymove so tests can read
    what happened
    """
    moves = []
    outs = []

    def patched_pipeOut(s: str):
        outs.append(s)
               
    def patched_do_mymove(x, y):
        moves.append((x, y))
        outs.append(f"{x},{y}")
    
    monkeypatch.setattr(pp, "pipeOut", patched_pipeOut, raising=True)
    monkeypatch.setattr(pp, "do_mymove", patched_do_mymove, raising=True)
    monkeypatch.setattr(pp, "width", 20, raising=True)
    monkeypatch.setattr(pp, "height", 20, raising=True)
    monkeypatch.setattr(pp, "terminateAI", False, raising=True)

    #load a clean myBrain
    import myBrain
    importlib.reload(myBrain)
    
    myBrain.brain_init()

    return pp, myBrain, moves, outs

@pytest.fixture
def clear_board():
    def _clear(ai):
        for x in range(ai.pp.width):
            for y in range(ai.pp.height):
                ai.board[x][y] = ai.EMPTY
        ai.move_stack.clear()
        ai.init_candidate_moves()
        ai.reset_bounds()
    return _clear
