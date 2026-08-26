#!/usr/bin/env python3
"""The judge: a vision model scoring bicycle drawings against a reference photograph.

    python3 judge.py checklist out/baseline/gen_005.png
    python3 judge.py pairwise out/ladder/00-gold.png out/ladder/scrambled.png

Reads OPENROUTER_API_KEY from the environment. Model is pinned in JUDGE_MODEL — pin it, do
not use a floating alias: a judge that silently updates mid-run makes the reward
non-stationary and the training curve becomes two reward functions stitched together.

Prompts live in prompt/judge_*.txt, never in this file.
"""
import argparse, base64, hashlib, json, os, pathlib, re, sys, urllib.request

HERE = pathlib.Path(__file__).parent
PHOTOS = HERE / "photos"
MODEL = os.environ.get("JUDGE_MODEL", "google/gemini-2.5-flash")
URL = "https://openrouter.ai/api/v1/chat/completions"
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


def ask(prompt_file, labelled, temperature=0.0):
    """labelled is [(caption, path), ...]. The caption goes in front of each image as its own
    text block: three bare images in a row and the model loses track of which is which — it
    told us two visibly different drawings were identical."""
    content = [{"type": "text", "text": (HERE / "prompt" / prompt_file).read_text().strip()}]
    for caption, path in labelled:
        content.append({"type": "text", "text": caption})
        content.append({"type": "image_url", "image_url": {"url": data_url(path)}})
    body = json.dumps({"model": MODEL, "temperature": temperature,
                       "messages": [{"role": "user", "content": content}]}).encode()
    req = urllib.request.Request(URL, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
        "HTTP-Referer": "https://github.com/ESCRI11/bicycle-rl", "X-Title": "bicycle-rl"})
    with urllib.request.urlopen(req, timeout=180) as r:
        text = json.load(r)["choices"][0]["message"]["content"]
    m = FENCE.search(text)
    return json.loads(m.group(1) if m else text)


ITEMS = ("two_wheels", "equal_wheels", "closed_frame", "steering", "drivetrain")


def checklist(png, photo=None):
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
    if "OPENROUTER_API_KEY" not in os.environ:
        sys.exit("OPENROUTER_API_KEY not set")
    out = checklist(a.images[0]) if a.mode == "checklist" else pairwise(*a.images[:2])
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
