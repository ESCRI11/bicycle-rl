# bike — a model that draws a bicycle from memory

The target: **a bicycle, side view, ink line drawing on off-white paper**, in p5.brush.
One fixed prompt for the whole run. Same canvas, same paper, same seeds — the only variable
is how good the bicycle is.

Bicycles because of [Velocipedia](https://www.gianlucagimini.it/portfolio-item/velocipedia/):
Gimini asked 376 people to draw a bike from memory and almost none could — frames that
cannot hold a wheel, chains that drive nothing. It is a task where failure is *legible*, so
a judge (human or VLM) ranks two attempts in half a second, and progress is visible in a
contact sheet without squinting at reward curves.

## The model

**Qwen2.5-Coder-7B-Instruct.** A code model for a code task, a LoRA that fits one 40 GB card
alongside vLLM rollouts, and bad enough at p5.brush to leave visible headroom. The post it is
based on only ever says "Qwen"; the size is our choice. Drop to 3B if the card is smaller.

## The contract

The model writes **one function, `paint()`**, and nothing else. The harness
(`template.html`) owns the canvas, the paper colour, the seeds and the screenshot:

```js
function paint() {
  brush.set('rotring', '#22221f', 2);
  brush.circle(-150, 120, 100, false);
  // …
}
```

Canvas is 700x700 **WEBGL**, so the origin is the centre: x and y run -350...350, +y is down.

**Allowlist — eight methods, nothing else:**

`brush.set` `brush.field` `brush.wiggle` `brush.line` `brush.circle` `brush.spline`
`brush.hatch` `brush.fill`

Short on purpose. The original post found that a strict allowlist beat pasting full API
docs into the prompt: more reference material made the models hallucinate *more* API, not
less. p5 built-ins (`cos`, `TWO_PI`, `random`, ...) are fair game.

## Generating

```bash
export OPENAI_BASE_URL=http://localhost:8000/v1     # vLLM, or any hosted provider
export OPENAI_API_KEY=...
python3 generate.py -n 50 --model Qwen/Qwen2.5-Coder-7B-Instruct
python3 render.py out/baseline/gen_*.js -o out/baseline
python3 sheet.py out/baseline/gen_*.png -o out/baseline.png --cols 8
```

The prompt is data, not code: `prompt/system.txt` + `prompt/user.txt`. Every batch copies
both into its output directory, so a contact sheet can always be traced back to the prompt
that made it. GEPA rewrites `system.txt` in place later.

## Rendering

```bash
python3 render.py gold/bike_01.js          # -> out/bike_01.png
python3 render.py out/gen_*.js -o out      # a whole batch
```

No npm, no pip: headless chrome writes the PNG, `node --check` catches syntax errors before
we pay for a browser, and runtime errors are painted onto the image as a red banner so a
broken sketch is obvious in a contact sheet.

Seeds are fixed in the harness (`randomSeed`, `noiseSeed`, `brush.seed`), so the same code
always produces the same image — no lucky-seed noise in the reward.

## The reward

`reward.py` scores a rendered batch. Four components, same shape as the post, with the
aesthetic scorer swapped for structure — a bicycle is judged on facts before taste.

```bash
python3 reward.py out/baseline -k 2      # -k = pairwise opponents per sketch
```

A sketch that does not render scores the length component only and is never sent to a judge:
there is nothing to look at, and judge calls are the expensive part. Length is measured on
code with comments and blank lines stripped — the band exists to stop collapse to one line
and to stop padding, and a well-commented sketch is neither. The bounds (300–2800) are set
so the gold reference sits inside at 1.0; a reward that marks down its own reference is
measuring the wrong thing.

| weight | signal | how |
|---|---|---|
| 0.05 | compiles and draws | `node --check`, then render; blank paper scores 0 |
| 0.05 | code length band | stops collapse to one line, and stops padding |
| 0.30 | structural checklist | vision judge, five grounded yes/no items |
| 0.60 | pairwise win-rate | two of *our own* drawings, a real photo alongside as reference |

The checklist, asked against a photo from `photos/`:

1. two wheels, both fully drawn
2. wheels the same size
3. frame closed — a shape you could actually weld
4. handlebars joined to the front wheel through a fork
5. a chain or drivetrain connecting a chainring to the rear hub

**Photos ground the judge, they are never the opponent.** Ask a judge "which looks more like
a real bicycle, this ink drawing or this photograph" and the photograph wins every time: the
reward saturates at zero and carries no gradient. The comparison has to stay in-domain —
drawing against drawing, with the photo in the prompt as the reference for what is true.

**One binary is not enough either.** Early on, every rollout fails "is this a bicycle", every
reward is 0, and there is nothing to climb. Five binaries summed give a dense 0–5 from the
same judge call.

Pairwise is the expensive part: a round robin over a group of 8 is 28 judge calls per step.
Two random opponents per rollout gets that to 8, or tile the group into one labelled grid and
ask for a single ranking.

## The photo pool

Target: **200 clean reference photographs**, judged by hand.

```bash
python3 fetch_photos.py            # candidates from Commons categories + searches
python3 -m http.server 8000        # then open localhost:8000/judge_photos.html
python3 fetch_photos.py --cull ~/Downloads/rejects.txt
```

`judge_photos.html` is the judging wireframe: every candidate as a tile, **click to keep**,
double-click to zoom, a counter that tracks progress toward 200. Decisions survive a reload
(localStorage). *Export rejects.txt* writes the filenames you did not keep; `--cull` deletes
them and records them in `photos/culled.json`, so the next fetch never hands them back.

Keep a photo if it is a **whole bicycle, side on, unobstructed**, the thing a judge could
check a drawing against: two wheels visible, frame legible, nothing sitting on it. Reject
riders, close-ups, three-quarter angles, drawings, book covers, and anything where the frame
disappears into the background.

`python3 fetch_photos.py --restore` re-downloads whatever `credits.json` lists but is missing
on disk — the pool is reproducible from the committed json, so the jpgs stay out of git.

Real bicycles, licensed and credited in `photos/credits.json` — the blog post has to credit
them. Commons enforces a robot policy: the User-Agent must name the project and a contact,
or every download comes back 429. Put your own contact in `fetch_photos.py`.

Watch the bias: what Commons photographs side-on is mostly folding bikes and Dutch
roadsters, so the queries ask for diamond frames explicitly. A pool of small-wheel folders
would teach the checklist judge the wrong proportions.

## The judge

Calibrated on the ablation ladder (below), not chosen on price.

- **Pairwise: `anthropic/claude-sonnet-5`.** Same structural accuracy as Gemini (53/60) but
  far steadier: 3/38 position flips against 11/38, and 35 of 38 pairs decisive against 27.
  With the consensus rule that matters — Gemini discards nearly a third of its comparisons
  as ties.
- **Checklist: both models, AND-ed.** Their blind spots are complementary and systematic,
  0/3 or 3/3 across three runs with nothing in between: **Gemini cannot count wheels**
  (misses `one-wheel` 0/3, `three-wheels` 1/3), **Sonnet cannot see an open frame or a size
  mismatch** (`frame-open` 0/3, `wheels-unequal` 0/3). An item counts as satisfied only if
  both models say yes, which costs one extra cheap call per image and makes the checklist
  hard to fool.

**Score a pair only when both orderings agree.** Every pairwise comparison runs twice with A
and B swapped; disagreement is a tie, not a coin flip. This is the difference between a
reward and a random number generator.

Pin the exact model ids. A floating alias that updates mid-run makes the reward
non-stationary, and the training curve then stitches two reward functions together with no
way to see it in the plot.

## Calibrating the judge: the ablation ladder

```bash
python3 ablate.py && python3 render.py out/ladder/*.js -o out/ladder
python3 sheet.py out/ladder/*.png -o out/ladder.png --cols 4 --cell 300
```

The baseline is fifty piles of scribbles with no ground-truth ordering, so hand-ranking
pairs from it is calibrating on coin flips. `ablate.py` breaks the reference bicycle in one
specific way at a time instead, and each way is one item on the checklist:

| rung | breaks |
|---|---|
| `00-gold` | nothing |
| `no-spokes` | nothing structural — cosmetic control |
| `no-chain` | chain connecting two rings |
| `frame-open` | frame closed (down tube removed) |
| `fork-detached` | bars joined to the front wheel |
| `wheels-unequal` | wheels the same size |
| `one-wheel` | two wheels, both drawn |
| `scrambled` | every joint moved — bottom anchor |

Rough tiers, best to worst: `gold` > `no-spokes` > {`no-chain`, `frame-open`,
`fork-detached`} > {`wheels-unequal`, `one-wheel`} > `scrambled`. Any cross-tier pair has an
answer that needs no human opinion, so a judge can be scored against it. **A judge that
prefers unequal wheels is disqualified.** Within-tier pairs are genuinely ambiguous — use
them to measure self-consistency, not correctness.

Show every pair twice, with the images swapped. A judge that changes its mind when A and B
trade places is measuring position, not bicycles.

The tubes are drawn twice — fat marker paint, then ink over it — so an ablation has to
remove both or the paint layer quietly puts the tube back. Every substitution asserts that
it fired; a silent no-op would turn a rung into a duplicate of the gold.

## Prompt optimisation (GEPA)

[GEPA](https://github.com/gepa-ai/gepa) rewrites `prompt/system.txt` by reading *why* a
sample failed, not just how much it scored: the metric hands back the JS error, or the
judge's own sentence for every failed checklist item, and a reflection model rewrites the
prompt from that. Score without feedback would just be a slower random search.

**This is the project's first pip dependency.** Everything else is stdlib plus headless
chrome. gepa is pure python with no transitive dependencies, so the venv holds exactly one
package — but it does mean `gepa_run.py` is the one script that needs the venv python.

```bash
python3 -m venv .venv           # from the repo root; .venv/ is already gitignored
source .venv/bin/activate
pip install gepa                # gepa 0.1.4, nothing else comes with it

cd bike
export OPENAI_BASE_URL=http://localhost:11434/v1   # the model that draws
export OPENROUTER_API_KEY=...                      # checklist judge + reflection model
python3 gepa_run.py --dry-run                      # 2 evaluations, ~2 min, no optimisation
python3 gepa_run.py --max-metric-calls 150         # the real run: hours, and money
```

The task has **one** fixed user prompt, so there is nothing to split into train and val
examples — the "instances" are just sampling seeds (8 train, 4 val by default). Every
evaluation draws a fresh completion at temperature 1.0, and averaging over seeds is what
stops GEPA from chasing one lucky sample.

Per evaluation: generate with the candidate system prompt, render, score
`0.05*renders + 0.05*length_band + 0.90*(checklist/5)`. Pairwise is dropped — it needs a
batch to draw opponents from, and there is none inside a single evaluation. **The checklist
runs on Gemini alone here**, not both judges AND-ed as in `reward.py`: two models over a few
hundred evaluations is about $2, which is more than the budget.

`--dry-run` performs exactly two evaluations and prints the score and the feedback string,
which is the whole wiring proven for the price of two samples:

```
instance 0  score 0.050  {'gate': 0.0, 'length': 1.0, 'checklist': 0.0}
  feedback: the sketch never drew: brush.wireframe is not a function

instance 1  score 0.460  {'gate': 1.0, 'length': 1.0, 'checklist': 0.4}
  feedback: closed_frame: Lines do not form a closed, weldable frame between the wheels. |
  steering: No handlebar or fork is visibly connected to the front wheel. | drivetrain: No
  chain, chainring, or crank is drawn.
```

That second one is the point: "no chain, chainring, or crank is drawn" is something a
reflection model can act on. A bare `0.46` is not.

The reflection model is any OpenRouter id (`--reflection-lm`, default
`anthropic/claude-sonnet-5`), called through the same eight-line urllib POST as the judge —
GEPA accepts any `(str | list[dict]) -> str` callable, so litellm never gets installed. The
winning prompt lands in `out/gepa/system.txt`; copy it over `prompt/system.txt` by hand once
a rendered batch shows it actually beats the baseline.

## Layout

```
prompt/         system.txt + user.txt — the fixed sketch prompt, as data
generate.py     sample sketches from an OpenAI-compatible endpoint
gepa_run.py     GEPA over prompt/system.txt (needs the venv: the only pip dependency)
template.html   the harness: canvas, paper, seeds, error banner
render.py       sketches -> PNGs, headless chrome, runtime errors into .err
ablate.py       the reference bicycle, broken one way at a time -> out/ladder/
sheet.py        many images -> one contact sheet PNG (batch eyeballing)
fetch_photos.py real bicycle photos from Wikimedia Commons -> photos/
judge_photos.html  click-to-keep wireframe for building the 200-photo pool
lib/            p5 2.3.2 + p5.brush 2.2.2, vendored (hermetic, no CDN per rollout)
gold/           hand-written reference sketches - what "good" looks like
photos/         the judge's grounding pool: jpgs (gitignored) + credits.json + culled.json
out/            rendered PNGs and contact sheets (gitignored)
```

**Version trap:** p5.brush 2.x calls `p5.registerAddon`, which only exists in **p5 2.x**.
Pair it with p5 1.x and every stroke silently no-ops onto blank paper.

## Where this differs from the post

The post could not use human watercolours as references — nothing hand-painted was
comparable to code-painted output, so its pool of 581 was model-generated and hand-rated.
A bicycle is different: a photograph of a real bicycle is *ground truth about the object*,
not a competing artwork, so real photos can do the grounding work from day one. Model-rated
drawings can still be added later as a second pool for the pairwise stage.
