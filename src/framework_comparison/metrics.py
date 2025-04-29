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
import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """Measure and record performance metrics of test frameworks."""

    def __init__(self, framework_name: str, test_suite_name: str, output_dir: str = None) -> None:
        self.framework: str = framework_name
        self.test_suite: str = test_suite_name

        # Determine output directory
        if output_dir is None:
            base_dir = Path(__file__).resolve().parent.parent
            self.output_dir = base_dir / "results" / "raw_metrics"
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
        self, command_list: List[str], iterations: int = 10, warmup_runs: int = 5
    ) -> None:
        """
        Execute warmup runs and measure performance across multiple iterations.
        Records execution time, memory, CPU usage, and thread count.
        """
        logger.info("Using %s version: %s", self.framework, self.results['metadata']['test_framework_version'])
        logger.info("Performing %d warmup runs", warmup_runs)

        self._run_warmup(command_list, warmup_runs)

        logger.info("Measuring %s on %s (%d iterations)", self.framework, self.test_suite, iterations)

        for i in range(iterations):
            # Clear memory before each run
            gc.collect()

            start_time = time.time()

            peak_memory, min_memory, cpu_user, cpu_system, thread_count, exit_code = \
                self._run_iteration(command_list, start_time)

            # Log per-iteration result
            logger.debug(
                "Run %d: Time: %.2fs, Min Memory: %.2fMB, Peak Memory: %.2fMB, CPU: user %.2fs system %.2fs, threads %d", 
                i+1, time.time() - start_time, min_memory, peak_memory, cpu_user, cpu_system, thread_count
            )

            # Store run data
            self.results["runs"].append({
                "iteration": i + 1,
                "execution_time_seconds": time.time() - start_time,
                "min_memory_mb": min_memory,
                "peak_memory_mb": peak_memory,
                "cpu_user_time_seconds": cpu_user,
                "cpu_system_time_seconds": cpu_system,
                "thread_count": thread_count,
                "exit_code": exit_code,
            })
            time.sleep(1)

    def _run_warmup(self, command_list: List[str], warmup_runs: int) -> None:
        """Run warmup runs without recording metrics"""
        for _ in range(warmup_runs):
            subprocess.run(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    def _run_iteration(self, command_list: List[str], start_time: float) -> Tuple[float, float, float, float, int, int]:
        """Run one iteration and monitor until completion"""
        process = subprocess.Popen(
            command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        p = psutil.Process(process.pid)
        start_cpu = p.cpu_times()
        peak_memory: float = 0.0
        min_memory: float = float('inf')
        cpu_user: float = 0.0
        cpu_system: float = 0.0
        thread_count: int = 0

        def monitor() -> None:
            nonlocal peak_memory, min_memory, cpu_user, cpu_system, thread_count
            while True:
                try:
                    ct = p.cpu_times()
                    cpu_user = ct.user - start_cpu.user
                    cpu_system = ct.system - start_cpu.system
                    thread_count = p.num_threads()
                    mem = p.memory_info().rss / 1024 / 1024
                except psutil.NoSuchProcess:
                    break
                peak_memory = max(peak_memory, mem)
                min_memory = min(min_memory, mem)
                if process.poll() is not None:
                    break
                time.sleep(0.01)

        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()
        stdout, stderr = process.communicate()
        monitor_thread.join()
        exit_code = process.returncode
        return peak_memory, min_memory, cpu_user, cpu_system, thread_count, exit_code

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
    
    def detect_test_dependencies(self, test_file: str) -> List[str]:
        """Detect and return required dependencies (imported modules) for a test file."""
        # TODO: implement import parsing via AST
        return []  # placeholder
