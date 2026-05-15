"""Simulates IoT sensor readings for SecureMark5G testing and benchmarking.

Generates realistic float32 sensor data for:
  - Temperature (°C): 20.0 – 35.0
  - Humidity (%):     40.0 – 90.0
  - Pressure (hPa): 980.0 – 1020.0
  - GPS lat/lon:    -90 to 90 / -180 to 180

Data is packed as float32 bytes and is exactly what the IoT device sends
before watermark embedding.
"""
import random
import struct
from typing import List


def generate_sensor_data(n_samples: int = 64, seed: int = None) -> bytes:
    """Generate n_samples float32 sensor readings as raw bytes.

    n_samples must be >= 8 * watermark_byte_length for embedding to work.
    Default 64 samples supports up to 8-byte watermarks.

    Args:
        n_samples: Number of float32 sensor readings (each = 4 bytes).
        seed:      Optional seed for reproducibility in tests.

    Returns:
        Raw bytes of packed float32 values (n_samples * 4 bytes).
    """
    rng = random.Random(seed)
    values: List[float] = []

    for i in range(n_samples):
        ch = i % 4
        if ch == 0:
            values.append(round(rng.uniform(20.0, 35.0), 4))   # Temperature
        elif ch == 1:
            values.append(round(rng.uniform(40.0, 90.0), 4))   # Humidity
        elif ch == 2:
            values.append(round(rng.uniform(980.0, 1020.0), 4)) # Pressure
        else:
            values.append(round(rng.uniform(-90.0, 90.0), 4))  # GPS-like

    return struct.pack(f"{n_samples}f", *values)


def parse_sensor_data(raw: bytes) -> List[float]:
    """Unpack raw float32 bytes back to a list of floats."""
    n = len(raw) // 4
    return list(struct.unpack(f"{n}f", raw[:n * 4]))


def generate_device_metadata(device_id: str) -> dict:
    """Generate realistic device metadata for logging/paper results."""
    return {
        "device_id": device_id,
        "firmware_version": "1.2.0",
        "hardware": "ESP32-S3",
        "network": "5G-SA",
        "signal_dbm": random.randint(-100, -60),
    }
