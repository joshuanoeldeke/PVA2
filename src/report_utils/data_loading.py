import json
from pathlib import Path
import pandas as pd

def load_results(results_dir):
    """Load JSON result files into a pandas DataFrame (recursively)."""
    records = []
    for file in Path(results_dir).rglob("*.json"):
        data = json.load(open(file))
        suite = data.get("test_suite")
        fw = data.get("framework")
        for run in data.get("runs", []):
            rec = {**run, "framework": fw, "test_suite": suite}
            records.append(rec)
    return pd.DataFrame.from_records(records)
