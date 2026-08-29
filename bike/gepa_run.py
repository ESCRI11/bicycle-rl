#!/usr/bin/env python3
"""GEPA over prompt/system.txt: sample -> render -> judge -> score + written feedback.

    . ../.venv/bin/activate
    export OPENAI_BASE_URL=http://localhost:11434/v1     # the model that draws
    export OPENROUTER_API_KEY=...                        # the judge and the reflector
    python3 gepa_run.py --dry-run                        # 2 evaluations, prints the feedback
    python3 gepa_run.py --max-metric-calls 150           # the real thing: hours, and money

The only "instances" are sampling seeds — one fixed user prompt, one fixed canvas — so a
candidate is scored by averaging several fresh samples rather than by one lucky draw.

Scoring is reward.py's shape minus the pairwise term (no batch to draw opponents from):
the expected checklist score per sample: 0 if it does not render, otherwise the tiered
score from prompt/judge_items.json, where two circles cap at 0.30 and only a frame reaching
both hubs pays the remaining 0.70.

GEPA's point is the feedback string, not the number: it is what the reflection model reads
when it rewrites the prompt. Errors and failed checklist items go in verbatim.
"""
import argparse, json, os, pathlib, re, shutil, sys, tempfile, urllib.request
from uuid import uuid4

import generate, judge, render, reward

HERE = pathlib.Path(__file__).parent
MODEL = os.environ.get("MODEL", "qwen2.5-coder:7b")   # the model that draws
CHECKLIST_MODEL = "google/gemini-2.5-flash"
# Checklist only. The gate is already inside it — a sketch that does not render scores 0 on
# every item — so a separate gate term double-counts, and it is the one term GEPA could max
# by making the prompt ask for less, which is how it would rediscover a prompt that renders
# reliably and draws nothing. Length never varied (~1.0 on every sample) and is not a
# component. Pairwise needs opponents and its 16-23% position flips would swamp a prompt
# difference; it belongs in RL where the group already exists.
WEIGHTS = {"checklist": 1.0}

# set once, not per call: judge.MODEL is a module global and evaluations run in parallel
judge.MODEL = CHECKLIST_MODEL


# GEPA's first run scored a perfect 1.0 by evolving a prompt that contained a complete,
# correct paint() and an order to copy its coordinates verbatim. The judge was right — a
# transcribed bicycle is a bicycle — but the metric could not tell drawing from copying.
# Knowledge about bicycles is fair game; an implementation is the answer.
#
# Measured on the two prompts: seed 2633 chars / 26 brush calls / no "function paint";
# the smuggled winner 6541 / 38 / has it. The caps sit between them.
LIMITS = {"chars": 3600, "brush_calls": 32}


def smuggled(text):
    """Why a zero and not a line in the prose: an optimiser routes around a request."""
    if "function paint" in text:
        return "prompt contains a complete paint() function — that is the answer, not instructions"
    if len(text) > LIMITS["chars"]:
        return f"prompt is {len(text)} chars, cap is {LIMITS['chars']} — say less, do not paste code"
    calls = len(re.findall(r"brush\.[a-zA-Z_]\w*\s*\(", text))
    if calls > LIMITS["brush_calls"]:
        return (f"{calls} brush.* calls in the prompt, cap is {LIMITS['brush_calls']} — "
                "describe what to draw, do not write the drawing")
    return None


def evaluate(candidate, example):
    """Never raises: GEPA has now lost two runs to a single bad evaluation."""
    try:
        return _evaluate(candidate, example)
    except Exception as e:
        return 0.0, {"feedback": f"evaluation failed: {type(e).__name__}: {str(e)[:200]}",
                     "scores": {"gate": 0.0, "length": 0.0, "checklist": 0.0}}


def _evaluate(candidate, example):
    """One rollout. Returns (score 0..1, side_info) — GEPA's `Evaluator` protocol.

    side_info["feedback"] is the reflection signal; side_info["scores"] is picked up by
    GEPA as per-objective scores, so the Pareto frontier keeps a candidate that is best at
    only one component.
    """
    bad = smuggled(candidate["system"])
    if bad:
        return 0.0, {"feedback": "REJECTED: " + bad,
                     "scores": {"gate": 0.0, "length": 0.0, "checklist": 0.0}}
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        # generate.complete() takes a prompt *directory*: hand it the candidate as system.txt
        (tmp / "system.txt").write_text(candidate["system"])
        shutil.copy(HERE / "prompt" / "user.txt", tmp / "user.txt")
        try:
            code = generate.clean(generate.complete(tmp, MODEL, 1.0, 1))
        except Exception as e:
            return 0.0, {"feedback": f"the endpoint failed, no sketch: {type(e).__name__} {e}"[:400]}

        # unique stem: render.py writes .render-<stem>.html next to lib/, shared across workers
        js = tmp / f"g{example}_{uuid4().hex[:6]}.js"
        js.write_text(code)
        png, err = render.render(js, tmp)

        rendered = not (err or png is None)
        parts = {"checklist": 0.0}
        if rendered:
            out = judge.checklist(png)
            parts["checklist"] = out["score"] / out.get("_max", 1.0)
            asked = [k for k in out if not k.startswith("_") and k != "score"]
            notes = [f"{k}: {out[k].get('why', '?')}" for k in asked if not out[k].get("yes")]
            if not out.get("_tier1_complete"):
                notes.insert(0, "recognition incomplete, so the frame items scored nothing")
        else:
            notes = ["the sketch never drew: " + err]
        # reported for the reflection model to read, not scored: length never varied and a
        # gate term is what would let a candidate win by asking for less
        if reward.length_band(reward.code_len(code)) < 1.0:
            notes.append(f"code length {reward.code_len(code)} is outside {reward.LO}-{reward.HI}")

        score = sum(WEIGHTS[k] * v for k, v in parts.items())
        return score, {"scores": {**parts, "rendered": float(rendered)},
                       "feedback": " | ".join(notes)[:400] or "every checklist item passed"}


