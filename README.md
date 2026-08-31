# bicycle-rl

Teaching a small model to draw with code, following
<https://surya.website/rling-qwen-to-paint-with-code>: model writes a sketch → render it
headlessly → judge the image → reward → repeat.

**The target: a bicycle, side view, painted in p5.brush** — see [`bike/`](bike/).
Bicycles because almost nobody can draw one from memory
([Velocipedia](https://www.gianlucagimini.it/portfolio-item/velocipedia/)), so the failures
are legible and the judging is fast.

Three GRPO runs of 320 steps each on `Qwen2.5-Coder-7B-Instruct`. The base model draws
**0 recognisable bicycles in 50**; run 3 finished with **117 of 128** judged a bicycle, and
still painting. The comparison, and what each run's reward bought, is in
[`results/README.md`](results/README.md). Adapters:
[run1](https://huggingface.co/ESCRI11/bicycle-rl-run1) ·
[run2](https://huggingface.co/ESCRI11/bicycle-rl-run2) ·
[run3](https://huggingface.co/ESCRI11/bicycle-rl-run3).

## Layout

- `AGENTS.md` — how we work here. Read it first.
- `BITACORA.md` — lab notebook, becomes the blog post. Every session appends to it.
- `bike/` — the whole thing: prompt, render harness, judge, reward, training loop
  ([its own README](bike/README.md))
- `bike/train/` — the three-phase loop: sample → score → update, as separate processes
- `box/` — rent a GPU, set it up, run, mirror it back ([its own README](box/README.md))
- `results/` — what survives the boxes: per-run logs, scores, prompts, sample sheets
- `runs/` — gitignored local mirror, one directory per run
- `bicycles-judged/` — the first drawings a judge called a bicycle
- `bitacora-assets/` — images the bitácora references
