import argparse
import os
from pathlib import Path

from benchmarking import generate_benchmarks
from reporting import generate_reports


def main():
    parser = argparse.ArgumentParser(description="Run benchmarking and/or reporting pipelines.")
    parser.add_argument('--bench', action='store_true', help='Execute benchmarks only')
    parser.add_argument('--report', action='store_true', help='Generate reports only')
    # Benchmarking options
    parser.add_argument('--path', '-p', default='sample_cases', help='Root directory with example suites')
    parser.add_argument('--frameworks', '-f', nargs='+', help='Frameworks to benchmark')
    parser.add_argument('--iterations', '-n', type=int, default=10, help='Number of iterations per run')
    parser.add_argument('--warmup', '-w', type=int, default=5, help='Warmup runs before measurement')
    parser.add_argument('--output-dir', '-o', default='results/raw_metrics', help='Directory for raw JSON outputs')
    # Reporting options
    parser.add_argument('--results-dir', default='results/raw_metrics', help='Directory containing raw JSON results')
    parser.add_argument('--report-dir', default='results/reports', help='Output directory for reports and plots')
    args = parser.parse_args()

    # Default to run both if no flag provided
    run_bench = args.bench or not args.report and not args.bench
    run_report = args.report or not args.report and not args.bench

    if run_bench:
        print("Starting benchmarks...")
        generate_benchmarks(
            path=args.path,
            frameworks=args.frameworks,
            iterations=args.iterations,
            warmup=args.warmup,
            output_dir=args.output_dir,
        )
    if run_report:
        print("Generating reports...")
        # Ensure report directory exists
        Path(args.report_dir).mkdir(parents=True, exist_ok=True)
        generate_reports(results_dir=args.results_dir, report_dir=args.report_dir)


if __name__ == '__main__':
    main()