def openrouter_lm(model):
    """GEPA accepts any (str | list[dict]) -> str callable as reflection_lm, so we skip
    litellm — the same urllib call judge.py already makes."""
    def call(prompt):
        msgs = prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}]
        body = json.dumps({"model": model, "messages": msgs}).encode()
        req = urllib.request.Request(judge.URL, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
            "HTTP-Referer": "https://github.com/ESCRI11/bicycle-rl", "X-Title": "bicycle-rl"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.load(r)["choices"][0]["message"]["content"]
    return call


OBJECTIVE = """Rewrite the system prompt so a 7B code model reliably writes a p5.brush
paint() function that draws a *structurally correct bicycle*, side view: two equal wheels,
a closed frame, handlebars joined to the front wheel through a fork, and a chain connecting
a chainring to the rear hub. The prompt must keep the output contract (one paint() function,
no fences, WEBGL coordinates -350..350, the p5.brush API listed) — a sketch that throws or
draws nothing scores near zero."""

BACKGROUND = """The user prompt is fixed and cannot be changed. Scores are 0.05 renders +
0.05 code-length band (300-2800 chars) + 0.90 a five-item structural checklist from a vision
judge. Feedback quotes the judge's reason for every failed item, or the JS error."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="2 evaluations, print the feedback")
    ap.add_argument("--train", type=int, default=8, help="samples averaged per candidate")
    ap.add_argument("--val", type=int, default=4)
    ap.add_argument("--max-metric-calls", type=int, default=150)
    # reflection, not judging, was 4/5 of the first run's $1.40: it reads every failure
    # trace and writes a whole replacement prompt each iteration. Flash is ~8x cheaper.
    ap.add_argument("--reflection-lm", default="google/gemini-2.5-flash")
    ap.add_argument("--check-prompt", type=pathlib.Path,
                    help="test a prompt file against the anti-smuggling rules and exit")
    ap.add_argument("--out", type=pathlib.Path, default=HERE / "out" / "gepa" / "system.txt")
    a = ap.parse_args()

    if a.check_prompt:
        bad = smuggled(a.check_prompt.read_text())
        print(f"{a.check_prompt}: {'REJECTED — ' + bad if bad else 'ok'}")
        return

    for var in ("OPENAI_BASE_URL", "OPENROUTER_API_KEY"):
        if var not in os.environ:
            sys.exit(f"set {var} first")

    seed = {"system": (HERE / "prompt" / "system.txt").read_text().strip()}
    # ponytail: instances are labels, not seeds passed to the endpoint — every call samples
    # fresh at temperature 1.0. Thread the int through generate.complete() as an OpenAI
    # `seed` if the sampling noise turns out to swamp the prompt differences.
    trainset, valset = list(range(a.train)), list(range(1000, 1000 + a.val))

    if a.dry_run:
        for i in trainset[:2]:
            score, info = evaluate(seed, i)
            print(f"\ninstance {i}  score {score:.3f}  {info.get('scores', {})}")
            print(f"  feedback: {info['feedback']}")
        return

    from gepa.optimize_anything import EngineConfig, GEPAConfig, ReflectionConfig, optimize_anything
    result = optimize_anything(
        seed_candidate=seed, evaluator=evaluate, dataset=trainset, valset=valset,
        objective=OBJECTIVE, background=BACKGROUND,
        config=GEPAConfig(
            # max_workers 2: ollama on CPU is the bottleneck, more threads just queue
            # display_progress_bar would need tqdm; gepa ships with no dependencies at all
            engine=EngineConfig(max_metric_calls=a.max_metric_calls, max_workers=2),
            reflection=ReflectionConfig(reflection_lm=openrouter_lm(a.reflection_lm))))

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(result.best_candidate["system"].strip() + "\n")
    print(f"\n{result.total_metric_calls} metric calls, {result.num_candidates} candidates")
    print(f"-> {a.out}   (copy over prompt/system.txt when it beats the baseline)")


if __name__ == "__main__":
    main()
