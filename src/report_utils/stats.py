import pandas as pd
from scipy import stats

def perform_pairwise_tests(df, alpha=0.05):
    """Perform pairwise t-tests between frameworks for each test suite."""
    results = []
    suites = df["test_suite"].unique()
    for suite in suites:
        sub = df[df["test_suite"] == suite]
        frameworks = sub["framework"].unique()
        for i, f1 in enumerate(frameworks):
            for f2 in frameworks[i+1:]:
                a = sub[sub["framework"] == f1]["execution_time_seconds"]
                b = sub[sub["framework"] == f2]["execution_time_seconds"]
                stat, p = stats.ttest_ind(a, b, equal_var=False)
                results.append({
                    "test_suite": suite,
                    "framework1": f1,
                    "framework2": f2,
                    "t_stat": stat,
                    "p_value": p,
                    "significant": p < alpha
                })
    return pd.DataFrame(results)
