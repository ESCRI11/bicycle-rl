#!/usr/bin/env python3
"""Stage 0 of v3: does the trained policy still sample colour at all?

    python3 collapse_test.py --lora run/lora -n 50

RL reinforces only what the policy samples. Run 2 drove `brush.fill` from 115/128 to 4/128
because nothing paid for paint; if that probability is now ~0, an aesthetic reward has
nothing to grab and v3 should start from the base model instead of warm-starting.

Compares three conditions on the same prompt: the base model, the adapter at temperature
1.0, and the adapter at 1.2 — temperature being the cheapest way to ask whether the
behaviour is suppressed or extinct.
"""
import argparse, pathlib, re, sys, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen2.5-Coder-7B-Instruct"
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import generate


def sample(model, tok, prompt, n, temp, batch=16, max_new=1000):
    out = []
    while len(out) < n:
        k = min(batch, n - len(out))
        enc = tok([prompt] * k, return_tensors="pt").to("cuda")
        with torch.no_grad():
            gen = model.generate(**enc, do_sample=True, temperature=temp, top_p=0.95,
                                 max_new_tokens=max_new, pad_token_id=tok.eos_token_id)
        out += [generate.clean(tok.decode(r[enc.input_ids.shape[1]:], skip_special_tokens=True))
                for r in gen]
    return out


def stats(codes):
    fill = sum(1 for c in codes if "brush.fill(" in c)
    cols = [len(set(re.findall(r"#[0-9a-fA-F]{6}", c))) for c in codes]
    return fill, sum(cols) / len(cols), sorted(len(c) for c in codes)[len(codes) // 2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lora", type=pathlib.Path, required=True)
    ap.add_argument("-n", type=int, default=50)
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(BASE)
    prompt = tok.apply_chat_template(
        [{"role": "system", "content": (HERE / "prompt/system.txt").read_text().strip()},
         {"role": "user", "content": (HERE / "prompt/user.txt").read_text().strip()}],
        tokenize=False, add_generation_prompt=True)

    base = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda").eval()
    print(f"{'condition':28} {'uses fill':>10}  {'colours':>8}  {'median code':>12}")
    f, c, l = stats(sample(base, tok, prompt, a.n, 1.0))
    print(f"{'base model, temp 1.0':28} {f:>4}/{a.n:<5} {c:>8.1f}  {l:>12}")

    from peft import PeftModel
    tuned = PeftModel.from_pretrained(base, str(a.lora)).eval()
    for temp in (1.0, 1.2):
        f, c, l = stats(sample(tuned, tok, prompt, a.n, temp))
        print(f"{'trained adapter, temp ' + str(temp):28} {f:>4}/{a.n:<5} {c:>8.1f}  {l:>12}")
        if temp == 1.0:
            verdict = f / a.n
    print()
    print(f"VERDICT: {'suppressed — warm-start from the adapter' if verdict >= 0.10 else 'extinct — start v3 from the base model'}"
          f"  ({verdict*100:.0f}% still paint, threshold 10%)")


if __name__ == "__main__":
    main()
