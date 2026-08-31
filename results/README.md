# results — what survives the boxes

Rented boxes disappear; `runs/` is a local mirror and is gitignored. This directory holds the
part of each run that has to outlive both: enough to write the post, reproduce the numbers,
and see what changed, without carrying gigabytes of renders.

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| steps | 320 | 320 | 320 (cycles 0-13 one box, 14-19 resumed on another) |
| prompt | v1 — API only, no bicycle description | v2.1 — written against 466 error logs | v2.1 |
| checklist | flat; two circles scored 2/3 | tiered; two circles capped at 0.30 | tiered |
| weights | pairwise 0.60, checklist 0.30 | checklist 0.55, pairwise 0.35 | checklist 0.45, hps 0.25, pairwise 0.20 |
| reward, start → end | 0.284 → 0.487 | 0.152 → 0.572 | **0.212 → 0.611** |
| gate | 0.64 → 0.97 | 0.38 → 0.98 | 0.45 → 0.97 |
| checklist | 0.070 → 0.255 | 0.043 → 0.544 | **0.084 → 0.621** |
| judged a bicycle, final cycle | ~6% | 72% (92/128) | **91% (117/128)** |
| closed frame, final cycle | not tracked | not tracked | 78/128 |
| all five checklist items | 7 in 2560 | 64 in 1974 | **98 in 2560** |
| still painting (`brush.fill`) | not measured | **4/128** | **128/128** |
| HPSv3 raw, first → last cycle | — | — | −4.85 → **+3.95** |

Baseline for all three: **0 recognisable bicycles in 50**. A gold reference photograph scores
6.94 on HPSv3, and two bare circles score −5.16.

**Run 3 is the result.** Runs 1 and 2 optimised rewards that never mentioned what a drawing
looks like, and run 2 paid for its structure with every drop of colour — 41/50 base-model
samples called `brush.fill`, 1/50 after training, and temperature 1.2 could not revive it.
Run 3 put a quarter of the reward on HPSv3 and finished with *every* sample painting, a
higher checklist score than run 2, and 91% of the final batch judged a bicycle.

The worry mid-run was that the aesthetic term would buy beautiful wheels instead of
bicycles: at cycle 11 a frameless pair of spoked wheels scored 0.623 on HPS and pairwise
alone, and `closed_frame` lagged `two_wheels` 1:4. It closed on its own — `closed_frame`
went 27 → 78 over the last six cycles while `two_wheels` saturated. The aesthetic term got
to wheels first; it did not stop there. See BITACORA 026 and 027.

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
      huggingface-cli upload <user>/bicycle-rl-run2 runs/ubuntu_216_81_245_141/lora

  Publish with the base model id (`Qwen/Qwen2.5-Coder-7B-Instruct`), the prompt it was
  trained against (`bike/prompt/system.txt`, v2.1) and the reward weights — an adapter
  without those three is not reproducible.

## Rebuilding a run's artefacts

`bike/sheet.py` makes contact sheets from any directory of images; `rewards/*.json` carries
the per-item verdicts, so every table in the bitácora can be recomputed from what is here.
