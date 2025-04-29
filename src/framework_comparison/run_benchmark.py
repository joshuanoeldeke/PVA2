#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import click
import configparser
import logging
from src.framework_comparison.metrics import PerformanceMetrics

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging output")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration INI file")
@click.option("--path", "-p", default="test_cases", show_default=True,
              help="Root directory containing example code subdirectories")
@click.option("--frameworks", "-f", default="unittest,pytest", show_default=True,
              help="Comma-separated list of test frameworks to benchmark")
@click.option("--iterations", "-n", default=10, show_default=True, type=int,
              help="Number of measurement iterations per suite")
@click.option("--warmup", "-w", default=5, show_default=True, type=int,
              help="Number of warmup runs before measurement")
@click.option("--output-dir", "-o", default="results/raw_metrics", show_default=True,
              help="Directory to save result JSON files")
def main(verbose, config, path, frameworks, iterations, warmup, output_dir):
    # Configure logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=level
    )
    logging.getLogger().setLevel(level)
    logging.debug("Verbose logging enabled")
    # Load config file if provided
    if config:
        cfg = configparser.ConfigParser()
        cfg.read(config)
        if cfg.has_section("benchmark"):
            sec = cfg["benchmark"]
            path = sec.get("path", path)
            frameworks = sec.get("frameworks", ",".join(frameworks.split(","))).split(",")
            iterations = sec.getint("iterations", iterations)
            warmup = sec.getint("warmup", warmup)
            output_dir = sec.get("output_dir", output_dir)
    # Normalize frameworks to list
    if isinstance(frameworks, str):
        frameworks = [fw.strip() for fw in frameworks.split(",")]
    root = Path(path)
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
    click.echo(f"Discovered {len(suite_dirs)} example suites in '{path}'.")

    for suite_dir in suite_dirs:
        suite_name = suite_dir.name
        click.echo(f"\nRunning suite '{suite_name}'...")
        for fw in frameworks:
            test_file = suite_dir / f"test_{suite_name}_{fw}.py"
            if not test_file.exists():
                click.echo(f"Skipping {fw} for suite '{suite_name}': {test_file} not found.")
                continue
            click.echo(f"Running {fw} on {test_file}...")
            metrics = PerformanceMetrics(fw, suite_name, output_dir=output_dir)
            # Execute tests in subprocess, inheriting environment
            cmd = [sys.executable]
            if fw.lower() == "pytest":
                cmd += ["-m", "pytest", str(test_file)]
            else:
                cmd += ["-m", "unittest", str(test_file)]
            metrics.measure_performance_subprocess(cmd,
                                                   iterations=iterations,
                                                   warmup_runs=warmup)
            output_file = metrics.save_results()
            click.echo(f"Results saved to {output_file}\n")

if __name__ == "__main__":
    main()
