#!/usr/bin/env python3
"""The judge: a vision model scoring bicycle drawings against a reference photograph.

    python3 judge.py checklist out/baseline/gen_005.png
    python3 judge.py pairwise out/ladder/00-gold.png out/ladder/scrambled.png

Reads OPENROUTER_API_KEY from the environment. Model is pinned in JUDGE_MODEL — pin it, do
not use a floating alias: a judge that silently updates mid-run makes the reward
non-stationary and the training curve becomes two reward functions stitched together.

Prompts live in prompt/judge_*.txt, never in this file.
"""
import argparse, base64, hashlib, json, os, pathlib, re, sys, time, urllib.error, urllib.request

HERE = pathlib.Path(__file__).parent
PHOTOS = HERE / "photos"
MODEL = os.environ.get("JUDGE_MODEL", "google/gemini-2.5-flash")
# JUDGE_BASE_URL points this at a local vLLM instead of OpenRouter: same OpenAI-compatible
# shape, no network hop, no per-call cost. The key is ignored by vLLM but must be present.
BASE = os.environ.get("JUDGE_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
URL = BASE + "/chat/completions"
KEY = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("JUDGE_API_KEY", "EMPTY")
FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def data_url(path):
    # sniff, do not trust the extension: one photo in the pool is a PNG named .jpg, and
    # Anthropic rejects a mismatched media type with a bare 400 while Gemini ignores it
    raw = path.read_bytes()
    mime = "image/png" if raw[:8] == b"\x89PNG\r\n\x1a\n" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def reference_photo(key):
    """Same drawing always gets the same reference photo: comparisons stay reproducible."""
    pool = sorted(PHOTOS.glob("*.jpg"))
    if not pool:
        sys.exit("no photos in photos/ — run fetch_photos.py")
    return pool[int(hashlib.sha1(str(key).encode()).hexdigest(), 16) % len(pool)]


class JudgeUnavailable(RuntimeError):
    """Every retry failed. The caller decides what that means; it must not end a run."""


def ask(prompt_file, labelled, temperature=0.0, tries=3):
    return ask_text((HERE / "prompt" / prompt_file).read_text().strip(), labelled,
                    temperature, tries, schema=SCHEMAS.get(prompt_file),
                    name=prompt_file.split(".")[0])


def ask_text(prompt, labelled, temperature=0.0, tries=3, schema=None, name="out", raw=False):
    """labelled is [(caption, path), ...]. The caption goes in front of each image as its own
    text block: three bare images in a row and the model loses track of which is which — it
    told us two visibly different drawings were identical."""
    content = [{"type": "text", "text": prompt}]
    for caption, path in labelled:
        content.append({"type": "text", "text": caption})
        content.append({"type": "image_url", "image_url": {"url": data_url(path)}})
    payload = {"model": MODEL, "temperature": temperature,
               "messages": [{"role": "user", "content": content}]}
    # a small local judge cannot hold a JSON format on its own — it burned three retries on
    # malformed output. vLLM constrains decoding to the schema, so what we measure is
    # whether the model can SEE, not whether it can format.
    if (os.environ.get("JUDGE_STRUCTURED", "1" if "localhost" in BASE else "0") == "1"
            and schema):
        payload["response_format"] = {"type": "json_schema",
                                      "json_schema": {"name": name, "schema": schema}}
    body = json.dumps(payload).encode()
    # a judge that answers with prose, an empty string or a 502 must cost one call, not a
    # multi-hour run: GEPA died at iteration 1 on a bare json.loads of an empty response
    last = ""
    for n in range(tries):
        try:
            req = urllib.request.Request(URL, data=body, headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + KEY,
                "HTTP-Referer": "https://github.com/ESCRI11/bicycle-rl", "X-Title": "bicycle-rl"})
            with urllib.request.urlopen(req, timeout=180) as r:
                text = json.load(r)["choices"][0]["message"]["content"]
            if raw:
                return text
            m = FENCE.search(text)
            return json.loads(m.group(1) if m else text)
        except Exception as e:                       # parse, HTTP, timeout, malformed body
            last = f"{type(e).__name__}: {str(e)[:120]}"
            if n < tries - 1:
                time.sleep(2 * (n + 1))
    raise JudgeUnavailable(last)


