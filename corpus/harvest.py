#!/usr/bin/env python3
"""Harvest hydra sketches from public sources into candidates.jsonl.

    python3 harvest.py                # everything in sources.json
    python3 harvest.py --no-search    # skip GitHub code search (no `gh` needed)

One JSON object per line: {"id", "code", "source", "origin", "license", "needs_input"}.
Deduped by whitespace-normalised code, id = content hash, output sorted => re-running is
idempotent, and curation decisions (keyed on id) survive a re-harvest.

stdlib only. GitHub code search shells out to the `gh` CLI (already authenticated).
"""
import argparse, base64, hashlib, json, re, subprocess, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

q = urllib.parse.quote

HERE = Path(__file__).parent
OUT = HERE / "candidates.jsonl"
UA = {"User-Agent": "bicycle-rl-corpus-harvester"}

SRC_FN = re.compile(r"\b(osc|noise|voronoi|shape|gradient|solid|src|s[0-3])\s*\(")
NEEDS_INPUT = re.compile(r"init(Cam|Screen|Video|Image|Stream)|\ba\.(fft|setBins)")
P5 = re.compile(r"new P5\(|\bp5\.|\.canvas\b")          # p5 running inside hydra as a texture source
# a real sketch renders to a hydra buffer; `.out(someVar)` is a fragment of somebody's framework
OUT_CALL = re.compile(r"\.out\(\s*(o[0-3]\s*)?\)")
JUNK = re.compile(r"^\s*(import |export |module\.exports|require\()|\bawait (?!loadScript)|"
                  r"\.csound\(|function\s+\w+\s*\(|<[a-z]+[ >]", re.M)
# lines that later sketches in the same file still depend on
SETUP = re.compile(r"new P5\(|\.init\(|await loadScript")


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def is_sketch(code):
    return bool(OUT_CALL.search(code) and SRC_FN.search(code)) and not JUNK.search(code) \
        and 20 <= len(code) <= 3000


# --- extractors: file text -> list of candidate code chunks -------------------
def from_md(text):
    return [m.group(1) for m in re.finditer(r"```(?:hydra|js|javascript)?\n(.*?)```", text, re.S)]


def _is_prose(chunk):
    lines = [l for l in chunk.splitlines() if l.strip()]
    return bool(lines) and all(l.lstrip().startswith("//") for l in lines) and len(chunk) > 120


def from_js(text):
    """Blank-line chunks, glued to the render call that follows them.

    Splitting on blank lines alone decapitates p5 sketches: `p1 = new P5()` and
    `s0.init({src: p1.canvas})` sit paragraphs above the `src(s0)...out()` that needs them.
    So accumulate chunks, emit on a render call, and carry the setup lines forward past
    prose and past the emit.
    """
    out, buf = [], []
    for chunk in re.split(r"\n\s*\n", text):
        if not chunk.strip():
            continue
        if _is_prose(chunk):
            buf = [c for c in buf if SETUP.search(c)]
            continue
        buf = (buf + [chunk])[-8:]
        if OUT_CALL.search(chunk):
            out.append("\n\n".join(buf))
            buf = [c for c in buf if SETUP.search(c)]
    return out


def from_editor_json(text):
    # hydra editor examples: base64 of a percent-encoded sketch
    return [urllib.parse.unquote(base64.b64decode(e["code"]).decode("utf-8", "replace"))
            for e in json.loads(text)]


EXTRACT = {"md": from_md, "js": from_js, "editor-json": from_editor_json}


def fmt_of(path):
    return "md" if path.endswith(".md") else "js"


# --- source expansion ---------------------------------------------------------
def expand_tree(t):
    """A repo + a path regex -> one file entry per matching blob."""
    url = f"https://api.github.com/repos/{t['repo']}/git/trees/{t.get('branch', 'HEAD')}?recursive=1"
    tree = json.loads(get(url)).get("tree", [])
    pat, skip = re.compile(t["match"]), re.compile(t.get("skip", r"^$"))
    return [{"url": f"https://raw.githubusercontent.com/{t['repo']}/{t.get('branch','HEAD')}/{q(b['path'])}",
             "source": f"https://github.com/{t['repo']}/blob/{t.get('branch','HEAD')}/{q(b['path'])}",
             "format": fmt_of(b["path"]), "origin": t["origin"], "license": t.get("license", "unknown")}
            for b in tree
            if b["type"] == "blob" and pat.search(b["path"]) and not skip.search(b["path"])]


