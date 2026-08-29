#!/usr/bin/env python3
"""Phase 1: sample a batch of sketches from the current policy, then exit.

Exits so the GPU is free for the judge. Everything needed by the later phases is written to
disk: the code, and the exact token ids that produced it (recomputing them from text risks
a tokenisation mismatch, and the gradient would be wrong in a way nothing would catch).
"""
import argparse, json, pathlib, sys, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen2.5-Coder-7B-Instruct"
HERE = pathlib.Path(__file__).resolve().parent.parent          # bike/
sys.path.insert(0, str(HERE))
import generate                                                # reuse clean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("-n", type=int, default=128)
    ap.add_argument("--lora", type=pathlib.Path)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--max-new", type=int, default=1200)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    if a.lora and a.lora.exists():
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, str(a.lora))
    model.eval()

    prompt = tok.apply_chat_template(
        [{"role": "system", "content": (HERE / "prompt/system.txt").read_text().strip()},
         {"role": "user", "content": (HERE / "prompt/user.txt").read_text().strip()}],
        tokenize=False, add_generation_prompt=True)
    prompt_ids = tok(prompt, return_tensors="pt").input_ids[0]

    completions, i = [], 0
    while i < a.n:
        k = min(a.batch, a.n - i)
        batch = tok([prompt] * k, return_tensors="pt").to("cuda")
        with torch.no_grad():
            out = model.generate(**batch, do_sample=True, temperature=1.0, top_p=0.95,
                                 max_new_tokens=a.max_new, pad_token_id=tok.eos_token_id)
        for row in out:
            comp = row[batch.input_ids.shape[1]:]
            comp = comp[comp != tok.eos_token_id]
            completions.append(comp.cpu())
            (a.out / f"gen_{i:03d}.js").write_text(generate.clean(tok.decode(comp)))
            i += 1
        print(f"{i}/{a.n}", flush=True)

    torch.save({"prompt_ids": prompt_ids, "completions": completions}, a.out / "tokens.pt")
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
