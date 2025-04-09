# Updated performance_metrics.py with subprocess support
import time
import psutil
import os
import gc
import statistics
import json
import subprocess
from pathlib import Path
from scipy import stats
import random


class PerformanceMetrics:
    """Class to measure and record performance metrics of test frameworks."""

    def __init__(self, framework_name, test_suite_name, output_dir=None):
        self.framework = framework_name
        self.test_suite = test_suite_name

        # If no output_dir is specified, create a 'results' directory at the project root
        if output_dir is None:
            # Navigate up one level from the 'code' directory to the project root
            base_dir = Path(__file__).parent.parent
            self.output_dir = base_dir / "results"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(exist_ok=True)
        self.results = {
            "framework": framework_name,
            "test_suite": test_suite_name,
            "runs": [],
        }

    def measure_performance(self, command, iterations=100):
        """Measure execution time and memory usage for a test command."""
        print(
            f"Measuring {self.framework} on {self.test_suite} ({iterations} iterations)..."
        )

        for i in range(iterations):
            # Clear memory before each run
            gc.collect()

            # Record starting metrics
            process = psutil.Process(os.getpid())
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            start_time = time.time()

            # Execute the test command
            exit_code = os.system(command)

            # Record ending metrics
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Calculate metrics
            execution_time = end_time - start_time
            memory_used = end_memory - start_memory

            # Store results
            run_data = {
                "iteration": i + 1,
                "execution_time_seconds": execution_time,
                "memory_delta_mb": memory_used,
                "exit_code": exit_code,
            }
            self.results["runs"].append(run_data)

            print(
                f"  Run {i + 1}: Time: {execution_time:.2f}s, Memory: {memory_used:.2f}MB"
            )

            # Wait between runs to stabilize system
            time.sleep(1)

    def measure_performance_subprocess(
        self, command_list, iterations=100, warmup_runs=5
    ):
        """Measure execution time and memory usage using subprocess with warmup runs."""
        print(f"Performing {warmup_runs} warmup runs...")

        # Execute warmup runs without recording metrics
        for i in range(warmup_runs):
            subprocess.run(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(
            f"Measuring {self.framework} on {self.test_suite} ({iterations} iterations)..."
        )

        for i in range(iterations):
            # Clear memory before each run
            gc.collect()

            # Record starting metrics
            process = psutil.Process(os.getpid())
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            start_time = time.time()

            # Execute the test command using subprocess
            result = subprocess.run(
                command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            exit_code = result.returncode

            # Print output for debugging
            print(result.stdout)
            if result.stderr:
                print(result.stderr)

            # Record ending metrics
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Calculate metrics
            execution_time = end_time - start_time
            memory_used = end_memory - start_memory

            # Store results
            run_data = {
                "iteration": i + 1,
                "execution_time_seconds": execution_time,
                "memory_delta_mb": memory_used,
                "exit_code": exit_code,
            }
            self.results["runs"].append(run_data)

            print(
                f"  Run {i + 1}: Time: {execution_time:.2f}s, Memory: {memory_used:.2f}MB"
            )

            # Wait between runs to stabilize system
            time.sleep(1)

    def bootstrap_stats(self, data, statistic_func, num_samples=1000):
        """Perform bootstrap resampling on the provided data."""

        n = len(data)
        results = []

        for _ in range(num_samples):
            # Sample with replacement
            sample = [data[random.randint(0, n - 1)] for _ in range(n)]
            results.append(statistic_func(sample))

        # Calculate 95% confidence interval
        results.sort()
        lower = results[int(0.025 * num_samples)]
        upper = results[int(0.975 * num_samples)]

        return {"mean": statistics.mean(results), "confidence_interval": (lower, upper)}

    def get_summary(self):
        """Compute summary statistics with confidence intervals."""
        times = [run["execution_time_seconds"] for run in self.results["runs"]]
        memories = [run["memory_delta_mb"] for run in self.results["runs"]]

        # Calculate 95% confidence interval
        confidence = 0.95
        n = len(times)
        mean = statistics.mean(times)
        stdev = statistics.stdev(times) if n > 1 else 0

        # t-distribution for small sample sizes
        t_value = stats.t.ppf((1 + confidence) / 2, n - 1)
        margin = t_value * stdev / (n**0.5)

        # Add bootstrap statistics
        bootstrap_time = self.bootstrap_stats(times, statistics.mean)
        bootstrap_memory = self.bootstrap_stats(memories, statistics.mean)

        summary = {
            "framework": self.framework,
            "test_suite": self.test_suite,
            "execution_time": {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "min": min(times),
                "max": max(times),
                "confidence_interval": (mean - margin, mean + margin),
                "confidence_level": confidence,
                "bootstrap": bootstrap_time,
            },
            "memory_usage": {
                "mean": statistics.mean(memories),
                "median": statistics.median(memories),
                "stdev": statistics.stdev(memories) if len(memories) > 1 else 0,
                "min": min(memories),
                "max": max(memories),
                "confidence_interval": (mean - margin, mean + margin),
                "confidence_level": confidence,
                "bootstrap": bootstrap_memory,
            },
        }

        return summary

    def save_results(self):
        """Save raw results and summary to JSON files."""
        # Save raw results
        results_file = self.output_dir / f"{self.framework}_{self.test_suite}_raw.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Save summary
        summary = self.get_summary()
        summary_file = (
            self.output_dir / f"{self.framework}_{self.test_suite}_summary.json"
        )
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        return results_file, summary_file
    
    def detect_test_dependencies(self, test_file):
        """Detect and return required dependencies for a test file"""
        # Implementation to detect imports
