#!/bin/bash
set -e

# ========= Scenario 1: Drift =========
echo "Running Scenario 1: Drift..."
python src/cli/run_eval.py --config configs/drift.yaml --mode baseline --out-prefix baseline
python src/cli/run_eval.py --config configs/drift.yaml --mode closed --out-prefix closed
python scripts/plot_results.py --scenario drift --results-root results --drift-tick 300

# ========= Scenario 2: Poisoned Logs =========
echo "Running Scenario 2: Poisoned Logs..."
python src/cli/run_eval.py --config configs/poison.yaml --mode baseline --out-prefix baseline
python src/cli/run_eval.py --config configs/poison.yaml --mode closed --out-prefix closed
python scripts/plot_results.py --scenario poison --results-root results --drift-tick 300

# ========= Scenario 3: Novel Incident =========
echo "Running Scenario 3: Novel Incident..."
python src/cli/run_eval.py --config configs/novel.yaml --mode baseline --out-prefix baseline
python src/cli/run_eval.py --config configs/novel.yaml --mode closed --out-prefix closed
python scripts/plot_results.py --scenario novel --results-root results --drift-tick 300

echo "✅ All scenarios completed. Plots are in results/<scenario>/figs/"