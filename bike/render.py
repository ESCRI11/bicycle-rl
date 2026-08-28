#!/usr/bin/env python3
"""Render p5.brush sketches to PNG with headless chrome. No npm, no pip.

    python3 render.py gold/*.js          # -> out/<name>.png
    python3 render.py out/gen_*.js -o out

Each sketch file defines one function `paint()`; the harness (template.html) owns the
canvas, the paper colour and the seeds. Syntax errors are caught by `node --check` before
we pay for a browser; runtime errors are painted onto the image as a red banner.
"""
import argparse, pathlib, re, shutil, subprocess, sys

HERE = pathlib.Path(__file__).parent
CHROME = next((c for c in ("google-chrome", "chromium", "chromium-browser")
               if shutil.which(c)), None)
FLAGS = ["--headless=new", "--hide-scrollbars", "--window-size=700,700",
         "--enable-unsafe-swiftshader", "--virtual-time-budget=15000", "--dump-dom"]
# the harness paints runtime errors into a #fail div; --dump-dom hands them back as text,
# which is what the compile gate reads. Skip the template's own literal.
FAIL = re.compile(r'id="fail">([^<]*)')


def render(js: pathlib.Path, out_dir: pathlib.Path) -> tuple[pathlib.Path, str]:
    syntax = subprocess.run(["node", "--check", js], capture_output=True, text=True)
    if syntax.returncode:
        return None, syntax.stderr.strip().splitlines()[-1][:200]

    page = HERE / f".render-{js.stem}.html"      # next to lib/, so relative paths resolve
    page.write_text((HERE / "template.html").read_text()
                    .replace("__SKETCH__", str(js.resolve())))
    png = out_dir / f"{js.stem}.png"
    try:
        r = subprocess.run([CHROME, *FLAGS, f"--screenshot={png.resolve()}",
                            f"file://{page.resolve()}"],
                           capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        # a sketch can loop forever; that is a failed render, not a reason to kill the
        # caller. GEPA lost a whole run to this propagating out of one evaluation.
        return None, "chrome timed out after 90s (runaway sketch?)"
    finally:
        page.unlink(missing_ok=True)
    if not png.exists():
        return None, (r.stderr or "chrome wrote no png")[-200:]
    errs = [m for m in FAIL.findall(r.stdout) if "msg" not in m]
    if errs:
        (out_dir / f"{js.stem}.err").write_text(errs[-1] + "\n")
        return png, errs[-1][:160]                     # rendered, but it threw
    return png, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sketches", nargs="+", type=pathlib.Path)
    ap.add_argument("-o", "--out", type=pathlib.Path, default=HERE / "out")
    a = ap.parse_args()
    if not CHROME:
        sys.exit("no chrome/chromium on PATH")
    a.out.mkdir(parents=True, exist_ok=True)
    ok = 0
    for js in a.sketches:
        png, err = render(js, a.out)
        print(f"{'FAIL' if err else ' ok '}  {js.name:24} {err or png}")
        ok += not err
    print(f"\n{ok}/{len(a.sketches)} rendered clean")


if __name__ == "__main__":
    main()
