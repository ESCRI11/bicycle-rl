# visuals-RL

LoRA fine-tune of an LLM to write [hydra](https://hydra.ojack.xyz/) live-coding visuals.

Goal: prompt in plain language ("slow pulsing kaleidoscope, teal"), get runnable hydra JS
that you paste into the editor.

## Layout

- `data/` — sketch corpus: `{"prompt": ..., "code": ...}` pairs (jsonl)
- `train/` — LoRA config + training script
- `eval/` — render sketches headlessly, eyeball the grid

Nothing here yet beyond the plan.

## Notes

Hydra is a JS DSL, so the base model already knows the syntax shape; the LoRA is
for style and for the operators it hallucinates wrong (`modulateScrollY`, `kaleid`,
feedback via `src(o0)`).
