.PHONY: eval run ingestion features learning inference

eval:
	PYTHONPATH=src python -m cli.run_eval --config configs/base.yaml --mode baseline --out-prefix baseline && \
	PYTHONPATH=src python -m cli.run_eval --config configs/base.yaml --mode closed   --out-prefix closed && \
	python scripts/plot_results.py

run:
	python src/main.py

ingestion:
	python src/ingestion.py

features:
	python src/features.py

learning:
	python src/learning.py

inference:
	python src/inference.py
