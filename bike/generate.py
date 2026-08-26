#!/usr/bin/env python3
"""Sample sketches from any OpenAI-compatible endpoint -> out/gen_NN.js.

    export OPENAI_BASE_URL=http://localhost:8000/v1   # vLLM, Together, DeepInfra, ...
    export OPENAI_API_KEY=...
    python3 generate.py -n 50 --model Qwen/Qwen2.5-Coder-7B-Instruct

Then: python3 render.py out/gen_*.js && python3 sheet.py out/gen_*.png -o out/batch.png

The prompt lives in prompt/system.txt and prompt/user.txt, never in this file — GEPA will
rewrite system.txt later, and a batch should always be traceable to the prompt that made it
(each run copies both into out/<run>/prompt/).
"""
import argparse, json, os, pathlib, re, shutil, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).parent
FENCE = re.compile(r"```(?:javascript|js)?\n(.*?)```", re.S)


def complete(prompt_dir, model, temperature, n):
    body = json.dumps({
        "model": model,
        "temperature": temperature,
        "max_tokens": 1600,
        "messages": [
            {"role": "system", "content": (prompt_dir / "system.txt").read_text().strip()},
            {"role": "user", "content": (prompt_dir / "user.txt").read_text().strip()},
        ],
    }).encode()
    req = urllib.request.Request(
        os.environ["OPENAI_BASE_URL"].rstrip("/") + "/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY", "-")})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def clean(text):
    """Models wrap code in fences however much you ask them not to."""
    m = FENCE.search(text)
    code = m.group(1) if m else text
    return code.strip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=50, help="how many samples")
    ap.add_argument("--model", default=os.environ.get("MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct"))
    ap.add_argument("--temp", type=float, default=1.0)
    ap.add_argument("--out", type=pathlib.Path, default=HERE / "out" / "baseline")
    ap.add_argument("--prompt", type=pathlib.Path, default=HERE / "prompt")
    ap.add_argument("--workers", type=int, default=8,
                    help="parallel requests; keep it low (2) against a CPU-only ollama")
    a = ap.parse_args()
    if "OPENAI_BASE_URL" not in os.environ:
        sys.exit("set OPENAI_BASE_URL (and OPENAI_API_KEY) first")

    a.out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(a.prompt, a.out / "prompt", dirs_exist_ok=True)   # what made this batch
    (a.out / "run.json").write_text(json.dumps(
        {"model": a.model, "temperature": a.temp, "n": a.n}, indent=1) + "\n")

    def one(i):
        try:
            code = clean(complete(a.prompt, a.model, a.temp, 1))
        except Exception as e:
            return f"gen_{i:03d}: {type(e).__name__} {e}"
        (a.out / f"gen_{i:03d}.js").write_text(code)
        return f"gen_{i:03d}: {len(code)} chars" + ("" if "function paint" in code else "  NO paint()")

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for line in pool.map(one, range(a.n)):
            print(line, flush=True)
    print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()
