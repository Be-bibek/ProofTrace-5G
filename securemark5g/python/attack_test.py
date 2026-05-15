"""
Attack Detection Rate Measurement Suite.

Tests SecureMark5G against:
  1. Replay attacks          — resend captured valid packet
  2. Tamper (10% prob)       — random byte flip 10% of packets
  3. Tamper (50% prob)       — random byte flip 50% of packets
  4. Impersonation           — wrong device_id on server verify

Outputs:
  paper/results/attack_results.csv

Usage:
    cd securemark5g/python
    python3 attack_test.py
"""
import csv
import os
import sys

try:
    import securemark5g
except ImportError:
    print("ERROR: securemark5g not found. Run: maturin develop")
    sys.exit(1)

from device_sim import generate_sensor_data
from channel_sim import ChannelSimulator

# ─── Config ───────────────────────────────────────────────────────────────────
DEVICE_ID   = "IOT_DEVICE_001"
SECRET_KEY  = b"attack_test_key_32_bytes_exactly"
ENC_KEY     = b"attack_enckey_32_bytes_padded_!!"
N_TRIALS    = 500
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "paper", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def run_attack_suite():
    payload  = generate_sensor_data(64, seed=7)
    data_len = len(payload)
    results  = []

    scenarios = [
        ("clean",          ChannelSimulator(seed=1)),
        ("replay",         ChannelSimulator(replay=True, seed=2)),
        ("tamper_10pct",   ChannelSimulator(tamper_prob=0.10, seed=3)),
        ("tamper_50pct",   ChannelSimulator(tamper_prob=0.50, seed=4)),
        ("impersonation",  ChannelSimulator(seed=5)),   # handled manually below
    ]

    for attack, channel in scenarios:
        detected = 0
        total    = N_TRIALS

        for _ in range(N_TRIALS):
            # Device sends a valid packet every iteration
            packet, _, _ = securemark5g.device_send(
                DEVICE_ID, SECRET_KEY, payload, ENC_KEY
            )
            transmitted = channel.transmit(packet)

            # Impersonation: correct packet but wrong device_id on server
            verify_device_id = (
                "FAKE_DEVICE_999" if attack == "impersonation" else DEVICE_ID
            )

            if transmitted is None:
                # Dropped packet — counts as detected for non-clean scenarios
                if attack != "clean":
                    detected += 1
                continue

            authentic, reason = securemark5g.server_verify(
                transmitted, ENC_KEY, verify_device_id, SECRET_KEY, data_len
            )

            if attack == "clean":
                if not authentic:
                    detected += 1   # False positive (bad)
            else:
                if not authentic:
                    detected += 1   # True positive (good)

        if attack == "clean":
            # For clean: detection rate = 1 - false_positive_rate
            detection_rate = 1.0 - (detected / total)
        else:
            detection_rate = detected / total

        results.append({
            "attack":         attack,
            "detection_rate": round(detection_rate, 4),
            "detected":       detected,
            "n_trials":       total,
        })
        print(f"  {attack:20s}  detection rate: {detection_rate * 100:.1f}%  "
              f"({detected}/{total})")

    path = os.path.join(RESULTS_DIR, "attack_results.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nAttack results → {path}")


if __name__ == "__main__":
    print(f"Running attack suite ({N_TRIALS} trials per scenario)...\n")
    run_attack_suite()
