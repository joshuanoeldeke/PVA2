import sys
import os
from pathlib import Path
import argparse

from benchmarking_utils.core import PerformanceMetrics


def generate_benchmarks(path='sample_cases', frameworks=None, iterations=10, warmup=5, output_dir='results/raw_metrics'):
    """Discover example suites and measure performance for each specified framework."""
    root = Path(path)
    # Determine if single-suite or multi-suite
    single_unittest = root / f"test_{root.name}_unittest.py"
    single_pytest = root / f"test_{root.name}_pytest.py"
    if single_unittest.exists() and single_pytest.exists():
        suite_dirs = [root]
    else:
        suite_dirs = sorted(
            [d for d in root.iterdir() if d.is_dir() and not d.name.startswith('.')]
        )
    print(f"Discovered {len(suite_dirs)} example suites in '{path}'.")

    for suite_dir in suite_dirs:
        suite_name = suite_dir.name
        print(f"\nRunning suite '{suite_name}'...")
        for fw in (frameworks or ['unittest', 'pytest']):
            test_file = suite_dir / f"test_{suite_name}_{fw}.py"
            if not test_file.exists():
                print(f"Skipping {fw} for suite '{suite_name}': {test_file} not found.")
                continue
            print(f"Running {fw} on {test_file}...")
            metrics = PerformanceMetrics(fw, suite_name, output_dir)
            # Ensure project imports resolve
            parent_dir = str(suite_dir.parent)
            os.environ['PYTHONPATH'] = parent_dir + os.pathsep + os.environ.get('PYTHONPATH', '')
            cmd = [sys.executable]
            if fw.lower() == 'pytest':
                cmd += ['-m', 'pytest', str(test_file)]
            else:
                cmd += ['-m', 'unittest', str(test_file)]
            metrics.measure(cmd, iterations=iterations, warmup_runs=warmup)
            out = metrics.save_results()
            print(f"Results saved to {out}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate raw performance metrics for test suites.")
    parser.add_argument('--path', '-p', default='sample_cases', help='Root directory with example suites')
    parser.add_argument('--frameworks', '-f', nargs='+', help='Frameworks to benchmark')
    parser.add_argument('--iterations', '-n', type=int, default=10, help='Number of iterations per run')
    parser.add_argument('--warmup', '-w', type=int, default=5, help='Warmup runs before measurement')
    parser.add_argument('--output-dir', '-o', default='results/raw_metrics', help='Directory for raw JSON outputs')
    args = parser.parse_args()
    generate_benchmarks(args.path, args.frameworks, args.iterations, args.warmup, args.output_dir)