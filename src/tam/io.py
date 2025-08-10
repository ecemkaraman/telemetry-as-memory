import csv, os, json


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def write_rows(path: str, rows: list[dict]):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def write_json(path: str, obj: dict):
    ensure_dir(os.path.dirname(path))
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
