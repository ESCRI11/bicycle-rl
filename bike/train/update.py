#!/usr/bin/env python3
"""Phase 3: one GRPO update per group, then exit.

GRPO in its plainest form: advantage is the reward normalised within its group, and the
loss is -(advantage x mean token logprob). No PPO clipping and no KL term — a single pass
over freshly sampled data is already on-policy, and the length band in the reward is what
guards against the degenerate long/short collapse.

Adapter and optimiser state live on disk between cycles, so killing the box costs one cycle.
"""
import argparse, json, os, pathlib, statistics, sys, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen2.5-Coder-7B-Instruct"
HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))


def seq_logprob(model, prompt_ids, comp_ids):
    """Mean logprob per completion token. Length-normalised so long sketches are not
    penalised for being long — that is the length band's job, not the gradient's."""
    ids = torch.cat([prompt_ids, comp_ids]).unsqueeze(0).cuda()
    out = model(ids).logits[0, :-1].float().log_softmax(-1)
    tgt = ids[0, 1:]
    lp = out.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
    return lp[len(prompt_ids) - 1:].mean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=pathlib.Path, required=True)
    ap.add_argument("--run", type=pathlib.Path, required=True)
    ap.add_argument("--group", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-5)
    a = ap.parse_args()

    rows = json.loads((a.dir / "rewards.json").read_text())
    blob = torch.load(a.dir / "tokens.pt", weights_only=False)
    prompt_ids, comps = blob["prompt_ids"], blob["completions"]
    lora_dir, opt_path = a.run / "lora", a.run / "opt.pt"

    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model.gradient_checkpointing_enable()
    if lora_dir.exists():
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, str(lora_dir), is_trainable=True)
    else:
        from peft import LoraConfig, get_peft_model
        model = get_peft_model(model, LoraConfig(
            r=16, lora_alpha=32, lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj"]))
    model.train()
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=a.lr)
    if opt_path.exists():
        opt.load_state_dict(torch.load(opt_path, weights_only=False))

    state = json.loads((a.run / "state.json").read_text()) if (a.run / "state.json").exists() else {"step": 0}
    log = (a.run / "log.jsonl").open("a")

    for g0 in range(0, len(rows), a.group):
        chunk = list(range(g0, min(g0 + a.group, len(rows))))
        rw = [rows[i]["reward"] for i in chunk]
        mean, sd = statistics.mean(rw), statistics.pstdev(rw)
        if sd < 1e-6:
            state["step"] += 1                     # every rollout tied: no gradient exists
            continue
        opt.zero_grad()
        for i in chunk:
            adv = (rows[i]["reward"] - mean) / (sd + 1e-4)
            loss = -adv * seq_logprob(model, prompt_ids, comps[i]) / len(chunk)
            loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        state["step"] += 1
        rec = {"step": state["step"], "reward_mean": round(mean, 4), "reward_max": round(max(rw), 4),
               "reward_sd": round(sd, 4),
               "gate": round(sum(rows[i]["parts"]["gate"] for i in chunk) / len(chunk), 3),
               "checklist": round(sum(rows[i]["parts"]["checklist"] for i in chunk) / len(chunk), 3)}
        log.write(json.dumps(rec) + "\n"); log.flush()
        print(rec, flush=True)

    model.save_pretrained(str(lora_dir))
    torch.save(opt.state_dict(), opt_path)
    # keep a periodic snapshot, not just the latest. Run 2 drove colour to extinction by the
    # end (1/50 sampling brush.fill against the base model's 41/50) and an earlier checkpoint
    # — cycle 9 still painted in 77/128 — would have been a warm start worth having. The
    # final adapter was the only one saved, so that option did not exist.
    every = int(os.environ.get("CHECKPOINT_EVERY", "5"))
    if every and (state["step"] // 16) % every == 0:
        snap = a.run / "checkpoints" / f"step_{state['step']:04d}"
        model.save_pretrained(str(snap))
        print(f"checkpoint -> {snap}")
    (a.run / "state.json").write_text(json.dumps(state) + "\n")
    print(f"step {state['step']} -> {lora_dir}")


if __name__ == "__main__":
    main()
