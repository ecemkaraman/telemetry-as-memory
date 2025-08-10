.PHONY: eval run ingestion features learning inference

eval:
	python src/cli/run_eval.py

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
