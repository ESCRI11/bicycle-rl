# Plan v2 — help the model see a bicycle before asking RL to teach it

Written 2026-08-29, after the 320-step run (bitácora 020). Stage by stage, each with a
decision gate. Nothing in a later stage starts until the gate before it is passed.

## Why

The v1 prompt is 2,633 characters about the p5.brush API and **not one word about what a
bicycle is**. The model had to infer the composition unaided *and* express it in an
unfamiliar library at the same time. The run showed where the budget went: 320 steps of RL
spent most of their gradient moving the render gate from 0.64 to 0.97 — teaching the model
not to crash. Structure only started moving at step 130.

If a better prompt starts near 0.9 on the gate, the whole step budget goes to structure
instead. **Prompt work is the cheap place to buy what RL buys expensively.**

The rule from bitácora 017 still binds: **knowledge is fair, implementation is not.** A
verbal description of a bicycle is guidance the model must still turn into code. A
`paint()` skeleton with literal coordinates is the answer, and `gepa_run.py --check-prompt`
rejects it mechanically (no `function paint`, ≤3600 chars, ≤32 `brush.*` calls).

## Stage 0 — draft prompt v2  ·  free, done

`bike/prompt/system_v2.txt`: the v1 API section unchanged, plus a STRUCTURE paragraph
describing a side-view bicycle in words, and one procedural line — *choose the two hub
positions and the wheel radius first, then derive everything from them*. Small models fail
composition tasks by drawing before deciding a layout; that sentence may matter more than
the description.

Passes the anti-smuggling check. No coordinates, no skeleton.

## Stage 1 — local baseline, judged by eye  ·  ~45 min on this workstation, free

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama
python3 generate.py -n 50 --model qwen2.5-coder:7b --workers 2 \
        --prompt prompt_v2 --out out/baseline-v2
python3 render.py out/baseline-v2/gen_*.js -o out/baseline-v2
python3 sheet.py out/baseline-v2/gen_*.png -o out/baseline-v2.png --cols 8
```

Measurable without any judge: render rate, code length, and the wheel-pair heuristic (two
`brush.circle` calls of similar large radius) — the same three numbers we have for v1's
baseline, so the comparison is like for like.

**Decision gate — yours, by eye.** Put the v2 sheet next to `bitacora-assets/baseline-v3.png`
(v1: 50 sketches, 0 bicycles):

- **Drawings already look like bicycles** → prompt work was the whole job. RL becomes
  optional polish, and the honest post is "a small model plus a good prompt", which is a
  more useful result than it sounds.
- **Better but not bicycles** → proceed. This is the expected case.
- **No better than v1** → the structural paragraph is not being used; try the procedural
  framing alone, or a worked *description* of the layout order, before spending on a box.

## Stage 2 — rent a box, re-validate the judge  ·  ~30 min, free

`./box/sync.sh` + `box/setup.sh` + `box/serve-judge.sh`, then `calibrate.py` against the
ladder to confirm `Qwen2.5-VL-72B-AWQ` still scores 6/7 items, ~82% structural pairs,
<20% position flips. **A judge that has not been re-validated is not a judge.**

## Stage 3 — better judging rules  ·  ~1 h, free

Every candidate item must discriminate on the ladder before it enters the reward. New
ablation rungs needed: `wheels-touching`, `frame-short-of-wheels`.

| candidate item | question | validated by |
|---|---|---|
| `wheels_apart` | are the two wheels separated, not touching or overlapping? | new `wheels-touching` rung |
| `frame_reaches_wheels` | do the frame lines meet both wheel centres? | `fork-detached`, `no-frame` |
| `wheels_on_a_line` | do both wheels sit on the same horizontal line? | `scrambled` |

**The crop experiment**, separately: the 72B cannot see a fork or a chain at full-canvas
scale, which is why `steering` and `drivetrain` were dropped and why the trained model draws
neither. Crop the right third of the image and ask about the fork there. VLMs read small
detail far better zoomed. If it works, both items come back and the ceiling rises from
"silhouette" to "machine". Ten minutes to find out.

## Stage 4 — reference pool  ·  ~1 h of your time

Pairwise is 0.60 of the reward and currently pits a rollout against a random sibling —
usually two failures, so the comparison is close to a coin toss. Build a pool of known-good
drawings and compare against *that*, as the original post did with its 581 rated images.

Seed material already exists: 7 perfect 3/3 rollouts, 49 the judge called bicycles, the gold
reference, and 2,560 renders in `runs/` to rate in `judge_photos.html` (it takes any image
directory).

## Stage 5 — GEPA, properly this time  ·  ~30–60 min on the box, ~$0

It failed in bitácora 018 for a measurable reason: 4 instances per candidate gives a
standard error of 0.072, and resolving a 0.10 difference needs ~23. That was 30 hours on
CPU. On the A100 it is half an hour. Same anti-smuggling constraints, seed = prompt v2,
metric = gate + the new checklist, judge local and free.

## Stage 6 — training, warm start  ·  ~7 h, one A100

Continue from `runs/run1/lora` rather than starting fresh — the 0.64 → 0.97
gate learning is paid for, no reason to buy it twice. Reward changes:

- **gate becomes a multiplier, not a component.** It is at 0.97; it no longer needs weight,
  it needs to be a precondition.
- weight moves to the checklist and to pairwise-against-the-pool.
- keep the length band; median code length drifted 1243 → 1533 and the band never bound.

## Stage 7 — the figure

Baseline v1 (0/50) → baseline v2 (prompt only) → trained v2. Three sheets, same 50-sample
protocol, same seeds. That separates what the prompt bought from what RL bought, which is
the honest version of the story and more useful than a single number.

## Costs

| stage | time | money |
|---|---|---|
| 0–1 local baseline | ~45 min | free |
| 2–3 judge + rules | ~1.5 h | free (local judge) |
| 4 reference pool | ~1 h of yours | free |
| 5 GEPA | ~1 h | free |
| 6 training | ~7 h | one A100 |

Roughly one box-day. The judge costs nothing because it runs on the same card.

## v3 candidate — HPSv3 as a dense component

Dropped in entry 005 on the grounds that a bicycle is judged on structure rather than beauty,
and that an aesthetic scorer trained on text-to-image generations would be out of
distribution on sparse ink drawings. The second half of that was an assumption, never tested,
and two arguments now point the other way:

- **HPS is prompt-conditioned.** It scores (image, prompt), i.e. "how well does this match
  *a bicycle, side view, ink drawing on off-white paper*" — a recognisability signal, not
  only an aesthetic one. Humans asked to pick between two bicycles pick the one that looks
  like a bicycle.
- **It is dense where our reward is sparse.** The tiered checklist is five binaries and 70%
  of samples score exactly 0 — that is what made GEPA unsearchable and what keeps the early
  gradient thin. A continuous score orders the blobs too, which is most of training.

Test it the same way as everything else, before it enters the reward: does it rank the gold
bicycle above `scrambled`, the ablation rungs in order, and the 24 two-circle rollouts below
the 6 real bicycles? Ten minutes on the ladder, and it needs a GPU slice alongside the judge.
