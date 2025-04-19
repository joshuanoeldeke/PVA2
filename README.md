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

### 1. Calculator Example

Run the benchmark on the simple calculator example:

```bash
cd testing-framework-comparison
python scripts/run_calculator_benchmark.py
```

Results will be saved in the `results/` directory.

### 2. Migration Dataset (TestMigrationsInPy)

Run the benchmark on real-world migration pairs:

```bash
python scripts/run_migration_benchmarks.py
```

You may need to update the dataset path in the script.

### 3. Generic Benchmarking CLI

You can now benchmark **any** example suite directory containing a code file and framework-specific test files using a single command.

```bash
python scripts/run_benchmark.py --path src/examples [options]
```

Common options:

- `--path, -p` : Directory containing example subdirectories (required), each with a code file and two test files named `test_<name>_unittest.py` and `test_<name>_pytest.py`
- `--frameworks, -f` : List of frameworks to benchmark (default: `unittest pytest`)
- `--iterations, -n` : Number of measurement iterations per suite (default: 10)
- `--warmup, -w` : Number of warmup runs before measurement (default: 5)
- `--output-dir, -o` : Directory to save JSON result files (default: `results/`)

Example: benchmark all example suites under `src/examples` with only pytest for 5 iterations:

```bash
python scripts/run_benchmark.py \
  --path src/examples \
  --frameworks pytest \
  --iterations 5 \
  --warmup 2
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
