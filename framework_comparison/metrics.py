# Updated performance_metrics.py with subprocess support
import time
import psutil
import os
import gc
import statistics
import json
import subprocess
import threading
import platform
from datetime import datetime
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
            # Navigate up two levels from this file to the project root
            base_dir = Path(__file__).resolve().parent.parent
            self.output_dir = base_dir / "results"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(exist_ok=True)
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "platform": platform.platform(),
                "machine_type": platform.machine(),
                "processor": platform.processor(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "total_memory_mb": psutil.virtual_memory().total / 1024 / 1024,
                "python_version": platform.python_version(),
            },
            "framework": framework_name,
            "test_suite": test_suite_name,
            "runs": [],
        }

        # Record test framework version
        try:
            if framework_name.lower() == 'pytest':
                import pytest
                fw_version = pytest.__version__
            elif framework_name.lower() == 'unittest':
                fw_version = f"stdlib ({platform.python_version()})"
            else:
                from importlib.metadata import version as _md_version
                fw_version = _md_version(framework_name)
        except Exception:
            fw_version = 'unknown'
        self.results['metadata']['test_framework_version'] = fw_version

    def measure_performance_subprocess(
        self, command_list, iterations=10, warmup_runs=5
    ):
        """Measure execution time and memory usage using subprocess with warmup runs."""
        # Announce framework version
        print(f"Using {self.framework} version: {self.results['metadata']['test_framework_version']}")
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

            # Record start time
            start_time = time.time()

            # Launch subprocess and monitor its peak memory usage
            process = subprocess.Popen(
                command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            # Record CPU baseline for subprocess and initialize resource trackers
            p = psutil.Process(process.pid)
            start_cpu = p.cpu_times()
            peak_memory = 0
            min_memory = float('inf')
            cpu_user = 0.0
            cpu_system = 0.0
            thread_count = 0

            def monitor():
                nonlocal peak_memory, min_memory, cpu_user, cpu_system, thread_count
                p_local = psutil.Process(process.pid)
                # Monitor CPU and memory until subprocess exits
                while True:
                    # Sample CPU times and thread count
                    try:
                        ct = p_local.cpu_times()
                        cpu_user = ct.user - start_cpu.user
                        cpu_system = ct.system - start_cpu.system
                        thread_count = p_local.num_threads()
                    except psutil.NoSuchProcess:
                        break
                    # Sample memory usage
                    mem = p_local.memory_info().rss / 1024 / 1024
                    if mem > peak_memory:
                        peak_memory = mem
                    if mem < min_memory:
                        min_memory = mem
                    # Check for process exit
                    if process.poll() is not None:
                        break
                    time.sleep(0.01)

            monitor_thread = threading.Thread(target=monitor)
            monitor_thread.start()
            stdout, stderr = process.communicate()
            monitor_thread.join()
            exit_code = process.returncode

            # Print output for debugging
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)

            # Calculate metrics
            end_time = time.time()
            execution_time = end_time - start_time
            memory_used = peak_memory

            # Store results
            run_data = {
                "iteration": i + 1,
                "execution_time_seconds": execution_time,
                "min_memory_mb": min_memory,
                "peak_memory_mb": peak_memory,
                "cpu_user_time_seconds": cpu_user,
                "cpu_system_time_seconds": cpu_system,
                "thread_count": thread_count,
                "exit_code": exit_code,
            }
            self.results["runs"].append(run_data)

            print(
                f"  Run {i + 1}: Time: {execution_time:.2f}s, Min Memory: {min_memory:.2f}MB, Peak Memory: {peak_memory:.2f}MB"
            )
            print(
                f"      CPU user: {cpu_user:.2f}s, system: {cpu_system:.2f}s, threads: {thread_count}"
            )

            # Wait between runs to stabilize system
            time.sleep(1)

    def get_summary(self):
        """Return raw per-iteration data only (no statistics or bootstrap)."""
        return {
            "metadata": self.results.get("metadata", {}),
            "framework": self.framework,
            "test_suite": self.test_suite,
            "runs": self.results["runs"],
        }

    def save_results(self):
        """Save summary (with raw runs) to a single JSON file per framework."""
        summary = self.get_summary()
        output_file = self.output_dir / f"{self.test_suite}_{self.framework}.json"
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)
        return output_file
    
    def detect_test_dependencies(self, test_file):
        """Detect and return required dependencies for a test file"""
        # Implementation to detect imports
