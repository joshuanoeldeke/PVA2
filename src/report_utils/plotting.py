import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def plot_mean_execution_time(summary_df, output_dir):
    """Grouped bar plot of mean execution times with 95% CI error bars."""
    frameworks = summary_df["framework"].unique()
    suites = summary_df["test_suite"].unique()
    n_suites = len(suites)
    n_fws = len(frameworks)
    x = np.arange(n_suites)
    bar_width = 0.8 / n_fws
    fig, ax = plt.subplots(figsize=(8, 6))
    for i, fw in enumerate(frameworks):
        sub = summary_df[summary_df["framework"] == fw]
        means = [sub[sub["test_suite"] == suite]["mean"].values[0] for suite in suites]
        cis = [sub[sub["test_suite"] == suite]["ci95"].values[0] for suite in suites]
        positions = x + (i - (n_fws - 1) / 2) * bar_width
        ax.bar(positions, means, width=bar_width, yerr=cis, capsize=5, label=fw, error_kw={"elinewidth": 1})
    ax.set_xticks(x)
    ax.set_xticklabels(suites)
    ax.set_ylabel("Mean Execution Time (s)")
    ax.set_title("Mean Execution Time by Framework and Test Suite")
    ax.legend()
    fig.tight_layout()
    out = Path(output_dir) / "mean_execution_time.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_boxplots(df, output_dir):
    """Generate boxplots of execution times for each test suite."""
    for suite in df["test_suite"].unique():
        sub = df[df["test_suite"] == suite]
        plt.figure(figsize=(6, 4))
        sns.boxplot(data=sub, x="framework", y="execution_time_seconds")
        plt.title(f"Execution Time Distribution: {suite}")
        plt.ylabel("Time (s)")
        plt.tight_layout()
        out = Path(output_dir) / f"boxplot_{suite}.png"
        plt.savefig(out)
        plt.close()


def plot_mean_per_suite(summary_df, output_dir):
    """Generate a bar chart of mean execution time with 95% CI for each framework, per test suite."""
    for suite in summary_df['test_suite'].unique():
        sub = summary_df[summary_df['test_suite'] == suite]
        frameworks = sub['framework'].tolist()
        means = sub['mean'].tolist()
        cis = sub['ci95'].tolist()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(frameworks, means, yerr=cis, capsize=5)
        ax.set_title(f"Mean Execution Time: {suite}")
        ax.set_ylabel("Mean Execution Time (s)")
        fig.tight_layout()
        out = Path(output_dir) / f"mean_execution_time_{suite}.png"
        fig.savefig(out)
        plt.close(fig)