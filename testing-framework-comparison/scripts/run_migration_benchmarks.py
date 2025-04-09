from src.framework_comparison.metrics import PerformanceMetrics
from src.framework_comparison.discovery import TestDiscovery
import sys
import tempfile
import shutil
import os


def run_migration_comparison(migration_pair, iterations=100):
    """Run comparison on a before/after migration pair."""
    before_file, after_file = migration_pair

    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy test files to temp directory
        temp_before = os.path.join(temp_dir, "test_before.py")
        temp_after = os.path.join(temp_dir, "test_after.py")

        shutil.copy(before_file, temp_before)
        shutil.copy(after_file, temp_after)

        # Run benchmarks
        test_name = os.path.basename(before_file).split("-")[-1].replace(".py", "")

        unittest_metrics = PerformanceMetrics("unittest", test_name)
        pytest_metrics = PerformanceMetrics("pytest", test_name)

        unittest_cmd = [sys.executable, "-m", "unittest", temp_before]
        pytest_cmd = [sys.executable, "-m", "pytest", temp_after, "-v"]

        unittest_metrics.measure_performance_subprocess(unittest_cmd, iterations)
        pytest_metrics.measure_performance_subprocess(pytest_cmd, iterations)

        return unittest_metrics, pytest_metrics


def main():
    # Path to TestMigrationsInPy dataset
    dataset_path = "path/to/TestMigrationsInPy"

    discovery = TestDiscovery()
    migration_pairs = discovery.discover_migration_pairs(dataset_path)

    results = []
    for pair in migration_pairs[:5]:  # Start with first 5 examples
        unittest_metrics, pytest_metrics = run_migration_comparison(pair)
        unittest_metrics.save_results()
        pytest_metrics.save_results()

        results.append(
            {
                "test_name": unittest_metrics.test_suite,
                "unittest": unittest_metrics.get_summary(),
                "pytest": pytest_metrics.get_summary(),
            }
        )


if __name__ == "__main__":
    main()
