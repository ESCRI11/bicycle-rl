#!/usr/bin/env python3
"""Render p5.brush sketches to PNG with headless chrome. No npm, no pip.

    python3 render.py gold/*.js          # -> out/<name>.png
    python3 render.py out/gen_*.js -o out

Each sketch file defines one function `paint()`; the harness (template.html) owns the
canvas, the paper colour and the seeds. Syntax errors are caught by `node --check` before
we pay for a browser; runtime errors are painted onto the image as a red banner.
"""
import argparse, os, pathlib, re, shutil, subprocess, sys

HERE = pathlib.Path(__file__).parent
CHROME = next((c for c in ("google-chrome", "chromium", "chromium-browser")
               if shutil.which(c)), None)
BACKEND = os.environ.get("RENDER_BACKEND", "cli")     # "playwright" where the CLI crashes
FLAGS = ["--headless=new", "--hide-scrollbars", "--window-size=700,700",
         "--enable-unsafe-swiftshader", "--virtual-time-budget=15000", "--dump-dom"]
# the harness paints runtime errors into a #fail div; --dump-dom hands them back as text,
# which is what the compile gate reads. Skip the template's own literal.
FAIL = re.compile(r'id="fail">([^<]*)')


def _render_playwright(page: pathlib.Path, png: pathlib.Path) -> str:
    """Chrome's CLI --screenshot mode core-dumps on some VMs (crashpad CHECK, `trap int3`)
    while the same binary driven over playwright's pipe works fine. Same flags, same
    template, different transport. Launch per call: sync playwright is not thread-safe and
    render is far cheaper than the generation it follows.
    # ponytail: reuse one browser per batch if render time ever matters
    """
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=["--no-sandbox", "--disable-gpu",
                                      "--enable-unsafe-swiftshader"])
        try:
            pg = br.new_page(viewport={"width": 700, "height": 700})
            pg.goto(f"file://{page.resolve()}")
            pg.wait_for_function("window.__done === true", timeout=30000)
            pg.wait_for_timeout(400)                      # let the last frame land
            err = pg.evaluate("() => document.querySelector('#fail')?.textContent || ''")
            pg.screenshot(path=str(png))
            return err
        finally:
            br.close()


def render(js: pathlib.Path, out_dir: pathlib.Path) -> tuple[pathlib.Path, str]:
    syntax = subprocess.run(["node", "--check", js], capture_output=True, text=True)
    if syntax.returncode:
        # node --check prints  path / offending line / caret / "SyntaxError: ..." / stack.
        # The last line is a stack frame; the useful one names the error.
        lines = [l.strip() for l in syntax.stderr.strip().splitlines() if l.strip()]
        msg = next((l for l in lines if "Error" in l), lines[-1] if lines else "syntax error")
        return None, msg[:200]

    page = HERE / f".render-{js.stem}.html"      # next to lib/, so relative paths resolve
    page.write_text((HERE / "template.html").read_text()
                    .replace("__SKETCH__", str(js.resolve())))
    png = out_dir / f"{js.stem}.png"
    if BACKEND == "playwright":
        try:
            err = _render_playwright(page, png)
        except Exception as e:
            return None, f"{type(e).__name__}: {str(e)[:160]}"
        finally:
            page.unlink(missing_ok=True)
        if err:
            (out_dir / f"{js.stem}.err").write_text(err + "\n")
        return (png if png.exists() else None), (err[:160] if err else "")
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
    if not CHROME and BACKEND != "playwright":
        sys.exit("no chrome/chromium on PATH (or set RENDER_BACKEND=playwright)")
    a.out.mkdir(parents=True, exist_ok=True)
    ok = 0
    for js in a.sketches:
        png, err = render(js, a.out)
        print(f"{'FAIL' if err else ' ok '}  {js.name:24} {err or png}")
        ok += not err
    print(f"\n{ok}/{len(a.sketches)} rendered clean")


if __name__ == "__main__":
    main()
