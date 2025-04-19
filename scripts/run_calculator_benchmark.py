import sys
import os

# Add the project root to sys.path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.framework_comparison.metrics import PerformanceMetrics

def main():
    unittest_metrics = PerformanceMetrics("unittest", "calculator_simple")
    pytest_metrics = PerformanceMetrics("pytest", "calculator_simple")
    
    python_exe = sys.executable
    
    unittest_file = "src/examples/calculator/test_calculator_unittest.py"
    pytest_file = "src/examples/calculator/test_calculator_pytest.py"
    
    unittest_cmd = [python_exe, "-m", "unittest", unittest_file]
    pytest_cmd = [python_exe, "-m", "pytest", pytest_file]
    
    unittest_metrics.measure_performance_subprocess(unittest_cmd)
    pytest_metrics.measure_performance_subprocess(pytest_cmd)
    
    unittest_metrics.save_results()
    pytest_metrics.save_results()

if __name__ == "__main__":
    main()
