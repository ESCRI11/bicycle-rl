# AGENTS.md

RL a small model to draw a **bicycle** with [p5.brush](https://github.com/acamposuribe/p5.brush).
Following <https://surya.website/rling-qwen-to-paint-with-code> (RL'd Qwen to paint
watercolour hibiscus): same loop — write code, render headlessly, judge the image, reward —
on a subject where failure is legible, because almost nobody can draw a bicycle from memory.

The project started as a hydra live-coding LoRA; that branch is parked in `corpus/`, and the
bitácora keeps the whole path including the pivot.

---

## RULE 1 — THE BITÁCORA IS THE PRODUCT

`BITACORA.md` is a lab notebook that **will be rewritten into a blog post**. The model, the
LoRA, the dataset — all of it is replaceable. The narrative of how we got there is not,
because nobody can reconstruct it after the fact.

**Every session that changes anything appends one entry to `BITACORA.md`.** Not a summary
at the end of the project, not a commit message: an entry, while it is fresh, in the format
at the top of that file.

What must land in an entry, because a blog post cannot be written without it:

- **Numbers.** Counts, reward values, wall-clock, VRAM, cost. "It got better" is worthless.
  "180 → 213 sketches, 61% keep rate, 40 min" is a paragraph of blog post.
- **Dead ends.** The thing that did not work is the most interesting part of the post.
  Never delete a failed approach from the bitácora — mark it `dead end` and say why.
- **Decisions with the alternative attached.** "Chose X over Y because Z."
- **Exact commands and file paths**, so a reader can follow along.
- **Screenshots/renders** worth showing: drop them in `bitacora-assets/` and link them.

Rules for editing it:

- **Append-only.** Fix typos, never rewrite history. If we later find out an entry was
  wrong, add a new entry saying so and link back. The reversal is the story.
- Present tense, first person plural, terse. Notes, not prose — the blog pass turns them
  into prose later.
- One entry per session, numbered, dated (absolute dates, never "yesterday").
- If the user says something quotable about why we are doing this, write it down verbatim.

When the user asks for "the blog post", read the whole bitácora and write from it. Do not
invent a nicer story than the one in the notes.

---

## Project layout

**Current target: `bike/`** — a bicycle, side view, ink line drawing, in p5.brush. The hydra
work below is parked, not deleted; the corpus and the curation wireframe come back if the
bicycle loop works.

| Path | What |
|---|---|
| `bike/` | The live target: render harness, reference sketches. Own README. |
| `BITACORA.md` | Lab notebook → blog post. See Rule 1. |
| `corpus/` | *Parked.* Hydra sketch harvest + curation wireframe. Own README. |
| `data/` | Final training pairs `{"prompt", "code"}` (jsonl), exported from `corpus/`. |
| `train/` | LoRA config + training script. |
| `eval/` | Headless render of generated sketches, contact-sheet eyeball. |
| `bitacora-assets/` | Images referenced by the bitácora. |

Folders appear when we get to them. Do not scaffold empty ones.

## Conventions

- **Python stdlib first.** `urllib`, `json`, `re`, `http.server` cover the whole data
  pipeline. A new dependency needs a sentence in the bitácora justifying it.
- **Shortest thing that works.** No abstraction with one caller, no config for a constant.
  Deliberate shortcuts get a `# ponytail:` comment naming the ceiling and the upgrade path.
- **p5 inside hydra is in scope.** `p1 = new P5()` → `s0.init({src: p1.canvas})` →
  `src(s0)…out(o0)` is core hydra (the editor ships the wrapper) and it is where the rich
  sketches live: text, typography, geometry, per-object logic. Anything that renders or
  evaluates a sketch — the curation preview, the eval harness, the RL sandbox — **must load
  p5 and define the `P5` wrapper class**, or every p5 sketch fails the compile gate and the
  model learns to avoid the best half of the language. Extension libraries (hyper-hydra,
  antlia, HY5) stay out: their API does not exist in vanilla hydra-synth.
- **Provenance is not optional.** Every harvested sketch keeps `source` (URL) and
  `license`. Hydra gallery sketches are CC BY-NC-SA 4.0; community repos vary. We are
  training on other people's art — the blog post has to be able to credit it.
- **Determinism where it's free.** Sort, seed, and dedupe by content hash so re-running the
  harvest gives the same file.
- Generated artefacts that are cheap to rebuild stay out of git; the curated corpus goes in.

## Open TODOs

- **Make the Hugging Face adapter repos public when the post goes out.** All three are
  uploaded at `ESCRI11/bicycle-rl-run{1,2,3}` with prompt, reward weights and sample sheet,
  but created private — flipping to public is one call, un-publishing something already
  indexed is not. Command in `results/README.md`.
- **Write the post.** The bitácora is the raw material; `results/README.md` has the
  three-run comparison and the arc in one line: each run got exactly what its reward asked
  for.

## Working agreements

- Ask before adding a training dependency, a GPU spend, or a new stage to the pipeline.
- Prefer running things and pasting real output over describing what would happen.
- Small commits, present-tense subject line.
