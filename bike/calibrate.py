#!/usr/bin/env python3
"""Does the judge agree with reality? Run before letting it near a reward.

    python3 calibrate.py                    # ladder only, ~56 calls
    python3 calibrate.py --baseline 20      # plus checklist on 20 baseline renders

Three questions, in order of how badly a wrong answer would hurt:

1. Per-item truth. Each ablation breaks exactly one checklist item, so we know what the
   judge should mark false. A judge that cannot see a missing chain cannot reward one.
2. Pair ordering. Cross-tier pairs have a ground-truth winner by construction.
3. Position bias. Every pair runs twice with A and B swapped. A judge that changes its mind
   is measuring position, not bicycles.
"""
import argparse, itertools, json, pathlib, sys
from concurrent.futures import ThreadPoolExecutor

import judge


def safe(fn, *a):
    """A judge that errors is a data point, not a crash: calibration exists to find that out."""
    try:
        return fn(*a)
    except Exception as e:
        return {"score": 0, "_error": f"{type(e).__name__}: {str(e)[:80]}"}

HERE = pathlib.Path(__file__).parent
LADDER = HERE / "out" / "ladder"

# rung -> (quality tier, the checklist item it should cost)
RUNGS = {
    "00-gold":        (4, None),
    "no-spokes":      (3, None),            # cosmetic control: structure intact
    "no-chain":       (2, "drivetrain"),
    "frame-open":     (2, "closed_frame"),
    "fork-detached":  (2, "steering"),
    "wheels-unequal": (1, "equal_wheels"),
    "one-wheel":      (1, "two_wheels"),
    "three-wheels":   (1, "two_wheels"),
    "no-frame":       (0, "closed_frame"),
    "scrambled":      (0, None),            # bottom anchor, everything wrong
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=int, default=0, help="also score N baseline renders")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    png = {name: LADDER / f"{name}.png" for name in RUNGS}
    missing = [str(p) for p in png.values() if not p.exists()]
    if missing:
        sys.exit(f"run ablate.py + render.py first, missing: {missing[0]}")

    pool = ThreadPoolExecutor(max_workers=a.workers)
    report = {"model": judge.MODEL}

    # 1 — per-item truth on the ablations
    print(f"judge: {judge.MODEL}\n\n== checklist on the ladder")
    scores = dict(zip(RUNGS, pool.map(lambda n: safe(judge.checklist, png[n]), RUNGS)))
    caught = total = 0
    for name, (tier, breaks) in RUNGS.items():
        s = scores[name]
        mark = ""
        if breaks:
            total += 1
            hit = not s.get(breaks, {}).get("yes")
            caught += hit
            mark = f"   {breaks}: {'CAUGHT' if hit else 'MISSED'}"
        print(f"  {name:16} score {s['score']}/5{mark}")
    report["item_detection"] = f"{caught}/{total}"
    report["ladder_scores"] = {k: v["score"] for k, v in scores.items()}

    # 2 + 3 — ordering and position bias, every pair both ways round
    pairs = [(x, y) for x, y in itertools.combinations(RUNGS, 2)
             if RUNGS[x][0] != RUNGS[y][0]]
    print(f"\n== {len(pairs)} cross-tier pairs, each run both ways")

    def both_ways(pair):
        x, y = pair
        fwd = safe(judge.pairwise, png[x], png[y])    # better one is A
        rev = safe(judge.pairwise, png[y], png[x])    # better one is B
        return pair, fwd, rev

    right = flips = right_struct = n_struct = 0
    wrong, verdicts = [], []
    for (x, y), fwd, rev in pool.map(both_ways, pairs):
        better = x if RUNGS[x][0] > RUNGS[y][0] else y
        got_fwd = x if fwd.get("winner") == "A" else y
        got_rev = y if rev.get("winner") == "A" else x
        verdicts.append((better, got_fwd, got_rev))
        right += (got_fwd == better) + (got_rev == better)
        flips += got_fwd != got_rev
        # scrambled keeps every checklist fact (two equal wheels, connected members) and only
        # fails globally, so pairs against it test coherence, not the checklist. Report apart.
        if "scrambled" not in (x, y):
            n_struct += 2
            right_struct += (got_fwd == better) + (got_rev == better)
        if got_fwd != better or got_rev != better:
            wrong.append(f"{x} vs {y}: picked {got_fwd}/{got_rev}, should be {better}"
                         f"  ({fwd.get('why','')})")
    report["pair_accuracy"] = f"{right}/{len(pairs) * 2}"
    report["position_flips"] = f"{flips}/{len(pairs)}"
    decisive = [p for p in verdicts if p[1] == p[2]]        # both orders agreed
    dec_right = sum(1 for better, f, _ in decisive if f == better)
    report["pair_accuracy_structural"] = f"{right_struct}/{n_struct}"
    report["decisive"] = f"{len(decisive)}/{len(pairs)}"
    report["decisive_accuracy"] = f"{dec_right}/{len(decisive)}" if decisive else "n/a"
    print(f"  correct              {right}/{len(pairs) * 2}")
    print(f"  correct, no scrambled {right_struct}/{n_struct}")
    print(f"  position flips {flips}/{len(pairs)}   (same pair, different answer when swapped)")
    print(f"  decisive       {len(decisive)}/{len(pairs)} pairs agreed both ways, "
          f"{dec_right}/{len(decisive)} of those correct"
          if decisive else "  decisive: none")
    for w in wrong[:8]:
        print(f"    x {w}")

    # optional — checklist over real baseline output, for the score distribution
    if a.baseline:
        base = sorted((HERE / "out" / "baseline").glob("gen_*.png"))[: a.baseline]
        got = list(pool.map(lambda b: safe(judge.checklist, b), base))
        dist = {i: sum(g["score"] == i for g in got) for i in range(6)}
        print(f"\n== checklist on {len(base)} baseline renders\n  score distribution {dist}")
        report["baseline_scores"] = {p.name: g["score"] for p, g in zip(base, got)}
        report["baseline_distribution"] = dist

    (HERE / "out" / "calibration.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"\n-> out/calibration.json")


if __name__ == "__main__":
    main()
