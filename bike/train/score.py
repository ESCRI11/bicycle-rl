#!/usr/bin/env python3
"""Phase 2: render every sketch and score it. Needs the judge server up, not the policy."""
import argparse, json, pathlib, random, sys
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import judge, render, reward


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=pathlib.Path, required=True)
    ap.add_argument("--group", type=int, default=8, help="GRPO group size")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    js = sorted(a.dir.glob("gen_*.js"))

    with ThreadPoolExecutor(max_workers=a.workers) as pool:      # render is CPU-bound
        list(pool.map(lambda p: render.render(p, a.dir), js))

    rng = random.Random(0)
    rows = []
    def score(idx_js):
        idx, p = idx_js
        png, err = p.with_suffix(".png"), p.with_suffix(".err")
        parts = {"gate": 1.0 if png.exists() and not err.exists() else 0.0,
                 "length": reward.length_band(reward.code_len(p.read_text())),
                 "checklist": 0.0, "pairwise": 0.0}
        items = {}
        if parts["gate"]:
            out = judge.checklist(png)
            parts["checklist"] = out["score"] / out.get("_max", 5)
            # keep WHICH items fired, not just the total: "the judge called it a bicycle"
            # is the headline claim of this project and the total cannot answer it
            items = {k: bool(out[k]["yes"]) for k in out if not k.startswith("_") and k != "score"}
            # opponent from the same group: GRPO compares inside the group anyway
            g0 = (idx // a.group) * a.group
            peers = [q for q in js[g0:g0 + a.group]
                     if q != p and q.with_suffix(".png").exists() and not q.with_suffix(".err").exists()]
            if peers:
                parts["pairwise"] = reward.duel(png, rng.choice(peers).with_suffix(".png"))
        total = sum(reward.WEIGHTS[k] * v for k, v in parts.items())
        return {"file": p.name, "reward": round(total, 4),
                "parts": {k: round(v, 3) for k, v in parts.items()}, "items": items}

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        rows = list(pool.map(score, enumerate(js)))

    (a.dir / "rewards.json").write_text(json.dumps(rows, indent=1) + "\n")
    r = [x["reward"] for x in rows]
    ok = sum(1 for x in rows if x["parts"]["gate"])
    cl = sum(x["parts"]["checklist"] for x in rows) / len(rows)
    bike = sum(1 for x in rows if x.get("items", {}).get("is_bicycle"))
    print(f"{len(rows)} scored  rendered {ok}  reward mean {sum(r)/len(r):.3f} "
          f"max {max(r):.3f}  checklist mean {cl:.3f}  judged-a-bicycle {bike}")


if __name__ == "__main__":
    main()
