import sys
import os
from pathlib import Path
# Add the project root to sys.path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from src.metrics import PerformanceMetrics

def main():
    parser = argparse.ArgumentParser(description="Benchmark example code suites against test frameworks")
    parser.add_argument("--path", "-p", default="test_cases",
                        help="Root directory containing example code subdirectories (defaults to 'test_cases')")
    parser.add_argument("--frameworks", "-f", nargs='+', default=["unittest", "pytest"],
                        help="List of test frameworks to benchmark (e.g. unittest pytest)")
    parser.add_argument("--iterations", "-n", type=int, default=10,
                        help="Number of measurement iterations per suite")
    parser.add_argument("--warmup", "-w", type=int, default=5,
                        help="Number of warmup runs before measurement")
    parser.add_argument("--output-dir", "-o", default="results/raw_metrics",
                        help="Directory to save result JSON files (defaults to results/raw_metrics)")
    args = parser.parse_args()

    root = Path(args.path)
    # detect if path itself is a single suite by presence of both framework test files
    single_unittest = root / f"test_{root.name}_unittest.py"
    single_pytest = root / f"test_{root.name}_pytest.py"
    if single_unittest.exists() and single_pytest.exists():
        suite_dirs = [root]
    else:
        # include only actual example subdirectories (skip __pycache__, hidden dirs)
        suite_dirs = sorted(
            [d for d in root.iterdir()
             if d.is_dir() and not d.name.startswith("__") and not d.name.startswith('.')]
        )
    print(f"Discovered {len(suite_dirs)} example suites in '{args.path}'.")

    for suite_dir in suite_dirs:
        suite_name = suite_dir.name
        print(f"\nRunning suite '{suite_name}'...")
        for fw in args.frameworks:
            test_file = suite_dir / f"test_{suite_name}_{fw}.py"
            if not test_file.exists():
                print(f"Skipping {fw} for suite '{suite_name}': {test_file} not found.")
                continue
            print(f"Running {fw} on {test_file}...")
            metrics = PerformanceMetrics(fw, suite_name, output_dir=args.output_dir)
            # ensure examples parent dir is on PYTHONPATH for proper imports
            parent_dir = suite_dir.parent
            env_path = f"{parent_dir}{os.pathsep}{os.environ.get('PYTHONPATH','')}"
            os.environ['PYTHONPATH'] = env_path
            cmd = [sys.executable]
            if fw.lower() == "pytest":
                cmd += ["-m", "pytest", str(test_file)]
            else:
                cmd += ["-m", "unittest", str(test_file)]
            metrics.measure_performance_subprocess(cmd,
                                                 iterations=args.iterations,
                                                 warmup_runs=args.warmup)
            output_file = metrics.save_results()
            print(f"Results saved to {output_file}\n")

if __name__ == "__main__":
    main()
