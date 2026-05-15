"""
Generate IEEE-style matplotlib figures from benchmark and attack results.

Saves high-DPI PNG files to paper/results/:
  - fig_latency.png           — line chart: Rust vs Python latency over 1000 runs
  - fig_attack_detection.png  — bar chart: detection rate per attack type
  - fig_memory.png            — memory comparison (Rust vs Python per call)

Usage:
    cd securemark5g/python
    python3 graphs.py
"""
import csv
import os
import sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

matplotlib.rcParams.update({
    "font.family":         "serif",
    "font.size":           11,
    "axes.spines.top":     False,
    "axes.spines.right":   False,
    "axes.titlesize":      12,
    "axes.titleweight":    "bold",
    "figure.dpi":          150,
})

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "paper", "results")
COLORS = {
    "rust":     "#534AB7",
    "python":   "#D85A30",
    "detected": "#1D9E75",
    "clean":    "#85B7EB",
}


def _require(path):
    if not os.path.exists(path):
        print(f"WARNING: {path} not found — run benchmark.py / attack_test.py first")
        return False
    return True


def plot_latency():
    path = os.path.join(RESULTS_DIR, "benchmark_raw.csv")
    if not _require(path):
        return
    rows = list(csv.DictReader(open(path)))
    rust = [float(r["rust_latency_us"])   for r in rows]
    py   = [float(r["python_latency_us"]) for r in rows]

    # Show first 200 runs for clarity (representative of full 1000)
    n = min(200, len(rust))
    x = list(range(1, n + 1))

    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.plot(x, rust[:n], label="SecureMark5G (Rust)",  linewidth=0.9, color=COLORS["rust"])
    ax.plot(x, py[:n],   label="AES+SHA256 (Python)",  linewidth=0.9, color=COLORS["python"], alpha=0.75)
    ax.set_xlabel("Run index (first 200 of 1,000)")
    ax.set_ylabel("Latency (µs)")
    ax.set_title("Fig. 1 — Authentication latency: SecureMark5G vs Python baseline")
    ax.legend(frameon=False)
    ax.annotate(
        f"Speedup ≈ {sum(py[:n]) / sum(rust[:n]):.1f}×",
        xy=(n * 0.6, max(py[:n]) * 0.85),
        fontsize=10, color=COLORS["rust"],
    )
    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, "fig_latency.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Saved → {out}")
    plt.close(fig)


def plot_attack_detection():
    path = os.path.join(RESULTS_DIR, "attack_results.csv")
    if not _require(path):
        return
    rows   = list(csv.DictReader(open(path)))
    labels = [r["attack"].replace("_", "\n") for r in rows]
    rates  = [float(r["detection_rate"]) * 100 for r in rows]
    colors = [COLORS["clean"] if r["attack"] == "clean" else COLORS["detected"] for r in rows]

    fig, ax = plt.subplots(figsize=(7, 3.8))
    bars = ax.bar(labels, rates, color=colors, edgecolor="white", linewidth=0.5, width=0.55)
    ax.set_ylabel("Detection / accuracy rate (%)")
    ax.set_ylim(0, 115)
    ax.set_title("Fig. 2 — Attack detection rate by scenario")
    for bar, rate in zip(bars, rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            f"{rate:.1f}%",
            ha="center", va="bottom", fontsize=9,
        )
    legend_patches = [
        mpatches.Patch(color=COLORS["clean"],    label="Benign (accuracy)"),
        mpatches.Patch(color=COLORS["detected"], label="Attack detected"),
    ]
    ax.legend(handles=legend_patches, frameon=False, fontsize=9)
    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, "fig_attack_detection.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Saved → {out}")
    plt.close(fig)


def plot_memory():
    path = os.path.join(RESULTS_DIR, "benchmark_raw.csv")
    if not _require(path):
        return
    rows     = list(csv.DictReader(open(path)))
    rust_mem = [float(r["rust_memory_kb"])   for r in rows]
    py_mem   = [float(r["python_memory_kb"]) for r in rows]

    import statistics
    fig, ax = plt.subplots(figsize=(5, 3.5))
    labels = ["SecureMark5G\n(Rust)", "AES+SHA256\n(Python)"]
    means  = [statistics.mean(rust_mem), statistics.mean(py_mem)]
    bars   = ax.bar(labels, means, color=[COLORS["rust"], COLORS["python"]],
                    edgecolor="white", width=0.45)
    ax.set_ylabel("Avg memory delta per call (KB)")
    ax.set_title("Fig. 3 — Memory usage comparison")
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{val:.1f} KB", ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, "fig_memory.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Saved → {out}")
    plt.close(fig)


if __name__ == "__main__":
    print("Generating IEEE paper figures...\n")
    plot_latency()
    plot_attack_detection()
    plot_memory()
    print("\nDone. Figures are in paper/results/")
