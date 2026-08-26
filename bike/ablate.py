#!/usr/bin/env python3
"""Break the reference bicycle in one specific way at a time -> out/ladder/*.js

    python3 ablate.py && python3 render.py out/ladder/*.js -o out/ladder

Calibrating a pairwise judge on the baseline is calibrating on coin flips: fifty piles of
scribbles have no ground-truth ordering. These do. Each variant is worse than the gold in
exactly one respect, and each respect is one item on the checklist, so (gold, variant) is a
pair whose answer needs no human opinion. A judge that prefers unequal wheels is disqualified.

Substitutions are exact text, and every one asserts it actually fired — a silent no-op would
quietly turn a ladder rung into a duplicate of the gold.
"""
import pathlib, shutil

HERE = pathlib.Path(__file__).parent
GOLD = HERE / "gold" / "bike_01.js"
OUT = HERE / "out" / "ladder"

WHEELS = """  for (const [hx, hy] of [rear, front]) {
    brush.circle(hx, hy, R, false);
    brush.circle(hx, hy, R - 9, false);               // tyre wall
    brush.circle(hx, hy, 7, false);                   // hub
    for (let i = 0; i < 12; i++) {
      const a = (TWO_PI / 12) * i + 0.2;
      brush.line(hx + cos(a) * 7, hy + sin(a) * 7,
                 hx + cos(a) * (R - 12), hy + sin(a) * (R - 12));
    }
  }"""
SPOKES = """    for (let i = 0; i < 12; i++) {
      const a = (TWO_PI / 12) * i + 0.2;
      brush.line(hx + cos(a) * 7, hy + sin(a) * 7,
                 hx + cos(a) * (R - 12), hy + sin(a) * (R - 12));
    }
"""
FRAME = """  for (const [a, b] of [[St, BB], [BB, Hb], [St, Ht], [BB, rear], [St, rear],
                        [Hb, front], [Ht, Hb]]) {"""
# the tubes are drawn twice: fat marker paint first, ink linework over it. An ablation has
# to remove BOTH or the paint layer quietly puts the tube back.
PAINT_DOWNTUBE = " [[-20, 112], [138, 18]],"
PAINT_FORK = ", [[138, 18], [150, 120]]"
CHAIN = """  brush.circle(BB[0], BB[1], 26, false);
  brush.circle(rear[0], rear[1], 12, false);          // sprocket
  brush.line(rear[0], rear[1] - 12, BB[0], BB[1] - 26);
  brush.line(rear[0], rear[1] + 12, BB[0], BB[1] + 26);
"""

# name -> (checklist item it breaks, [(find, replace), ...])
ABLATIONS = {
    "wheels-unequal": ("wheels the same size", [
        (WHEELS, WHEELS.replace("of [rear, front]", "of [[...rear, R], [...front, R * 0.6]]")
                       .replace("[hx, hy]", "[hx, hy, r]")
                       .replace(", R,", ", r,").replace("R - 9", "r - 9").replace("R - 12", "r - 12")),
    ]),
    "one-wheel": ("two wheels, both drawn", [
        (WHEELS, WHEELS.replace("of [rear, front]", "of [rear]")),
        (FRAME, FRAME.replace("[Hb, front], ", "")),
        (PAINT_FORK, ""),
    ]),
    "frame-open": ("frame closed", [
        (FRAME, FRAME.replace("[BB, Hb], ", "")),          # no down tube, in ink
        (PAINT_DOWNTUBE, ""),                              # and none in paint
    ]),
    "fork-detached": ("bars joined to the front wheel", [
        (FRAME, FRAME.replace("[Hb, front]", "[Hb, [Hb[0] + 14, Hb[1] + 34]]")),
        (PAINT_FORK, ""),
    ]),
    "no-chain": ("chain connecting two rings", [
        (CHAIN, ""),
    ]),
    "no-spokes": ("(cosmetic control — structure intact)", [
        (SPOKES, ""),
    ]),
    "scrambled": ("(bottom anchor — every joint moved)", [
        ("const BB = [-20, 112];", "const BB = [70, 40];"),
        ("const St = [-78, -60], Sb = [-40, 30];", "const St = [-160, 10], Sb = [-40, 30];"),
        ("const Ht = [112, -52], Hb = [138, 18];", "const Ht = [40, -140], Hb = [220, -20];"),
    ]),
}


def main():
    src = GOLD.read_text()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "00-gold.js").write_text(src)
    for name, (breaks, subs) in ABLATIONS.items():
        out = src
        for find, repl in subs:
            assert find in out, f"{name}: pattern not found, gold/bike_01.js has drifted"
            out = out.replace(find, repl, 1)
        assert out != src, f"{name}: substitutions changed nothing"
        (OUT / f"{name}.js").write_text(f"// ablation: {breaks}\n" + out)
        print(f"  {name:16} breaks: {breaks}")
    print(f"\n{len(ABLATIONS) + 1} rungs -> {OUT}")


if __name__ == "__main__":
    main()
