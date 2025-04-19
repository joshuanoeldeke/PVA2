import sys
import os

# Add the project root to sys.path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.framework_comparison.metrics import PerformanceMetrics
from src.framework_comparison.discovery import TestDiscovery

def main():
    dataset_path = "datasets/TestMigrationsInPy/projects/"
    
    discovery = TestDiscovery()
    migration_pairs = discovery.discover_migration_pairs(dataset_path)
    
    results = []
    
    for before_file, after_file in migration_pairs[:5]:  # Limit to first 5 pairs for testing
        unittest_metrics = PerformanceMetrics("unittest", os.path.basename(before_file))
        pytest_metrics = PerformanceMetrics("pytest", os.path.basename(after_file))
        
        python_exe = sys.executable
        
        unittest_cmd = [python_exe, "-m", "unittest", before_file]
        pytest_cmd = [python_exe, "-m", "pytest", after_file]
        
        unittest_metrics.measure_performance_subprocess(unittest_cmd)
        pytest_metrics.measure_performance_subprocess(pytest_cmd)
        
        unittest_metrics.save_results()
        pytest_metrics.save_results()
        
        results.append({
            "unittest": unittest_metrics.get_summary(),
            "pytest": pytest_metrics.get_summary(),
        })
    
if __name__ == "__main__":
    main()
