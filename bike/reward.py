#!/usr/bin/env python3
"""The reward: four components over a rendered batch.

    python3 reward.py out/baseline            # score a whole batch
    python3 reward.py out/baseline -k 2       # 2 pairwise opponents each

    weight  component
      0.05  renders at all (node --check passed, a PNG exists, nothing thrown)
      0.05  code length inside a band
      0.30  structural checklist, both judges AND-ed
      0.60  pairwise win rate against opponents from the same batch

Shape borrowed from surya.website/rling-qwen-to-paint-with-code, with the aesthetic scorer
swapped for structure: a bicycle is judged on facts before taste.

A sketch that does not render scores 0.0 and is never sent to a judge — there is nothing to
look at, and judge calls are the expensive part.
"""
import argparse, json, os, pathlib, random, sys
from concurrent.futures import ThreadPoolExecutor

import judge

# one local judge on the GPU box, two API judges when their blind spots must cancel out
CHECKLIST_MODELS = tuple(os.environ.get(
    "CHECKLIST_MODELS", "google/gemini-2.5-flash,anthropic/claude-sonnet-5").split(","))
PAIRWISE_MODEL = os.environ.get("PAIRWISE_MODEL", "anthropic/claude-sonnet-5")
# Rebalanced after the 320-step run. Pairwise was 0.60 and it is what paid for two circles:
# a rollout only has to beat a sibling, and when every sibling is bad "less bad" wins. The
# tiered checklist is now the discriminating signal — validated at 2.9x separation between
# real bicycles and the two-circle local optimum — so it carries the weight, and pairwise
# drops to a tiebreaker. Gate stays small: it is already implicit in the checklist, and the
# last run took it 0.64 -> 0.97 without needing a large share.
WEIGHTS = {"gate": 0.05, "length": 0.05, "checklist": 0.55, "pairwise": 0.35}
LO, HI = 300, 2800            # the gold reference is 2676 code chars: the band must not punish it


def code_len(src):
    """Length of the code, comments and blank lines removed. The band is there to stop
    collapse to one line and stop padding; a well-commented sketch is neither."""
    lines = [l for l in src.splitlines()
             if l.strip() and not l.strip().startswith("//")]
    return len("\n".join(lines))


def length_band(n, lo=LO, hi=HI):
    """1.0 inside the band, falling to 0 at half of lo and twice hi."""
    if lo <= n <= hi:
        return 1.0
    if n < lo:
        return max(0.0, (n - lo / 2) / (lo / 2))
    return max(0.0, (2 * hi - n) / hi)


def checklist_and(png):
    """An item counts only if BOTH judges see it: their blind spots do not overlap, and
    either one alone would wave through a bicycle with one wheel or mismatched wheels."""
    outs = []
    for model in CHECKLIST_MODELS:
        judge.MODEL = model
        outs.append(judge.checklist(png))
    asked = [k for k in outs[0] if not k.startswith("_")]
    items = {k: all(o.get(k, {}).get("yes") for o in outs) for k in asked}
    return sum(items.values()) / len(asked), items


def duel(png, other):
    """Both orderings. Agreement is a result, disagreement is a tie — never a coin flip."""
    judge.MODEL = PAIRWISE_MODEL
    fwd = judge.pairwise(png, other).get("winner")
    rev = judge.pairwise(other, png).get("winner")
    if fwd == "A" and rev == "B":
        return 1.0
    if fwd == "B" and rev == "A":
        return 0.0
    return 0.5


def score_one(js, opponents):
    png, err = js.with_suffix(".png"), js.with_suffix(".err")
    parts = {"gate": 1.0 if png.exists() and not err.exists() else 0.0,
             "length": length_band(code_len(js.read_text())),
             "checklist": 0.0, "pairwise": 0.0}
    detail = {}
    if parts["gate"]:
        parts["checklist"], detail = checklist_and(png)
        if opponents:
            wins = [duel(png, o) for o in opponents]
            parts["pairwise"] = sum(wins) / len(wins)
    total = sum(WEIGHTS[k] * v for k, v in parts.items())
    return {"sketch": js.name, "reward": round(total, 4),
            "parts": {k: round(v, 3) for k, v in parts.items()}, "items": detail}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=pathlib.Path)
    ap.add_argument("-k", type=int, default=1, help="pairwise opponents per sketch")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    sketches = sorted(a.batch.glob("gen_*.js")) or sorted(a.batch.glob("*.js"))
    if a.limit:
        sketches = sketches[: a.limit]
    rendered = [s for s in sketches if s.with_suffix(".png").exists()
                and not s.with_suffix(".err").exists()]
    if not rendered:
        sys.exit("nothing in this batch rendered — reward would be all zero by definition")
    rng = random.Random(a.seed)

    def opponents_for(js):
        pool = [r.with_suffix(".png") for r in rendered if r != js]
        return rng.sample(pool, min(a.k, len(pool))) if pool else []

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        rows = list(pool.map(lambda s: score_one(s, opponents_for(s)), sketches))

    out = a.batch / "reward.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    vals = sorted(r["reward"] for r in rows)
    nz = [v for v in vals if v > 0]
    print(f"{len(rows)} sketches, {len(rendered)} rendered\n")
    print(f"  reward   min {vals[0]:.3f}  median {vals[len(vals)//2]:.3f}  max {vals[-1]:.3f}")
    print(f"  non-zero {len(nz)}/{len(vals)}   distinct values {len(set(vals))}")
    for k in WEIGHTS:
        col = [r["parts"][k] for r in rows]
        print(f"  {k:10} mean {sum(col)/len(col):.3f}  max {max(col):.3f}")
    top = sorted(rows, key=lambda r: -r["reward"])[:3]
    print("\n  best:", ", ".join(f"{r['sketch']} {r['reward']:.3f}" for r in top))
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
