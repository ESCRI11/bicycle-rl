# results — what survives the boxes

Rented boxes disappear; `runs/` is a local mirror and is gitignored. This directory holds the
part of each run that has to outlive both: enough to write the post, reproduce the numbers,
and see what changed, without carrying gigabytes of renders.

| | run 1 | run 2 |
|---|---|---|
| prompt | v1 — API only, no bicycle description | v2.1 — written against 466 error logs |
| checklist | flat; two circles scored 2/3 | tiered; two circles capped at 0.30 |
| weights | pairwise 0.60, checklist 0.30 | checklist 0.55, pairwise 0.35 |
| reward, start → end | 0.284 → 0.487 | **0.152 → 0.572** |
| gate | 0.64 → 0.97 | 0.38 → 0.98 |
| checklist | 0.070 → 0.255 | **0.043 → 0.544** |
| judged a bicycle, final cycle | ~6% | **72% (92/128)** |
| all five checklist items | 7 in 2560 | 64 in 1974 |

Baseline for both: **0 recognisable bicycles in 50**.

Each run directory holds `log.jsonl` (every step), `per-cycle.json` (the summary table),
`rewards/NNN.json` (per-rollout scores *and* per-item judge verdicts), `state.json`, and
sample sheets from the start, middle and end.

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
