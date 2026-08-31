# AGENTS.md

RL a small model to draw a **bicycle** with [p5.brush](https://github.com/acamposuribe/p5.brush).
Following <https://surya.website/rling-qwen-to-paint-with-code> (RL'd Qwen to paint
watercolour hibiscus): same loop — write code, render headlessly, judge the image, reward —
on a subject where failure is legible, because almost nobody can draw a bicycle from memory.

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

**The target: `bike/`** — a bicycle, side view, painted in p5.brush.

| Path | What |
|---|---|
| `bike/` | Prompt, render harness, judge, reward. Own README. |
| `bike/train/` | The loop: `rollout.py` → `score.py` → `update.py`, separate processes. |
| `BITACORA.md` | Lab notebook → blog post. See Rule 1. |
| `box/` | Rent a GPU, set it up, run it, mirror it back. Own README. |
| `results/` | Per-run logs, scores, prompts and sample sheets. Own README. |
| `runs/` | Gitignored mirror of each run, one directory per run. |
| `bitacora-assets/` | Images referenced by the bitácora. |

Folders appear when we get to them. Do not scaffold empty ones.

## Conventions

- **Python stdlib first.** `urllib`, `json`, `re`, `http.server` cover the whole data
  pipeline. A new dependency needs a sentence in the bitácora justifying it.
- **Shortest thing that works.** No abstraction with one caller, no config for a constant.
  Deliberate shortcuts get a `# ponytail:` comment naming the ceiling and the upgrade path.
- **Provenance is not optional.** Every reference photograph keeps its `source` and
  `license` in `bike/photos/credits.json`. The judge compares drawings against other
  people's photographs — the blog post has to be able to credit them.
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
