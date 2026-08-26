#!/usr/bin/env python3
"""Contact sheet: many images -> one PNG you can actually look at.

    python3 sheet.py photos/*.jpg -o out/photos.png
    python3 sheet.py out/gen_*.png -o out/batch.png --cols 6

Same trick as render.py: an HTML grid, screenshotted by headless chrome. Used for culling
the photo pool now, and for eyeballing a batch of generated bicycles later.
"""
import argparse, html, pathlib, subprocess, shutil, sys

HERE = pathlib.Path(__file__).parent
CHROME = next((c for c in ("google-chrome", "chromium", "chromium-browser")
               if shutil.which(c)), None)

CSS = """body{margin:0;background:#111;color:#999;font:11px ui-monospace,monospace;
 display:grid;gap:4px;padding:4px}
figure{margin:0;min-width:0}  /* else long captions blow the grid up */img{width:100%;aspect-ratio:4/3;object-fit:contain;background:#000;display:block}
figcaption{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:2px}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+", type=pathlib.Path)
    ap.add_argument("-o", "--out", type=pathlib.Path, default=HERE / "out" / "sheet.png")
    ap.add_argument("--cols", type=int, default=8)
    ap.add_argument("--cell", type=int, default=190, help="cell width in px")
    a = ap.parse_args()
    if not CHROME:
        sys.exit("no chrome/chromium on PATH")

    rows = -(-len(a.images) // a.cols)
    page = HERE / ".sheet.html"
    page.write_text(
        f"<meta charset=utf-8><style>{CSS}\nbody{{grid-template-columns:repeat({a.cols},1fr)}}</style>"
        + "".join(f'<figure><img src="{i.resolve()}"><figcaption>{html.escape(i.name)}</figcaption></figure>'
                  for i in a.images))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([CHROME, "--headless=new", "--hide-scrollbars",
                        f"--window-size={a.cols * a.cell},{rows * int(a.cell * 0.83) + 20}",
                        "--virtual-time-budget=8000", f"--screenshot={a.out.resolve()}",
                        f"file://{page.resolve()}"], capture_output=True, timeout=120)
    finally:
        page.unlink(missing_ok=True)
    print(f"{len(a.images)} images -> {a.out}")


if __name__ == "__main__":
    main()
