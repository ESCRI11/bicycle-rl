#!/usr/bin/env bash
# One-shot setup for a fresh rented GPU box. Tested on Prime Intellect A100 80GB,
# Ubuntu 22.04, passwordless sudo, ~700 GB disk. Run it ON the box:
#
#   ssh ubuntu@<ip> 'bash -s' < box/setup.sh
#
# Takes ~10 min, most of it pip pulling torch for vllm.
set -euo pipefail

sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nodejs wget nvtop python3.10-venv
# python3.10-venv: without it `python3 -m venv` builds an environment with no pip,
# silently, and every install into it fails with "No such file or directory"

# node is only needed for `node --check` (the compile gate), any version does.
# chrome is the render backend on a normal machine; on this class of VM its CLI
# --screenshot mode core-dumps (crashpad CHECK, `trap int3` in dmesg) even with
# --no-sandbox --disable-gpu --single-process. Playwright drives the same engine over a
# pipe and works, so we install both and use RENDER_BACKEND=playwright here.
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/chrome.deb

pip3 install -q --upgrade pip
pip3 install -q vllm playwright peft accelerate gepa
# accelerate: transformers needs it for device_map.
#
# hpsv3 goes in its OWN venv: it pins torch 2.5 and drags vLLM back to 0.7, which predates
# Qwen2.5-VL support and silently breaks the judge. bike/hps.py talks to it over a pipe.
python3 -m venv "$HOME/hpsenv"
"$HOME/hpsenv/bin/pip" install -q --upgrade pip
"$HOME/hpsenv/bin/pip" install -q hpsv3 matplotlib tensorboard  # both undeclared hpsv3 deps
python3 -m playwright install chromium

echo
echo "setup done:"
echo "  chrome     $(google-chrome --version)"
echo "  node       $(node -v)"
echo "  vllm       $(python3 -c 'import vllm;print(vllm.__version__)')"
echo "  gpu        $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
echo
echo "always export RENDER_BACKEND=playwright on this box"
