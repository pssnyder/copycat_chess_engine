"""Pure Python UCI smoke test for Copycat Chess Engine.

Avoids using the batch script / stdin piping so it works in shells
where .bat invocation is unreliable (e.g., bash on Windows inside VS Code).

This test directly instantiates the CopycatUCI interface and calls the
methods that would normally be triggered by UCI textual commands.

It validates that:
 1. Identification outputs contain name/author.
 2. Engine reports ready.
 3. A simple position can be set.
 4. A best move is produced for a shallow search (depth 1 or provided depth).

If anything fundamental is broken, assertions will fail, giving fast feedback
before building an executable.
"""

import io
import re
import sys
import os
from contextlib import redirect_stdout

# Ensure we can import from src/core when running as a module
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
SRC_DIR = os.path.join(REPO_ROOT, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from core.uci_interface import CopycatUCI


def run_and_capture(fn, *args, **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn(*args, **kwargs)
    return buf.getvalue()


def test_uci_basic_identification():
    uci = CopycatUCI()
    out = run_and_capture(uci.uci)  # Call identification
    assert "id name" in out.lower(), f"Expected name line, got: {out}"
    assert "id author" in out.lower(), f"Expected author line, got: {out}"
    assert "uciok" in out.lower(), f"Expected uciok terminator, got: {out}"


def test_uci_isready():
    uci = CopycatUCI()
    out = run_and_capture(uci.isready)
    assert out.strip() == "readyok"


def test_uci_position_and_go_depth():
    uci = CopycatUCI()
    # Simulate: ucinewgame, position startpos moves e2e4 e7e5, go depth 1
    uci.ucinewgame()
    # Position command parsing logic is inside position(); supply tokenized args
    uci.position(["startpos", "moves", "e2e4", "e7e5"])
    # Request a very shallow search for speed/stability in CI
    out = run_and_capture(uci.go, ["depth", "1"])
    # Expect a bestmove line
    assert re.search(r"bestmove\s+[a-h][1-8][a-h][1-8][qrbn]?", out), f"No valid bestmove in output: {out}"


if __name__ == "__main__":  # Optional manual quick run
    failures = 0
    for fn in [
        test_uci_basic_identification,
        test_uci_isready,
        test_uci_position_and_go_depth,
    ]:
        try:
            fn()
            print(f"[PASS] {fn.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"[FAIL] {fn.__name__}: {e}", file=sys.stderr)
    if failures:
        sys.exit(1)
    print("All UCI smoke tests passed.")
