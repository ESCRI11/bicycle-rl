# Plan v3 — bicycles that a person would want to look at

Run 2 got structure: 0 bicycles in 50 → **72% of the final batch judged bicycles**. It also
threw the paint away, because nothing in the reward asked for it:

| | cycle 0 | cycle 19 |
|---|---|---|
| distinct colours per sketch | 3.6 | **0.9** |
| uses `brush.fill` | 115/128 | **4/128** |

That is a clean demonstration of a reward doing exactly what it is told, and v3 tells it
something more: **keep the structure, and make it worth looking at.**

## Stage 0 — the collapse test  ·  10 min on the box, free

Before anything else. RL can only reinforce what the policy still samples. Load run 2's
adapter, draw 50 sketches at temperature 1.0 and 50 at 1.2, and count how many still touch
`brush.fill`.

- **≥10% still paint** → colour is suppressed, not extinct. Warm-start from the adapter and
  keep the seven hours of structure we already bought.
- **≈0 paint** → the collapse is total, there is nothing to reinforce, and v3 starts from the
  base model with the aesthetic term present from step one.

This decides the next four stages, and it is the cheapest question we can ask.

## Stage 1 — does HPSv3 carry signal here?  ·  30 min, free

`bike/hps.py` wraps it (`pip install hpsv3`; 7B Qwen2-VL with a RankNet head, ~16 GB, scores
an (image, prompt) pair). `bike/validate_hps.py` runs four gates:

1. the ablation ladder, gold on top
2. two-circle rollouts below real bicycles
3. — as above, both directions
4. **run 2 cycle 0 (colourful, badly drawn) versus cycle 19 (bare ink, well drawn)**

Gate 4 is the whole point. If HPS cannot separate those two piles, it cannot bring the colour
back and it does not belong in the reward, however good the idea sounds. Both sets are
already built in `bike/validation/`.

**Fallback if it fails: your own taste.** Rate a few hundred of the 4,500 renders in
`judge_photos.html` for looks, and use that pool as pairwise opponents with the local 72B as
the judge — which is what the original post did with its 581 hand-rated images. Slower to set
up, but it optimises for *your* preference rather than a proxy for the average human's.

## Stage 2 — weights  ·  free

| component | v2 | **v3** |
|---|---|---|
| renders at all | 0.05 | 0.05 |
| code length band | 0.05 | 0.05 |
| structural checklist | 0.55 | **0.45** |
| pairwise (structure, in-group) | 0.35 | **0.20** |
| **HPSv3 (aesthetic)** | — | **0.25** |

HPS scores are unbounded reals, so they get normalised within each GRPO group before
weighting — the group is the natural scale, and it is what GRPO already uses.

**The failure mode to watch is the mirror of run 2's**: trading frames away for prettiness.
The checklist number reports it immediately, so treat any drop below ~0.45 as a signal to cut
the HPS weight rather than a curiosity.

## Stage 3 — training  ·  ~7 h, one A100

Warm-start or fresh, per stage 0. Same three-phase loop, which now has to fit the judge (46
GB) and HPS (16 GB) together during scoring — 62 GB, comfortable — while training still gets
the card to itself.

## Stage 4 — the figure

Three sheets, same protocol: **baseline** (0 in 50) → **run 2** (structure, no colour) →
**run 3** (structure and colour). That is the shape of the story, and each step has a reason
attached rather than a number that merely went up.

## What is already prepared

- `bike/hps.py`, `bike/validate_hps.py` — scorer and its four gates
- `bike/validation/run2-c0`, `run2-c19` — 24 images each for gate 4
- `box/setup.sh` — installs `hpsv3` with everything else
- `box/resume.sh` — puts run 2's adapter back on a fresh box for the warm start

Rent the box and it is: `sync.sh` → `setup.sh` → stage 0 → stage 1 → train.