def expand_search(s):
    cmd = ["gh", "search", "code", s["query"], "--limit", str(s.get("limit", 40)),
           "--json", "path,repository"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(f"  ! gh search failed ({s['query']}): {r.stderr.strip()[:120]}", file=sys.stderr)
        return []
    return [{"url": f"https://raw.githubusercontent.com/{i['repository']['nameWithOwner']}/HEAD/{q(i['path'])}",
             "source": f"https://github.com/{i['repository']['nameWithOwner']}/blob/HEAD/{q(i['path'])}",
             "format": fmt_of(i["path"]), "origin": "github-search", "license": "unknown"}
            for i in json.loads(r.stdout)]


def harvest(entry):
    try:
        chunks = EXTRACT[entry["format"]](get(entry["url"]))
    except Exception as e:  # a dead URL is not worth stopping a 400-file run
        print(f"  ! {entry['url']}: {type(e).__name__}", file=sys.stderr)
        return []
    out = []
    for code in chunks:
        code = code.strip("\n").rstrip()
        if is_sketch(code):
            out.append({"code": code, "source": entry["source"], "origin": entry["origin"],
                        "license": entry["license"], "needs_input": bool(NEEDS_INPUT.search(code)),
                        "uses_p5": bool(P5.search(code))})
    return out


def selftest():
    keep = ["osc(10).kaleid(4).out(o0)", "voronoi()\n  .color(1,0,0)\n  .out()"]
    drop = ["src(sourceOut).invert().out(out)",              # somebody's framework, not a sketch
            "import x from 'y'\nosc().out(o0)",
            "osc(10)",                                        # never rendered
            "console.log('out(o0)')"]                         # no source function
    for c in keep: assert is_sketch(c), c
    for c in drop: assert not is_sketch(c), c
    assert from_md("text\n```hydra\nosc().out()\n```\n") == ["osc().out()\n"]
    assert from_editor_json('[{"code":"JTJGJTJGaGk="}]') == ["//hi"]
    assert len(from_js("osc().out()\n\nnoise().out()")) == 2
    p5file = ("p1 = new P5()\n\n" + "// " + "x" * 130 + "\n\n"
              "s0.init({src: p1.canvas})\n\nsrc(s0).repeat().out(o0)")
    glued = from_js(p5file)[-1]                       # setup survives the prose block
    assert "new P5()" in glued and "s0.init" in glued and "src(s0)" in glued, glued
    assert is_sketch("await loadScript('p5.js')\nsrc(s0).out(o0)")   # hydra idiom, not framework code
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-search", action="store_true", help="skip `gh search code` sources")
    ap.add_argument("--selftest", action="store_true", help="check the extractors and the filter")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    src = json.loads((HERE / "sources.json").read_text())

    entries = list(src.get("files", []))
    for t in src.get("trees", []):
        found = expand_tree(t)
        print(f"tree {t['repo']}: {len(found)} files")
        entries += found
    if not args.no_search:
        for s in src.get("searches", []):
            found = expand_search(s)
            print(f"search {s['query']!r}: {len(found)} files")
            entries += found

    seen_urls, uniq = set(), []
    for e in entries:
        if e["url"] not in seen_urls:
            seen_urls.add(e["url"])
            uniq.append(e)
    print(f"\nfetching {len(uniq)} files...")

    by_id = {}
    if OUT.exists():  # keep what previous runs found; search results drift
        by_id = {r["id"]: r for r in map(json.loads, OUT.read_text().splitlines()) if r.strip()}
    before = len(by_id)

    with ThreadPoolExecutor(max_workers=8) as pool:
        for sketches in pool.map(harvest, uniq):
            for s in sketches:
                key = re.sub(r"\s+", "", s["code"])
                s["id"] = hashlib.sha1(key.encode()).hexdigest()[:10]
                by_id.setdefault(s["id"], s)

    OUT.write_text("".join(json.dumps(by_id[k], ensure_ascii=False) + "\n" for k in sorted(by_id)))

    tally = {}
    for r in by_id.values():
        tally[r["origin"]] = tally.get(r["origin"], 0) + 1
    print(f"\n{len(by_id)} sketches in {OUT.name} (+{len(by_id) - before} new)")
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {v:4d}  {k}")
    print(f"  {sum(r['needs_input'] for r in by_id.values()):4d}  need camera/audio/video input")
    print(f"  {sum(r.get('uses_p5') for r in by_id.values()):4d}  use p5 inside hydra")


if __name__ == "__main__":
    main()
