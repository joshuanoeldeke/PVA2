import os
from pathlib import Path
from report_utils.data_loading import load_results
from report_utils.summary import compute_summary
from report_utils.stats import perform_pairwise_tests
from report_utils.plotting import plot_mean_execution_time, plot_boxplots


def generate_reports(results_dir="results", report_dir="reports"):
    """Load results, compute stats, perform tests, and generate visualizations and CSV summaries."""
    os.makedirs(report_dir, exist_ok=True)
    df = load_results(results_dir)
    summary = compute_summary(df)
    summary.to_csv(Path(report_dir) / "summary.csv", index=False)
    tests = perform_pairwise_tests(df)
    tests.to_csv(Path(report_dir) / "pairwise_tests.csv", index=False)
    plot_mean_execution_time(summary, report_dir)
    plot_boxplots(df, report_dir)
    # Create speed comparison GIF
    #animate_speed_comparison(summary, report_dir)
    print(f"Reports generated in {report_dir}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate performance reports from raw results")
    parser.add_argument("--results-dir", "-r", default="results/raw_metrics",
                        help="Directory containing raw JSON result files (defaults to results/raw_metrics)")
    parser.add_argument("--report-dir", "-o", default="results/reports",
                        help="Output directory for reports and plots")
    args = parser.parse_args()
    generate_reports(args.results_dir, args.report_dir)
