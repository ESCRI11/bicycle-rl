# corpus — hydra reference set

Self-contained. Two steps: **harvest** a big pool of real hydra sketches, then **curate**
it by hand down to the 200–300 that are actually good. The curated set is what the reward
model judges against and what the LoRA trains on, so it is worth an afternoon of eyeballs.

```
harvest.py   public sources -> candidates.jsonl   (stdlib + the `gh` CLI, no pip install)
sources.json which repos and which GitHub code searches
curate.html  the wireframe: renders each sketch live, keep/reject/prompt/tag
```

## 1. Harvest

```bash
python3 harvest.py              # ~2 min, needs `gh auth login` for the code-search sources
python3 harvest.py --no-search  # curated repos only, no gh
```

Writes `candidates.jsonl`, one sketch per line:

```json
{"id":"8387d4f095","code":"voronoi()\n  .color(.8,.4,.38)\n  .out(o1)","source":"https://github.com/…","origin":"github-search","license":"unknown","needs_input":false}
```

`id` is a hash of the whitespace-stripped code, so re-running is idempotent and your
curation decisions survive a re-harvest. New search hits are merged into the existing file,
never replace it. Delete `candidates.jsonl` to start from scratch.

`needs_input` flags sketches that want a webcam, microphone or video file — hidden by
default in the UI because they render black without one. `uses_p5` flags sketches that run
**p5 inside hydra**, the pattern where a p5 canvas becomes a hydra texture:

```js
p1 = new P5()
p1.hide()
p1.draw = () => { p1.background(0); p1.text('hydra', 60, 200) }
s0.init({ src: p1.canvas })
src(s0).modulate(noise(2), 0.03).kaleid(6).out(o0)
```

This is the only way to get text, typography, precise geometry and per-object logic into a
hydra sketch — the GLSL chain alone cannot express them — so it is explicitly in scope and
worth over-collecting. The `only p5-in-hydra sketches` filter in the UI isolates them.

## 2. Curate

```bash
python3 -m http.server 8000     # in this folder — file:// cannot fetch the jsonl
```

Open <http://localhost:8000/curate.html>. Each candidate runs live in the canvas via
hydra-synth from unpkg. p5 sketches run too: the page loads p5, defines the editor's `P5`
wrapper class and a `loadScript` shim, and evaluates each sketch inside an async function so
top-level `await loadScript(...)` works exactly as it does in the hydra editor. p5 instances
are removed between sketches.

| key | |
|---|---|
| `k` | keep, next |
| `x` | reject, next |
| `j` / `l` | prev / next |
| `r` | re-render |
| `ctrl+enter` | run your edits to the code |

The code box is editable — trim a broken sketch instead of rejecting it, the edit is what
gets exported. Write a plain-language **prompt** for every keep ("slow pulsing teal
kaleidoscope"): that is the input side of the training pair, and nothing downstream can
invent it for us. Tags are free signal for later filtering; use them loosely.

Decisions live in `localStorage` and survive a reload. **Export keeps.jsonl** downloads the
kept set as `{"id","prompt","code","tags","source","license"}` — move it to `data/`.

### What to keep

- Runs with no error, and looks like something after 3 seconds.
- Self-contained: no `s0.initCam()`, no external assets, no functions that vanilla
  hydra-synth does not define (`datamosh`, hyper-hydra extensions — the UI shows the error).
  `p1 = new P5()` is fine and wanted; it is part of the editor.
- Uses core hydra idiom: source → transforms → `.out(o0)`, feedback via `src(o0)`.
- Distinct from what is already kept. 200 sketches that all say `osc().kaleid()` teach one trick.

Aim for **200–300 keeps** with a bias toward variety over polish, and **keep at least ~40
p5-in-hydra sketches** among them (tick `only p5-in-hydra sketches` and do a dedicated pass).
That is the richest corner of the language and the one the base model is worst at.

## Provenance

Every record keeps its `source` URL and `license`. Hydra editor examples are CC BY-NC-SA
4.0; most GitHub-search results are unlicensed sketches by live coders. We are training on
other people's art — the blog post credits it, and anything we redistribute stays inside
what the licence allows.
