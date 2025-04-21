# Python Testing Framework Comparison

## Overview

This project provides a **scientific, reproducible, and extensible benchmarking tool** for comparing the performance of Python’s two most widely used testing frameworks: **unittest** and **pytest**. It is designed to help developers, researchers, and students understand the trade-offs between these frameworks in terms of execution time and memory usage, and to support informed decisions about framework selection and migration.

The project is inspired by and complements the research of Barbosa and Hora, _“How and Why Developers Migrate Python Tests”_ (2022), which analyzes the motivations and patterns behind real-world migrations from unittest to pytest. While their work focuses on qualitative aspects and migration patterns, this project adds **quantitative, technical performance metrics** to the discussion.

---

## Project Goals

- **Benchmark** unittest and pytest on both simple and complex test suites
- **Analyze** execution time and memory usage with robust statistical methods
- **Support** both toy examples (like a calculator) and real-world migration datasets (e.g., [TestMigrationsInPy](https://github.com/altinoalvesjunior/TestMigrationsInPy))
- **Enable reproducibility** and extensibility for further research or practical use
- **Provide a universal framework** to compare test suites across projects and datasets

---

## Project Structure

```plaintext
PVA2/
├── README.md
├── requirements.txt
├── datasets/
│   └── TestMigrationsInPy-main/
├── scripts/
│   ├── run_calculator_benchmark.py
│   ├── run_migration_benchmarks.py
│   └── run_benchmark.py
├── results/
│   ├── pytest_calculator_simple.json
│   └── unittest_calculator_simple.json
├── src/
│   ├── examples/
│   │   ├── calculator/
│   │   │   ├── calculator.py  # code file for example suite
│   │   │   ├── test_calculator_unittest.py  # unittest for calculator
│   │   │   └── test_calculator_pytest.py    # pytest for calculator
│   │   └── another_example/                 # additional example suites follow same pattern
│   │       ├── another_example.py
│   │       ├── test_another_example_unittest.py
│   │       └── test_another_example_pytest.py
│   └── framework_comparison/
│       ├── __init__.py
│       ├── metrics.py
│       ├── discovery.py
│       └── reporting.py
└── tests/
```

---

## Methodology

- **Warmup Runs:** Each benchmark includes several warmup runs to eliminate cold-start bias.
- **Isolated Execution:** Each test run is executed in a subprocess to isolate resource usage.
- **Multiple Iterations:** Benchmarks are run for many iterations (default: 100) for statistical reliability.
- **Metrics Collected:** Execution time, memory usage (minimum & peak), CPU user/system times, and thread count for each run.
- **Metadata Recorded:** Timestamp, host OS & machine specs, CPU & total RAM, Python version, and test framework version.
- **Data Output:** Raw per-iteration data saved as a single JSON file per framework (no built-in statistical analysis).
- **Universal Comparison:** The tool can discover and compare test suites in any project structure, and can specifically analyze before/after migration pairs from datasets like TestMigrationsInPy.

---

## Key Findings (Example)

- **unittest** is typically faster (lower mean execution time) and more consistent (lower standard deviation) than **pytest** for simple test suites.
- **pytest** offers more advanced features (fixtures, parameterization, plugins) and is preferred by developers for code maintainability and flexibility, despite its higher overhead.
- **Memory usage** is often similar for both frameworks on simple tests, but may differ on complex suites.
- **Developer preference** for pytest, as documented by Barbosa and Hora, is driven more by usability and maintainability than by raw performance.

---

## Usage

Run any example suite(s) under a directory using the generic benchmarking CLI:

```bash
python scripts/run_benchmark.py --path <examples_dir> [options]
```

Options:
- `--path, -p`: Root directory containing example subdirectories or a single suite (required).
- `--frameworks, -f`: List of test frameworks to benchmark (default: `unittest pytest`).
- `--iterations, -n`: Number of measurement iterations per suite (default: `10`).
- `--warmup, -w`: Number of warmup runs before measurement (default: `5`).
- `--output-dir, -o`: Directory to save result JSON files (default: `results/`).

Examples:

```bash
# Benchmark all example suites under src/examples
python scripts/run_benchmark.py -p src/examples

# Benchmark only the pytest framework for calculator suite
python scripts/run_benchmark.py -p src/examples/calculator -f pytest -n 5 -w 2

# Benchmark a single suite directory directly
python scripts/run_benchmark.py -p src/examples/fibonacci
```

---

## How to Extend

- Add new test suites to `src/examples/` or point the tool at any project directory.
- Add new datasets to the `datasets/` directory and update the discovery logic as needed.
- Modify `metrics.py` to collect additional metrics (e.g., peak memory, CPU usage).
- Use or extend `reporting.py` for richer result visualization.

---

## Statistical Terms Explained

- **Mean:** The average value across all runs.
- **Median:** The middle value when all runs are sorted; less sensitive to outliers.
- **Standard Deviation (stdev):** How much the results vary from the mean; lower is more consistent.
- **Confidence Interval:** The range in which the true mean likely falls (e.g., 95% certainty).
- **Bootstrap:** A resampling technique to estimate the reliability of statistics, especially with small samples.

---

## References

- Barbosa, E. S., & Hora, A. (2022). [How and Why Developers Migrate Python Tests](https://doi.org/10.5281/zenodo.5847361)
- [TestMigrationsInPy dataset](https://github.com/altinoalvesjunior/TestMigrationsInPy)

---

## License

MIT License (or your preferred license).

---

## Contact

For questions, suggestions, or contributions, please open an issue or submit a pull request.

---

**This project aims to bridge the gap between developer experience and objective performance data, empowering the Python testing community with actionable insights.**
