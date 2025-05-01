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
.
├── README.md
├── requirements.txt
├── src/                  # Application code and entrypoints
│   ├── main.py           # Unified CLI: benchmarks + reporting
│   ├── benchmarking.py   # Standalone benchmarking CLI
│   ├── reporting.py      # Standalone reporting CLI
│   ├── benchmarking_utils/  # Core benchmarking modules
│   └── report_utils/     # Core reporting modules
├── sample_cases/         # Example test suites (calculator, fibonacci, ...)
└── results/              # Output of runs and reports
    ├── raw_metrics/      # JSON per-framework metrics
    └── reports/          # CSV summaries and PNG/graphics
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

Choose one of the CLI entrypoints under `src/`:

**Benchmarking only:**
```bash
python src/benchmarking.py --path <examples_dir> [options]
```
Options:
- `--path, -p`  : Root directory with example suites (default: `test_cases`)
- `--frameworks, -f` : Frameworks to benchmark (default: `unittest pytest`)
- `--iterations, -n` : Number of measurement iterations (default: `10`)
- `--warmup, -w` : Warmup runs before timing (default: `5`)
- `--output-dir, -o` : Directory for raw JSON outputs (default: `results/raw_metrics`)

**Reporting only:**
```bash
python src/reporting.py --results-dir <raw_metrics_dir> [options]
```
Options:
- `--results-dir, -r` : Directory containing raw JSON results (default: `results/raw_metrics`)
- `--report-dir, -o` : Directory for CSV and PNG outputs (default: `results/reports`)

**Benchmarks + Reports (unified):**
```bash
python src/main.py [--bench] [--report] [options]
```
Flags:
- `--bench`   : run benchmarks only
- `--report`  : generate reports only

All benchmarking and reporting flags from above are supported together. Example:
```bash
# run both pipelines on sample_cases
python src/main.py -p sample_cases -n 5 -w 2

# benchmarks only
python src/main.py --bench -p sample_cases

# reports only
python src/main.py --report -r results/raw_metrics -o results/reports
```

---

## Detailed Workflow & Outputs

1. **Discovery**
   - The benchmarking CLI (`src/benchmarking.py` or via `src/main.py`) scans the `--path` directory.
   - If it finds matching `test_<suite>_unittest.py` and `test_<suite>_pytest.py`, it treats the folder as a single suite; otherwise it enumerates each subdirectory.

2. **Measurement**
   - For each suite and framework, tests run in an isolated subprocess to capture:
     - **execution_time_seconds**: wall-clock duration.
     - **min_memory_mb** / **peak_memory_mb**: tracked via `psutil`.
     - **cpu_user_time_seconds** / **cpu_system_time_seconds**: CPU usage breakdown.
     - **thread_count**: number of threads spawned.
     - **exit_code**: process return code.
   - Warmup runs (default `--warmup 5`) skip recording; measurement runs (default `--iterations 10`) record detailed per-run data.

3. **Raw JSON Output**
   - Saved under `results/raw_metrics/` as `<suite>_<framework>.json`.
   - Structure:
     ```json
     {
       "metadata": { /* timestamp, platform, CPU/RAM specs, Python and framework version */ },
       "framework": "pytest",             
       "test_suite": "calculator",
       "runs": [                          
         {"iteration": 1, "execution_time_seconds": 0.09, /* ... */},
         {"iteration": 2, /* ... */},
         /* ... */
       ]
     }
     ```

4. **Summary CSV (`summary.csv`)**
   - One row per (test_suite, framework).
   - Columns:
     - `count`: number of recorded runs
     - `mean`, `median`, `std`, `sem`: descriptive stats of execution times
     - `ci95`: half-width of the 95% confidence interval

5. **Pairwise Tests (`pairwise_tests.csv`)**
   - Two-sample t-tests between each pair of frameworks, per suite.
   - Columns:`t_stat`, `p_value`, `significant` (p < 0.05)

6. **Visualizations**
   - `mean_execution_time.png`: grouped bar chart of all suites’ mean times (95% CI).
   - `mean_execution_time_<suite>.png`: per-suite bar chart with error bars.
   - `boxplot_<suite>.png`: boxplot of raw iteration times.

---

## How to Extend

- Add new test suites under `sample_cases/` or any directory and point `--path` to it.
- Extend `benchmarking_utils/` to collect additional metrics or support new execution modes.
- Enhance `report_utils/` (data_loading, summary, stats, plotting) for custom analyses or new visualizations.
- Adjust or add CLI options in `src/benchmarking.py`, `src/reporting.py`, and `src/main.py` to fit your workflow.

---

## Statistical Terms Explained

- **Mean:** The average value across all runs.
- **Median:** The middle value when all runs are sorted; less sensitive to outliers.
- **Standard Deviation (stdev):** How much the results vary from the mean; lower is more consistent.

---

## References

- Barbosa, E. S., & Hora, A. (2022). [How and Why Developers Migrate Python Tests](https://doi.org/10.5281/zenodo.5847361)
- [TestMigrationsInPy dataset](https://github.com/altinoalvesjunior/TestMigrationsInPy)

---

## License

MIT License.

---

## Contact

For questions, suggestions, or contributions, please open an issue or submit a pull request.

---

**This project aims to bridge the gap between developer experience and objective performance data, empowering the Python testing community with actionable insights.**
