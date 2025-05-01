import json
from pathlib import Path


def get_summary(self):
    """Return raw per-iteration data only (no statistics or bootstrap)."""
    return {
        "metadata": self.results.get("metadata", {}),
        "framework": self.framework,
        "test_suite": self.test_suite,
        "runs": self.results["runs"],
    }


def save_results(self):
    """Save summary (with raw runs) to a single JSON file per framework."""
    summary = self.get_summary()
    output_file = self.output_dir / f"{self.test_suite}_{self.framework}.json"
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)
    return output_file
