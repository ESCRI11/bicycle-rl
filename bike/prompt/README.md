# prompt

`system.txt` is **the** prompt. Everything else here is either an archive or a judge prompt.

| file | what it is |
|---|---|
| `system.txt` | canonical, v2.1 — the prompt runs 2 and 3 trained against |
| `user.txt` | the fixed user turn, unchanged across all three runs |
| `system_v1_archive.txt` | v1 — run 1 trained against this |
| `system_v2.0_archive.txt` | v2.0 draft, superseded by v2.1 before any run used it |
| `judge_*.txt`, `judge_items.json` | the judge's prompts and the tiered checklist |

Nothing loads a file with `archive` in its name. Keep it that way: the worst bug of the
project (BITACORA 024) was a collapse test that read v1 while the adapter had been trained on
v2.1, and it reported the exact opposite of the truth. A prompt directory with two plausible
candidates in it is how that happens.

The prompt each run actually used is copied into `results/run<N>-320steps/prompt/`, so a run's
archive is readable without working out which version was canonical on which date.
