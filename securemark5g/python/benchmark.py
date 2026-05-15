"""
Benchmark SecureMark5G (Rust) vs AES+SHA256 (Python baseline).

Measures:
  - Per-call latency in microseconds (1,000 iterations)
  - RSS memory delta per call in kilobytes
  - Throughput in packets/second

Outputs:
  - paper/results/benchmark_raw.csv   (all 1000 run rows)
  - paper/results/benchmark_stats.csv (summary statistics)

Usage:
    cd securemark5g/python
    python3 benchmark.py
"""
import time
import os
import csv
import sys
import psutil
import statistics

# Try importing the Rust extension; fall back with a clear message
try:
    import securemark5g
except ImportError:
    print("ERROR: securemark5g Rust extension not found.")
    print("Run:  maturin develop    (from the securemark5g/ directory)")
    sys.exit(1)

from baseline import baseline_full_pipeline, baseline_server_verify
from device_sim import generate_sensor_data

# ─── Config ──────────────────────────────────────────────────────────────────
DEVICE_ID   = "IOT_DEVICE_001"
SECRET_KEY  = b"benchmark_secret_key_32_bytes__!"
ENC_KEY     = b"benchmark_enckey_32_bytes_padded"
N_RUNS      = 1000
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "paper", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ─── Measurement helper ───────────────────────────────────────────────────────
def measure(fn, *args):
    """Measure latency (µs) and RSS memory delta (KB) of a single function call."""
    proc = psutil.Process()
    mem_before = proc.memory_info().rss / 1024  # KB
    t0 = time.perf_counter_ns()
    result = fn(*args)
    t1 = time.perf_counter_ns()
    mem_after = proc.memory_info().rss / 1024
    latency_us = (t1 - t0) / 1_000
    mem_kb = max(0.0, mem_after - mem_before)
    return result, latency_us, mem_kb


def run_benchmarks():
    print(f"Running {N_RUNS} benchmark iterations...")
    payload = generate_sensor_data(64, seed=42)
    rows = []

    for i in range(N_RUNS):
        # ── Rust pipeline ──────────────────────────────────────────────────
        _, rust_lat, rust_mem = measure(
            securemark5g.device_send,
            DEVICE_ID, SECRET_KEY, payload, ENC_KEY,
        )
        # ── Python baseline ────────────────────────────────────────────────
        _, py_lat, py_mem = measure(
            baseline_full_pipeline,
            DEVICE_ID, SECRET_KEY, payload, ENC_KEY,
        )
        rows.append({
            "run":                i + 1,
            "rust_latency_us":    round(rust_lat, 3),
            "python_latency_us":  round(py_lat, 3),
            "rust_memory_kb":     round(rust_mem, 3),
            "python_memory_kb":   round(py_mem, 3),
        })

        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{N_RUNS} done...")

    # ── Write raw CSV ──────────────────────────────────────────────────────
    raw_path = os.path.join(RESULTS_DIR, "benchmark_raw.csv")
    with open(raw_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nRaw data → {raw_path}")

    # ── Compute stats ──────────────────────────────────────────────────────
    rust_lats = [r["rust_latency_us"]   for r in rows]
    py_lats   = [r["python_latency_us"] for r in rows]
    rust_mems = [r["rust_memory_kb"]    for r in rows]
    py_mems   = [r["python_memory_kb"]  for r in rows]

    stats = [
        {"metric": "rust_latency_us",   "mean": statistics.mean(rust_lats),
         "median": statistics.median(rust_lats), "stdev": statistics.stdev(rust_lats),
         "min": min(rust_lats), "max": max(rust_lats)},
        {"metric": "python_latency_us", "mean": statistics.mean(py_lats),
         "median": statistics.median(py_lats), "stdev": statistics.stdev(py_lats),
         "min": min(py_lats), "max": max(py_lats)},
        {"metric": "rust_memory_kb",    "mean": statistics.mean(rust_mems),
         "median": statistics.median(rust_mems), "stdev": statistics.stdev(rust_mems),
         "min": min(rust_mems), "max": max(rust_mems)},
        {"metric": "python_memory_kb",  "mean": statistics.mean(py_mems),
         "median": statistics.median(py_mems), "stdev": statistics.stdev(py_mems),
         "min": min(py_mems), "max": max(py_mems)},
    ]

    stats_path = os.path.join(RESULTS_DIR, "benchmark_stats.csv")
    with open(stats_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=stats[0].keys())
        writer.writeheader()
        writer.writerows(stats)
    print(f"Stats    → {stats_path}")

    # ── Print summary ──────────────────────────────────────────────────────
    rust_avg = statistics.mean(rust_lats)
    py_avg   = statistics.mean(py_lats)
    speedup  = py_avg / rust_avg if rust_avg > 0 else float("inf")
    print(f"\n{'─'*50}")
    print(f"  Rust avg latency:   {rust_avg:.2f} µs")
    print(f"  Python avg latency: {py_avg:.2f} µs")
    print(f"  Speedup:            {speedup:.1f}×")
    print(f"  Throughput (Rust):  {1_000_000 / rust_avg:,.0f} pkts/s")
    print(f"  Throughput (Py):    {1_000_000 / py_avg:,.0f} pkts/s")
    print(f"{'─'*50}")


if __name__ == "__main__":
    run_benchmarks()
