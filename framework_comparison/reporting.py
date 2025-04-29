import os
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter  # for loop support in GIF


def load_results(results_dir):
    """Load JSON result files into a pandas DataFrame (recursively)."""
    records = []
    # Search all JSON files recursively in results_dir
    for file in Path(results_dir).rglob("*.json"):
        data = json.load(open(file))
        suite = data.get("test_suite")
        fw = data.get("framework")
        for run in data.get("runs", []):
            rec = {**run, "framework": fw, "test_suite": suite}
            records.append(rec)
    df = pd.DataFrame.from_records(records)
    return df


def compute_summary(df):
    """Compute summary statistics and confidence intervals grouped by suite and framework."""
    grp = df.groupby(["test_suite", "framework"])
    summary = grp["execution_time_seconds"].agg(["count", "mean", "median", "std"]).reset_index()
    summary["sem"] = summary["std"] / np.sqrt(summary["count"])
    summary["ci95"] = summary["sem"] * 1.96
    return summary


def perform_pairwise_tests(df, alpha=0.05):
    """Perform pairwise t-tests between frameworks for each test suite."""
    results = []
    suites = df["test_suite"].unique()
    for suite in suites:
        sub = df[df["test_suite"] == suite]
        frameworks = sub["framework"].unique()
        for i, f1 in enumerate(frameworks):
            for f2 in frameworks[i+1:]:
                a = sub[sub["framework"] == f1]["execution_time_seconds"]
                b = sub[sub["framework"] == f2]["execution_time_seconds"]
                stat, p = stats.ttest_ind(a, b, equal_var=False)
                results.append({"test_suite": suite,
                                "framework1": f1,
                                "framework2": f2,
                                "t_stat": stat,
                                "p_value": p,
                                "significant": p < alpha})
    return pd.DataFrame(results)


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
        ax.bar(
            positions,
            means,
            width=bar_width,
            yerr=cis,
            capsize=5,
            label=fw,
            error_kw={"elinewidth": 1},
        )
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


# def animate_speed_comparison(summary_df, output_dir, frames=120):
#     """Create and save a GIF showing balls bouncing at speeds inverse to mean execution time, with labels."""
#     frameworks = summary_df['framework'].tolist()
#     mean_times = summary_df['mean'].tolist()
#     # Compute normalized speeds and apply speed multiplier
#     speed_factor = 2.0  # increase this to speed up ball movement
#     speeds = [1.0 / t for t in mean_times]
#     max_speed = max(speeds)
#     norm_speeds = [s / max_speed * speed_factor for s in speeds]
#     # Setup figure with white background and walls
#     # set to 1080p (16:9) resolution
#     fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
#     fig.patch.set_facecolor('white')
#     ax.set_xlim(0, 1)
#     ax.set_ylim(0, len(frameworks) + 1)
#     ax.set_aspect('equal')
#     ax.axis('off')
#     # expand axes to full figure to remove white margins
#     fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
#     ax.margins(x=0)
#     # expand axis to fill entire figure (remove all white borders)
#     ax.set_position([0, 0, 1, 1])
#     # draw left/right walls at ball bounce limits
#     radius = 0.08  # must match circle radius
#     wall_opts = dict(colors='gray', linestyles='--', linewidth=1, alpha=0.3)
#     ax.vlines([radius, 1 - radius], ymin=0, ymax=len(frameworks)+1, **wall_opts)
#     ax.set_title('Framework Speed Comparison', pad=10)
#     # assign colors
#     colors = sns.color_palette('tab10', n_colors=len(frameworks))
#     # Create circle and text artists
#     circles, labels = [], []
#     x_off = 0.05
#     for idx, (fw, color) in enumerate(zip(frameworks, colors), start=1):
#         y = idx
#         circ = plt.Circle((0.1, y), radius, color=color, ec='black', lw=1)
#         ax.add_patch(circ)
#         text = ax.text(0.1 + x_off, y, fw,
#                        va='center', ha='left', fontsize=9, color=color)
#         circles.append(circ)
#         labels.append(text)
#     # Animation update
#     def update(frame):
#         artists = []
#         for i, circ in enumerate(circles):
#             # smooth bounce across full width
#             frac = (frame * norm_speeds[i] / frames) % 1
#             offset = 0.5 * (1 - np.cos(2 * np.pi * frac))  # 0→1→0
#             x = radius + (1 - 2 * radius) * offset
#             y = i + 1
#             circ.center = (x, y)
#             labels[i].set_position((x + x_off, y))
#             artists.extend([circ, labels[i]])
#         return artists
#     # Create and save animation
#     ani = animation.FuncAnimation(fig, update, frames=frames, blit=True)
#     out = Path(output_dir) / 'speed_comparison.gif'
#     # create PillowWriter for GIF
#     writer = PillowWriter(fps=30)
#     # save with tight bounding box and no padding to eliminate borders
#     ani.save(out, writer=writer, dpi=100,
#              savefig_kwargs={'bbox_inches':'tight','pad_inches':0})
#     plt.close(fig)
#     return out


def generate_reports(results_dir="results", report_dir="reports"):
    """Load results, compute stats, perform tests, and generate visualizations and CSV summaries."""
    os.makedirs(report_dir, exist_ok=True)
    df = load_results(results_dir)
    summary = compute_summary(df)
    summary.to_csv(Path(report_dir) / "summary.csv", index=False)
    tests = perform_pairwise_tests(df)
    tests.to_csv(Path(report_dir) / "pairwise_tests.csv", index=False)
    plot_mean_execution_time(summary, report_dir)
    plot_boxplots(df, report_dir)
    # Create speed comparison GIF
    #animate_speed_comparison(summary, report_dir)
    print(f"Reports generated in {report_dir}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate performance reports from raw results")
    parser.add_argument("--results-dir", "-r", default="results/raw_metrics",
                        help="Directory containing raw JSON result files (defaults to results/raw_metrics)")
    parser.add_argument("--report-dir", "-o", default="results/reports",
                        help="Output directory for reports and plots")
    args = parser.parse_args()
    generate_reports(args.results_dir, args.report_dir)
