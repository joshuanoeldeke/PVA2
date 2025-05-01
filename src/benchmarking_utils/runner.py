import time
import gc
import subprocess
import threading
import psutil


def measure_performance_subprocess(self, command_list, iterations=10, warmup_runs=5):
    """Measure execution time and memory usage using subprocess with warmup runs."""
    # Announce framework version
    print(f"Using {self.framework} version: {self.results['metadata']['test_framework_version']}")
    print(f"Performing {warmup_runs} warmup runs...")

    # Execute warmup runs without recording metrics
    for _ in range(warmup_runs):
        subprocess.run(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(
        f"Measuring {self.framework} on {self.test_suite} ({iterations} iterations)..."
    )

    for i in range(iterations):
        # Clear memory before each run
        gc.collect()

        # Record start time
        start_time = time.time()

        # Launch subprocess and monitor its resources
        process = subprocess.Popen(
            command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
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
                try:
                    ct = p_local.cpu_times()
                    mem = p_local.memory_info().rss / 1024 / 1024
                    # Update resource metrics
                    cpu_user = ct.user - start_cpu.user
                    cpu_system = ct.system - start_cpu.system
                    thread_count = p_local.num_threads()
                    if mem > peak_memory:
                        peak_memory = mem
                    if mem < min_memory:
                        min_memory = mem
                except psutil.NoSuchProcess:
                    break
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
