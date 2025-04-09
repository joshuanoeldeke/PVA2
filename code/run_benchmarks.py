# Alternative run_benchmarks.py using subprocess
from performance_metrics import PerformanceMetrics
import os
import subprocess
import sys


def run_simple_tests():
    # Get the project base directory (one level up from the code directory)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Get paths to test files
    tests_dir = os.path.join(base_dir, "tests")
    unittest_file = os.path.join(tests_dir, "test_calculator_unittest.py")
    pytest_file = os.path.join(tests_dir, "test_calculator_pytest.py")

    # Python executable path
    python_exe = sys.executable

    # Measure unittest performance
    unittest_metrics = PerformanceMetrics("unittest", "calculator_simple")
    unittest_cmd = [python_exe, "-m", "unittest", unittest_file]
    unittest_metrics.measure_performance_subprocess(unittest_cmd)
    unittest_metrics.save_results()

    # Measure pytest performance
    pytest_metrics = PerformanceMetrics("pytest", "calculator_simple")
    pytest_cmd = [python_exe, "-m", "pytest", pytest_file, "-v"]
    pytest_metrics.measure_performance_subprocess(pytest_cmd)
    pytest_metrics.save_results()


if __name__ == "__main__":
    run_simple_tests()
