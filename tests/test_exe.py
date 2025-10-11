import os
import re
import subprocess
import time

#points to exe
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXE = os.path.join(ROOT, "pbrain", "pbrain-mybrain.exe")  # adjust name if different
EXE_DIR = os.path.dirname(EXE)

MOVE_RE = re.compile(r"^\s*(\d+)\s*,\s*(\d+)\s*$")

def start_brain():
    return subprocess.Popen(
        [EXE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=EXE_DIR,
    )

def send(p: subprocess.Popen, line: str):
    assert p.stdin is not None
    p.stdin.write(line + "\n")
    p.stdin.flush()

def read_until(p: subprocess.Popen, predicate, timeout=3.0):
    assert p.stdout is not None
    deadline = time.time() + timeout
    lines = []
    while time.time() < deadline:
        line = p.stdout.readline()
        if not line:
            time.sleep(0.01)
            continue
        s = line.strip()
        lines.append(s)
        if predicate(s):
            return s, lines
    return None, lines

def is_ok(line: str) -> bool:
    return line == "OK"

def is_move(line: str) -> bool:
    return MOVE_RE.match(line) is not None

def test_protocol_begin_center():
    p = start_brain()

    try:
        send(p, "START 15")
        matched, lines = read_until(p, is_ok, timeout=3.0)
        assert matched == "OK", f"Expected OK after START, got: {lines}"
        send(p, "BEGIN")
        matched, lines2 = read_until(p, is_move, timeout=3.0)
        assert matched is not None, f"No move after BEGIN. Output:\n{lines + lines2}"
        assert is_move(matched), f"Unexpected move format: {matched}"
        send(p, "END")

    finally:
        try:
            p.terminate()
        except Exception:
            pass
