# box — renting a GPU and getting this project running on it

Everything learned the hard way on a Prime Intellect **A100 80 GB** (Ubuntu 22.04, 16 cores,
94 GB RAM, 711 GB disk, passwordless sudo, open outbound internet). Next box should be one
shot.

## Renting

Prime Intellect, on-demand rather than spot for a first run — an eviction mid-training loses
everything, and the price gap is a couple of dollars. Indicative: H100 $2.43/h on-demand,
$0.94/h spot; H200 from $0.47/h; A100 80 GB in between. Paste **your workstation's public
key** (`~/.ssh/id_ed25519.pub`) into the instance's SSH keys field at creation.

Ask for ≥150 GB disk: vLLM, a 7B policy and a 32–72B judge add up fast.

## Bringing it up

```bash
./box/sync.sh ubuntu@<ip>                      # push the repo + the 147 photos (~40 MB)
ssh ubuntu@<ip> 'bash -s' < box/setup.sh       # ~10 min, mostly torch
ssh ubuntu@<ip>
```

Then on the box, **always**:

```bash
export RENDER_BACKEND=playwright
```

## Gotchas, all of them real

**Chrome's CLI screenshot mode core-dumps on this class of VM.** `google-chrome
--headless=new --screenshot` dies with a crashpad CHECK — `trap int3` in `dmesg` — and it
survives none of `--no-sandbox`, `--disable-gpu`, `--disable-dev-shm-usage`,
`--single-process`, `--headless=old`, a fresh `--user-data-dir`, or Playwright's own chromium
build. `/dev/shm` is 48 GB and user namespaces are enabled, so it is not the usual causes.
The **Playwright API drives the same engine over a pipe and works perfectly**, which is why
`render.py` has a `RENDER_BACKEND=playwright` path. Renders come out pixel-identical to the
workstation's.

**`--limit-mm-per-prompt` takes JSON.** `image=3` is rejected with a confusing
`cannot be converted to <function loads>`. Use `'{"image":3}'`. Without it vLLM allows one
image per prompt and the pairwise judge (photo + two drawings) fails.

**Don't `pkill` over SSH from a one-liner** that also does the relaunch — killing a pattern
that matches your own shell drops the connection before the relaunch runs, and you are left
with nothing serving. Use the scripts.

**pip installs to `~/.local/bin`, which is not on PATH.** Call `~/.local/bin/vllm`, as
`serve-judge.sh` does.

## Serving the judge

```bash
cd ~/bicycle-rl/bike
nohup ../box/serve-judge.sh > ~/vllm.log 2>&1 &     # Qwen2.5-VL-7B by default
tail -f ~/vllm.log                                   # wait for "Application startup complete"
```

Then point the harness at it — no OpenRouter, no per-call cost:

```bash
export JUDGE_BASE_URL=http://localhost:8000/v1
export JUDGE_MODEL=Qwen/Qwen2.5-VL-7B-Instruct
export RENDER_BACKEND=playwright
python3 ablate.py && python3 render.py out/ladder/*.js -o out/ladder
python3 calibrate.py
```

**The calibration is a gate, not a formality.** A local judge only earns its place if it
clears what the API judges managed: ≥5/7 broken items caught, ≥85% on structural pairs,
<15% position flips. Frontier models already have systematic blind spots here (Gemini cannot
count wheels, Sonnet cannot see an open frame); a small VLM will likely be worse, and a bad
judge at 0.90 weight trains the model toward nonsense while the reward curve climbs.

## Watching the GPU

```bash
nvtop                                    # htop for GPUs: memory, utilisation, per-process
watch -n1 nvidia-smi                     # the classic
nvidia-smi dmon -s um                    # one line/second: utilisation + memory, good for logs
nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv -l 5
```

From the workstation without logging in:

```bash
ssh ubuntu@<ip> 'nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader'
watch -n5 "ssh ubuntu@<ip> nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader"
```

Expect a served 7B VLM to sit near the `--gpu-memory-utilization` fraction you gave it (vLLM
preallocates its KV cache), so **memory used is not a measure of load** — watch the
utilisation column instead.

## Memory budget on 80 GB

| | |
|---|---|
| 7B policy, bf16 | ~14 GB |
| vLLM rollout KV cache | ~10 GB |
| Qwen2.5-VL-7B judge | ~16 GB |
| Qwen2.5-VL-72B-AWQ judge | ~40 GB |

Policy + rollouts + a 7B judge fits comfortably. With the 72B judge it is tight, and a second
GPU purely for the judge costs less than the API calls it replaces.
