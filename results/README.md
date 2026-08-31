# results — what survives the boxes

Rented boxes disappear; `runs/` is a local mirror and is gitignored. This directory holds the
part of each run that has to outlive both: enough to write the post, reproduce the numbers,
and see what changed, without carrying gigabytes of renders.

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| steps | 320 | 320 | 320 (cycles 0-13 one box, 14-19 resumed on another) |
| prompt | v1 | v2.1 | v2.1 |
| checklist | flat; two circles scored 2/3 | tiered; two circles capped at 0.30 | tiered |
| weights | pairwise 0.60, checklist 0.30 | checklist 0.55, pairwise 0.35 | checklist 0.45, hps 0.25, pairwise 0.20 |
| reward, start → end | 0.284 → 0.487 | 0.152 → 0.570 | **0.212 → 0.611** |
| gate | 0.64 → 0.97 | 0.38 → 0.98 | 0.45 → 0.97 |
| checklist | 0.070 → 0.255 | 0.043 → 0.547 | **0.084 → 0.621** |
| judged a bicycle, final cycle | 9/128 | 92/128 | **117/128** |
| closed frame, final cycle | 15/128 | 47/128 | **78/128** |
| all five checklist items, whole run | 3 | 64 | **98** |
| sketches calling `brush.fill`, final | 128/128 | 4/128 | 128/128 |
| distinct `brush.fill` arguments, start → end | 27 → 11 | 192 → 5 | **163 → 95** |
| HPSv3 raw, first → last cycle | — | — | −4.85 → **+3.95** |

Baseline for all three: **0 recognisable bicycles in 50**. A gold reference photograph scores
6.94 on HPSv3; two bare circles score −5.16.

**Read the two colour rows together, not the first one alone.** Run 1 appears to keep its
paint at 128/128, but its v1 prompt shipped a worked example containing
`brush.fill(WASH_COLOUR, 90)`, so a sketch scored on that row by transcribing. Its final cycle
made 381 fill calls with **11 distinct arguments** — the same few copied lines. Run 3's made
289 with **95**. All three runs lost colour *variety*; run 3 is the only one that kept
painting, and the only one whose reward ever mentioned what a drawing looks like.

That is the whole arc in one sentence: **each run got exactly what its reward asked for.**
Run 1's pairwise-heavy reward bought a gate and little else. Run 2 added a tiered structural
checklist, reached 72% bicycles, and paid for them with every drop of colour — 116 painting
sketches down to 4. Run 3 put a quarter of the reward on HPSv3 and finished with more
structure than run 2 *and* the paint intact.

The worry mid-run 3 was that the aesthetic term would buy beautiful wheels instead of
bicycles — at cycle 11 a frameless pair of spoked wheels scored 0.623 on HPS and pairwise
alone. It closed on its own: `closed_frame` went 27 → 78 over the last six cycles. See
BITACORA 026 and 027.

## Where each run lives

`runs/` is the gitignored local mirror, one directory per run — **not** per box, so a run
that spanned two rentals is still one directory:

| run | mirror | adapter | checkpoints |
|---|---|---|---|
| 1 | `runs/run1/` | final only | — |
| 2 | `runs/run2/` | final only | — |
| 3 | `runs/run3/` | final | 0080, 0160, 0224, 0240, 0320 |

Each committed `results/run<N>-320steps/` holds `log.jsonl`, `per-cycle.json`, `rewards/*.json`
(per-rollout scores and per-item judge verdicts), `state.json`, `prompt/` (the exact prompt
that run trained against) and three sample sheets.

`results/rebuild.py <run> <mirror>` regenerates the committed archive from a mirror, so all
three share one schema. Fields a run never measured are `null`, never 0 — run 1 recorded no
per-item verdicts for its early cycles, and a zero there would read as "the judge said no"
rather than "nobody asked". Numbers it recorded at the time but we can no longer derive are
kept with a `legacy_` prefix.

## What is deliberately not here

- **The renders and sketches** — ~2,500 PNG/JS pairs per run, hundreds of MB. The sample
  sheets carry the visual story; individual rollouts live in the local `runs/` mirror.
- **The LoRA adapters** — 154 MB each, over GitHub's 100 MB per-file limit, so they cannot go
  in plain git. They are in `runs/<box>/lora/` locally, with the optimiser state beside them.

  **TODO, when the project wraps: publish the adapters to the Hugging Face Hub.** That is
  where model weights belong, it costs nothing, and it means a reader of the post can load
  run 2's adapter and draw their own bicycles rather than take the numbers on trust. Until
  then they exist on exactly one disk, which is the real risk here — not the repo size.

      huggingface-cli login
      huggingface-cli upload <user>/bicycle-rl-run2 runs/run2/lora

  Publish with the base model id (`Qwen/Qwen2.5-Coder-7B-Instruct`), the prompt it was
  trained against (`bike/prompt/system.txt`, v2.1) and the reward weights — an adapter
  without those three is not reproducible.

## Rebuilding a run's artefacts

`bike/sheet.py` makes contact sheets from any directory of images; `rewards/*.json` carries
the per-item verdicts, so every table in the bitácora can be recomputed from what is here.
