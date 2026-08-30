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
import argparse, pathlib, sys

_INFERENCER = None


def scorer():
    global _INFERENCER
    if _INFERENCER is None:
        from hpsv3 import HPSv3RewardInferencer
        _INFERENCER = HPSv3RewardInferencer(device="cuda")
    return _INFERENCER


def score(paths, prompt=None):
    """mu for each image. The prompt matters — HPS scores (image, prompt) alignment as well
    as quality, which is why it can reward 'looks like the bicycle we asked for'."""
    paths = [str(p) for p in paths]
    prompt = prompt or (pathlib.Path(__file__).parent / "prompt/user.txt").read_text().strip()
    out = scorer().reward(paths, [prompt] * len(paths))
    return [float(r[0].item()) for r in out]


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