ITEMS = ("two_wheels", "equal_wheels", "closed_frame", "steering", "drivetrain")

_ITEM = {"type": "object", "additionalProperties": False,
         "properties": {"yes": {"type": "boolean"}, "why": {"type": "string"}},
         "required": ["yes", "why"]}
SCHEMAS = {
    "judge_checklist.txt": {"type": "object", "additionalProperties": False,
                            "properties": {k: _ITEM for k in ITEMS},
                            "required": list(ITEMS)},
    "judge_pairwise.txt": {"type": "object", "additionalProperties": False,
                           "properties": {"a_has": {"type": "string"},
                                          "b_has": {"type": "string"},
                                          "winner": {"type": "string", "enum": ["A", "B"]},
                                          "why": {"type": "string"}},
                           "required": ["a_has", "b_has", "winner", "why"]},
}


def checklist_single(png):
    """Five one-question calls instead of one five-question call, and no reference photo.

    A local 72B scored a correct bicycle and an incoherent scramble identically (2/5 each)
    when asked all five at once with a photo alongside; asked one at a time it separates
    them. Frontier judges do not need this — it costs 5x the calls, which is free locally.
    """
    items = json.loads((HERE / "prompt" / "judge_items.json").read_text())
    suffix = items["_suffix"]
    qs = {k: items[k] for k in items["_tier1"] + items["_tier2"]}
    out = {}
    for k, q in qs.items():
        # pass the question as text, never through a shared temp file: calibrate runs six
        # threads in one process, they raced on the filename, and the gold bicycle scored
        # 0/5 while the scrambled one scored 3/5 because questions swapped between images
        # read the answer as text, not JSON. The 32B replies "True" with a capital T,
        # which json.loads rejects — every item came back false and the model looked blind
        # when it was answering correctly. Models are not obliged to speak JSON.
        try:
            ans = str(ask_text(q + suffix, [("THE DRAWING:", png)], raw=True)).strip()
            yes = ans.strip('".* ').lower().startswith(("true", "yes"))
        except JudgeUnavailable:
            yes = False
        out[k] = {"yes": yes, "why": q[:40]}
    return out


def checklist(png, photo=None):
    if os.environ.get("JUDGE_SINGLE") == "1":
        out = checklist_single(png)
        spec = json.loads((HERE / "prompt" / "judge_items.json").read_text())
        earned = sum(spec["_tier1_each"] for k in spec["_tier1"] if out.get(k, {}).get("yes"))
        # tier 2 carries 70% of the score and unlocks on recognition only — is_bicycle and
        # two_wheels. Gating it on wheels_apart as well scored real framed bicycles at 0.20
        # because their wheels touch. Two circles still cap at 0.30: they have no frame.
        unlocked = all(out.get(k, {}).get("yes") for k in spec["_tier2_requires"])
        if unlocked:
            earned += sum(spec["_tier2_each"] for k in spec["_tier2"] if out.get(k, {}).get("yes"))
        out["score"] = round(earned, 3)
        out["_max"] = 1.0
        out["_tier1_complete"] = unlocked
        return out
    photo = photo or reference_photo(png.name)
    out = ask("judge_checklist.txt",
              [("REFERENCE PHOTOGRAPH — do not grade this one:", photo),
               ("THE DRAWING TO GRADE:", png)])
    out["score"] = sum(bool(out.get(k, {}).get("yes")) for k in ITEMS)
    out["_photo"] = photo.name
    return out


def pairwise(a, b, photo=None):
    photo = photo or reference_photo(a.name + b.name)
    out = ask("judge_pairwise.txt",
              [("REFERENCE PHOTOGRAPH — do not judge this one:", photo),
               ("DRAWING A:", a), ("DRAWING B:", b)])
    out["_photo"] = photo.name
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["checklist", "pairwise"])
    ap.add_argument("images", nargs="+", type=pathlib.Path)
    a = ap.parse_args()
    if "openrouter" in BASE and "OPENROUTER_API_KEY" not in os.environ:
        sys.exit("OPENROUTER_API_KEY not set (or point JUDGE_BASE_URL at a local vLLM)")
    out = checklist(a.images[0]) if a.mode == "checklist" else pairwise(*a.images[:2])
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
