#!/usr/bin/env python3
"""Runs INSIDE the hpsv3 virtualenv. Reads {"paths": [...], "prompt": "..."} on stdin,
writes {"scores": [...]} on stdout.

hpsv3 pins torch 2.5 and drags vLLM down to 0.7, which predates Qwen2.5-VL support and so
breaks the judge. The two cannot share an environment, and a subprocess boundary is cheaper
than resolving that fight.
"""
import json, sys

from hpsv3 import HPSv3RewardInferencer

_inf = None
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    if _inf is None:
        _inf = HPSv3RewardInferencer(device="cuda")
    out = _inf.reward(req["paths"], [req["prompt"]] * len(req["paths"]))
    print(json.dumps({"scores": [float(r[0].item()) for r in out]}), flush=True)
