# bicycle-rl

Teaching a model to draw with code, following
<https://surya.website/rling-qwen-to-paint-with-code>: model writes a sketch → render it
headlessly → judge the image → reward → repeat.

**Current target: a bicycle, side view, ink line drawing, in p5.brush** — see [`bike/`](bike/).
Bicycles because almost nobody can draw one from memory
([Velocipedia](https://www.gianlucagimini.it/portfolio-item/velocipedia/)), so the failures
are legible and the judging is fast.

## Layout

- `AGENTS.md` — how we work here. Read it first.
- `BITACORA.md` — lab notebook, becomes the blog post. Every session appends to it.
- `bike/` — the current target: harness, renderer, reference sketches ([its own README](bike/README.md))
- `corpus/` — **parked.** Hydra sketch harvest + curation wireframe ([its own README](corpus/README.md))
- `data/` — final `{"prompt": ..., "code": ...}` pairs (jsonl), exported from `corpus/`
- `train/` — LoRA config + training script
- `eval/` — render sketches headlessly, eyeball the grid

Where we are: the render loop works end to end (`bike/render.py`). Next is a base-model
baseline batch. `train/` and `eval/` are still just the plan.

## Notes — the parked hydra branch

Hydra is a JS DSL, so the base model already knows the syntax shape; the LoRA is
for style and for the operators it hallucinates wrong (`modulateScrollY`, `kaleid`,
feedback via `src(o0)`).

p5 runs inside hydra (`p1 = new P5()` → `s0.init({src: p1.canvas})`), which is how a sketch
gets text, typography and per-object geometry. Every renderer we build has to load p5.
