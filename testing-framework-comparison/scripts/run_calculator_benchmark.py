from src.framework_comparison.metrics import PerformanceMetrics
import sys


def main():
    # Your existing calculator benchmark code
    unittest_metrics = PerformanceMetrics("unittest", "calculator_simple")
    pytest_metrics = PerformanceMetrics("pytest", "calculator_simple")

    python_exe = sys.executable
    unittest_file = "src/examples/calculator/test_calculator_unittest.py"
    pytest_file = "src/examples/calculator/test_calculator_pytest.py"

    unittest_cmd = [python_exe, "-m", "unittest", unittest_file]
    pytest_cmd = [python_exe, "-m", "pytest", pytest_file, "-v"]

    unittest_metrics.measure_performance_subprocess(unittest_cmd)
    pytest_metrics.measure_performance_subprocess(pytest_cmd)

    # Save results
    unittest_metrics.save_results()
    pytest_metrics.save_results()


if __name__ == "__main__":
    main()
