#!/usr/bin/env bash
set -euo pipefail

mkdir -p results/csv results/metrics results/figs

python -m src.cli.run_eval --config configs/base.yaml --mode baseline --out-prefix baseline
python -m src.cli.run_eval --config configs/base.yaml --mode closed   --out-prefix closed

python scripts/plot_results.py
