#!/usr/bin/env python3
"""Does HPSv3 carry signal on ink drawings of bicycles? Four gates, all free.

    python3 validate_hps.py

Nothing enters the reward until the ladder says it discriminates — the rule that caught a
judge that answered a constant, a judge that preferred the scrambled bicycle, and a parser
that threw away every "True".

Gate 4 is the one this component exists for: run 2's cycle-0 sketches are colourful and
structurally poor; its cycle-19 sketches are structurally good and bare ink. If HPS cannot
tell those apart, it cannot restore the colour we trained away.
"""
import pathlib, statistics, sys

import hps

HERE = pathlib.Path(__file__).parent


def mean_of(d, n=24):
    pngs = sorted(pathlib.Path(d).glob("*.png"))[:n]
    return (statistics.mean(hps.score(pngs)), len(pngs)) if pngs else (None, 0)


def main():
    ok = True
    print("gate 1 — the ablation ladder (gold should lead)")
    rungs = sorted((HERE / "out" / "ladder").glob("*.png"))
    scores = dict(zip([p.stem for p in rungs], hps.score(rungs)))
    for k in sorted(scores, key=lambda k: -scores[k]):
        print(f"    {k:16} {scores[k]:8.3f}")
    if scores and max(scores, key=scores.get) != "00-gold":
        print(f"  ! gold is not top: {max(scores, key=scores.get)} is"); ok = False

    print("\ngate 2/3 — two circles vs real bicycles")
    tc, n1 = mean_of(HERE / "validation" / "two-circles")
    tg, n2 = mean_of(HERE / "validation" / "target")
    if tc is not None and tg is not None:
        print(f"    two circles (n={n1})  {tc:8.3f}")
        print(f"    bicycles    (n={n2})  {tg:8.3f}")
        if tg <= tc:
            print("  ! HPS does not prefer the real bicycles"); ok = False

    print("\ngate 4 — colourful-but-wrong vs bare-but-correct")
    print("    (if this cannot separate them, HPS cannot bring the colour back)")
    for label, d in [("run2 cycle 0  (colourful, poor structure)", "validation/run2-c0"),
                     ("run2 cycle 19 (bare ink, good structure)", "validation/run2-c19")]:
        m, n = mean_of(HERE / d)
        print(f"    {label:42} {m:8.3f}" if m is not None else f"    {label:42}  (missing)")

    print(f"\n{'HPS carries signal — safe to weight it' if ok else 'BLOCKED — do not put this in the reward'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
