#!/usr/bin/env python3
"""HPSv3 — human preference score for (image, prompt), as the aesthetic half of the reward.

    python3 hps.py out/ladder/*.png          # print scores, highest first

Run 2 produced structurally correct bicycles in bare ink: colours per sketch fell 3.6 -> 0.9
and brush.fill from 115/128 to 4/128, because every component of that reward was structural
and nothing paid for paint. This is the component that pays for it.

HPSv3 is a 7B Qwen2-VL with a RankNet head, ~16 GB in bf16 — it fits alongside the 72B judge
during the scoring phase (46 + 16 = 62 GB) but not alongside training, which is why the loop
already swaps models between phases.

Scores are unbounded reals, not 0..1: calibrate against the ladder before weighting them.
"""
import argparse, json, os, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).parent
# hpsv3 pins torch 2.5 and pulls vLLM back to 0.7, which cannot serve Qwen2.5-VL — so it
# lives in its own venv and we talk to it over a pipe. HPS_PYTHON points at that interpreter.
HPS_PYTHON = os.environ.get("HPS_PYTHON", str(pathlib.Path.home() / "hpsenv/bin/python"))
_PROC = None


def _worker():
    global _PROC
    if _PROC is None or _PROC.poll() is not None:
        # stderr is left attached to ours: the worker's chatter is visible but out of the
        # protocol, and a crash shows up as output rather than a silent hang
        _PROC = subprocess.Popen([HPS_PYTHON, str(HERE / "hps_worker.py")],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                                 env={**os.environ, "MPLCONFIGDIR": "/tmp/mpl"})
    return _PROC


def score(paths, prompt=None):
    """mu for each image. The prompt matters — HPS scores (image, prompt) alignment as well
    as quality, which is why it can reward 'looks like the bicycle we asked for'."""
    # absolute: hpsv3 opens the path itself and does not resolve it against our cwd
    paths = [str(pathlib.Path(p).resolve()) for p in paths]
    prompt = prompt or (HERE / "prompt/user.txt").read_text().strip()
    if not paths:
        return []
    # chunk: HPSv3 is a Qwen2-VL and a 700x700 sketch becomes a lot of visual tokens, so a
    # ten-image call allocated 78GB and died. Four at a time is comfortable on an 80GB card.
    batch = int(os.environ.get("HPS_BATCH", "4"))
    out = []
    w = _worker()
    for i in range(0, len(paths), batch):
        w.stdin.write(json.dumps({"paths": paths[i:i + batch], "prompt": prompt}) + "\n")
        w.stdin.flush()
        line = w.stdout.readline()
        if not line:
            raise RuntimeError(f"hps worker died — check {HPS_PYTHON} and hpsv3 install")
        reply = json.loads(line)
        if "error" in reply:
            raise RuntimeError("hps worker: " + reply["error"])
        out += reply["scores"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+", type=pathlib.Path)
    ap.add_argument("--prompt")
    a = ap.parse_args()
    s = score(a.images, a.prompt)
    for path, v in sorted(zip(a.images, s), key=lambda t: -t[1]):
        print(f"  {v:8.3f}  {path.name}")


if __name__ == "__main__":
    main()
