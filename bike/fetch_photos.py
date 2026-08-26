#!/usr/bin/env python3
"""Pull real bicycle photos from Wikimedia Commons -> photos/ + photos/credits.json.

    python3 fetch_photos.py            # ~60 side-view bicycle photos
    python3 fetch_photos.py --prune    # only rewrite credits for files still on disk

These are the judge's grounding: what a real bicycle looks like, so the checklist has
something to check against. They are never the pairwise opponent — a photo beats a drawing
every time and the reward saturates.

Everything on Commons is licensed and credited; credits.json keeps title/author/licence per
file, because the blog post has to credit them. stdlib only.
"""
import argparse, json, pathlib, re, time, urllib.parse, urllib.request

HERE = pathlib.Path(__file__).parent
OUT = HERE / "photos"
API = "https://commons.wikimedia.org/w/api.php"
# Commons enforces a robot policy: the UA must name the project and a way to reach you,
# or every download comes back 429 "does not comply with our robot policy". Put your own
# contact here.
UA = {"User-Agent": "bicycle-rl/0.1 (research project, non-commercial; "
                    "https://github.com/ESCRI11) python-urllib/3.12"}

# what Commons photographs side-on is mostly folders and Dutch roadsters, so ask
# explicitly for diamond frames too, or the pool teaches the judge odd proportions
# categories are where the volume is; searches fill in the specific angles we want
CATEGORIES = ["Bicycles", "Road bicycles", "Racing bicycles", "City bicycles",
              "Touring bicycles", "Utility bicycles", "Track bicycles", "Cargo bicycles",
              "Single-speed bicycles", "Bicycles by model",
              # modern road: brand categories are the only place Commons keeps them
              "Trek bicycles", "Giant bicycles", "Bianchi bicycles", "Cannondale bicycles",
              "Specialized bicycles", "Time trial bicycles"]
QUERIES = ["bicycle side view", "bicycle drive side", "roadster bicycle",
           "racing bicycle 1980", "city bicycle whole", "road bicycle drive side",
           "vintage road bicycle", "touring bicycle side", "bicycle 1970s racing",
           "carbon road bicycle", "aero road bicycle", "gravel bicycle side"]
# Commons is full of bike racks, bike lanes and bike shops
REJECT = re.compile(
    # bike racks, bike lanes, bike shops
    r"stand|rack|park|lane|path|shop|sign|helmet|wheel\b|chain\b|pedal\b|frame only|"
    # scanned books: Commons is full of them and they are all covers, not bicycles
    r"\(IA |guide|directory|hand.?book|romance|tour|care and repair|poster|map|diagram|logo|"
    # "diamond frame" also matches NATO map symbology, and Commons has a lot of it
    r"military|symbol|hostile|neutral|report|assessment|regulation|evolution|chart|\.svg",
    re.I)


def get(**params):
    params.update(action="query", format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def download(url, tries=3):
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or n == tries - 1:
                raise
            time.sleep(10 * (n + 1))


def usable(pages, require_word=True):
    """require_word: a search hit must say 'bicycle' somewhere; a category member need not —
    the category already guarantees the topic, and modern bikes are titled 'Trek Madone'."""
    for page in pages:
        title = page["title"].removeprefix("File:")
        if REJECT.search(title):
            continue
        if require_word and not re.search(r"bicycle|bike|velo|fiets|rad\b", title, re.I):
            continue
        if not re.search(r"\.(jpe?g|png)$", title, re.I):     # svg, pdf, video: not photographs
            continue
        ii = (page.get("imageinfo") or [{}])[0]
        if "thumburl" not in ii:                              # category listings carry stubs
            continue
        meta = ii.get("extmetadata", {})
        yield {
            "file": re.sub(r"[^a-z0-9]+", "-", title.rsplit(".", 1)[0].lower()).strip("-")[:60] + ".jpg",
            "title": title,
            "author": re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip(),
            "license": meta.get("LicenseShortName", {}).get("value", "?"),
            "page": ii["descriptionurl"],
            "url": ii["thumburl"],
        }


def search(query, limit=50):
    d = get(generator="search", gsrsearch=query, gsrnamespace=6, gsrlimit=limit,
            prop="imageinfo", iiprop="url|extmetadata", iiurlwidth=640)
    return usable(d.get("query", {}).get("pages", {}).values())


def category(name, limit=100):
    d = get(generator="categorymembers", gcmtitle=f"Category:{name}", gcmtype="file",
            gcmlimit=limit, prop="imageinfo", iiprop="url|extmetadata", iiurlwidth=640)
    return usable(d.get("query", {}).get("pages", {}).values(), require_word=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prune", action="store_true", help="rewrite credits.json only")
    ap.add_argument("--cull", type=pathlib.Path,
                    help="file of rejected filenames (from judge_photos.html) to delete")
    ap.add_argument("--restore", action="store_true",
                    help="re-download whatever credits.json lists but is missing on disk")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    credits_path, culled_path = OUT / "credits.json", OUT / "culled.json"
    credits = json.loads(credits_path.read_text()) if credits_path.exists() else {}
    # a file you deleted stays deleted: the same search will otherwise hand it back forever
    culled = set(json.loads(culled_path.read_text()) if culled_path.exists() else [])

    if args.cull:
        for name in args.cull.read_text().split():
            (OUT / name).unlink(missing_ok=True)
        print(f"culled {len(args.cull.read_text().split())} files")

    if args.restore:
        for name, rec in credits.items():
            if not (OUT / name).exists():
                (OUT / name).write_bytes(download(rec["url"]))
                time.sleep(1.5)

    if not (args.prune or args.cull or args.restore):
        sources = [(f"category:{c}", category) for c in CATEGORIES] + \
                  [(q, search) for q in QUERIES]
        for label, fn in sources:
            found = list(fn(label.removeprefix("category:")))
            print(f"{label!r}: {len(found)} usable", flush=True)
            for rec in found:
                if rec["file"] in culled:
                    continue
                path = OUT / rec["file"]
                if not path.exists():
                    path.write_bytes(download(rec["url"]))
                    time.sleep(1.5)          # commons throttles, and we are guests here
                credits[rec["file"]] = rec

    culled |= {k for k in credits if not (OUT / k).exists()}
    credits = {k: v for k, v in credits.items() if (OUT / k).exists()}
    credits_path.write_text(json.dumps(credits, indent=1, ensure_ascii=False) + "\n")
    culled_path.write_text(json.dumps(sorted(culled), indent=1) + "\n")
    print(f"\n{len(credits)} photos in {OUT}/ ({len(culled)} culled, never refetched)"
          f" — delete the bad ones, then rerun with --prune")


if __name__ == "__main__":
    main()
