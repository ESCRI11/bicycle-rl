#!/usr/bin/env python3
"""Runs INSIDE the hpsv3 virtualenv. Reads {"paths": [...], "prompt": "..."} per line on
stdin, writes {"scores": [...]} per line on stdout — and *nothing else* on stdout.

hpsv3 pins torch 2.5 and drags vLLM to 0.7, which cannot serve Qwen2.5-VL, so it cannot
share an environment with the judge; a pipe is cheaper than resolving that fight. But the
library prints download bars and warnings to stdout, which corrupted the protocol: the first
read came back as a progress bar, not JSON. Everything the library says is redirected to
stderr, and the real stdout is held aside for replies only.
"""
import contextlib, json, os, sys

REPLY = os.fdopen(os.dup(sys.stdout.fileno()), "w")     # the only clean channel
os.dup2(sys.stderr.fileno(), sys.stdout.fileno())        # everything else goes to stderr
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")

with contextlib.redirect_stdout(sys.stderr):
    from hpsv3 import HPSv3RewardInferencer

_inf = None
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    try:
        with contextlib.redirect_stdout(sys.stderr):
            if _inf is None:
                _inf = HPSv3RewardInferencer(device="cuda")
            out = _inf.reward(req["paths"], [req["prompt"]] * len(req["paths"]))
            scores = [float(r[0].item()) for r in out]
        reply = {"scores": scores}
    except Exception as e:
        # answer with the error instead of dying: a dead worker gives the caller a blank
        # pipe and nothing to diagnose, which cost a round trip to find a missing file
        reply = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    REPLY.write(json.dumps(reply) + "\n")
    REPLY.flush()
