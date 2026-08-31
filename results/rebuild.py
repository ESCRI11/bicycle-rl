#!/usr/bin/env python3
"""Rebuild a run's committed archive from its local mirror.

    python3 results/rebuild.py 3 runs/run3

Runs 1-3 were archived by hand as each finished, so their per-cycle.json ended up with three
different schemas and run 1 shipped with no rewards/ at all. This regenerates all of it from
the mirror to one schema, so the three runs can be compared by a script instead of by eye.

Fields the run never measured come out null rather than 0 — run 1 stored no per-item judge
verdicts, and inventing zeros for them would read as "the judge said no" instead of "nobody
asked". Anything not computable is carried forward from the existing archive.
"""
import argparse, json, pathlib, re, shutil, sys

ITEMS = ["is_bicycle", "two_wheels", "wheels_apart", "frame_spans", "closed_frame"]


def cycle_row(d):
    rows = json.loads((d / "rewards.json").read_text())
    n = len(rows)
    has_items = any(r.get("items") for r in rows)
    hps = [r["hps_raw"] for r in rows if "hps_raw" in r]
    js = sorted(d.glob("gen_*.js"))
    out = {"cycle": d.name, "n": n,
           "mean_reward": round(sum(r["reward"] for r in rows) / n, 4),
           "gate": round(sum(r["parts"]["gate"] for r in rows) / n, 3),
           "checklist_mean": round(sum(r["parts"]["checklist"] for r in rows) / n, 4),
           # recoverable for every run: the sketches are on disk even when the reward that
           # scored them never mentioned colour
           "paint": sum(1 for f in js if "brush.fill" in f.read_text()) if js else None,
           # `paint` alone is not comparable across runs: run 1's v1 prompt shipped a worked
           # example containing `brush.fill(WASH_COLOUR, 90)`, so a sketch could score on it
           # by transcribing. Distinct arguments separate copying from choosing — run 1's
           # final cycle had 381 fill calls with 11 distinct args, run 3's 289 with 95.
           "distinct_fill_args": len({a.strip() for f in js
                                      for a in re.findall(r"brush\.fill\(([^,)]+)", f.read_text())})
                                 if js else None}
    for k in ITEMS:
        out[k] = sum(1 for r in rows if r.get("items", {}).get(k)) if has_items else None
    out["all_five"] = (sum(1 for r in rows if r.get("items") and all(r["items"].values()))
                       if has_items else None)
    out["hps_raw_mean"] = round(sum(hps) / len(hps), 2) if hps else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=int)
    ap.add_argument("mirror", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path)
    a = ap.parse_args()
    out = a.out or pathlib.Path(f"results/run{a.run}-320steps")
    cycles = sorted(p for p in (a.mirror / "cycles").glob("*") if (p / "rewards.json").exists())
    if not cycles:
        sys.exit(f"no scored cycles in {a.mirror}")

    (out / "rewards").mkdir(parents=True, exist_ok=True)
    for c in cycles:
        shutil.copy(c / "rewards.json", out / "rewards" / f"{c.name}.json")

    meta = json.loads((out / "per-cycle.json").read_text()) if (out / "per-cycle.json").exists() else {}
    old = {c["cycle"]: c for c in meta.get("cycles", [])}
    rebuilt = []
    for c in cycles:
        row = cycle_row(c)
        # Keep numbers the run recorded at the time but we can no longer derive, under a
        # legacy_ prefix so nobody mistakes them for the unified fields: run 1's
        # perfect_checklist counted 3 items, run 3's all_five counts 5. Same name would have
        # been a worse lie than a missing column.
        computed = {"judged_bicycle": "is_bicycle", "drew_a_frame": "frame_spans",
                    "perfect_checklist": "all_five"}
        for k, v in old.get(c.name, {}).items():
            if k in row:
                continue
            if row.get(computed.get(k)) is None:
                row["legacy_" + k] = v
        rebuilt.append(row)
    meta["cycles"] = rebuilt
    meta["steps"] = len(cycles) * 16
    (out / "per-cycle.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"run {a.run}: {len(cycles)} cycles -> {out}")


if __name__ == "__main__":
    main()
