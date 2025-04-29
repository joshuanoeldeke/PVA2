import numpy as np

def compute_summary(df):
    """Compute summary statistics and confidence intervals grouped by suite and framework."""
    grp = df.groupby(["test_suite", "framework"])
    summary = grp["execution_time_seconds"].agg(["count", "mean", "median", "std"]).reset_index()
    summary["sem"] = summary["std"] / np.sqrt(summary["count"])
    summary["ci95"] = summary["sem"] * 1.96
    return summary
