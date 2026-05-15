# SecureMark5G — Architecture

## System Overview

SecureMark5G implements a five-stage pipeline that runs entirely inside a single Rust
library, callable from Python via PyO3 bindings.

```
IoT Device                          5G Channel          Server
─────────────────────────           ──────────          ────────────────────────
[Sensor Data (f32 array)]
       │
       ▼
[Watermark Embed]          ← LSB steganography (watermark.rs)
Device fingerprint hidden
in float LSBs
       │
       ▼
[BLAKE3 Token]             ← auth.rs
BLAKE3(device_id ‖ key ‖
       payload ‖ ts_nonce)
       │
       ▼
[ChaCha20-Poly1305]        ← crypto.rs
Encrypt(payload ‖ token
        ‖ timestamp)
       │
       └──────────────────────────────────────────────────────►
                                                               │
                                                       Decrypt (crypto.rs)
                                                               │
                                                       Replay check (replay.rs)
                                                       |now - ts| < 30s
                                                               │
                                                       Watermark verify
                                                       (watermark.rs)
                                                               │
                                                       Token verify (auth.rs)
                                                               │
                                                       ┌───────┴────────┐
                                                    Authentic       Rejected
```

---

## Module Breakdown

### watermark.rs — LSB Steganographic Watermarking

**Algorithm:** Each byte of the watermark string is spread across 8 consecutive
float32 sensor values. The least-significant bit (LSB) of each float's binary
representation is overwritten with one bit of the watermark.

**Why floats:** Sensor readings (temperature, pressure, GPS) are naturally float32.
Modifying the LSB of a float32 changes its value by at most 1.2 × 10⁻⁷ — well below
the measurement noise floor of any real sensor. The modification is physically invisible.

**Capacity:** 64 float samples can carry 8 bytes of watermark. 256 samples carry
32 bytes — enough for a full device UUID.

**Detection:** On the server side, `extract()` reads the LSBs back. If any byte of the
payload was modified in transit (tamper attack), the extracted watermark will not match
the registered device fingerprint.

**Mathematical notation for IEEE paper:**

```
Let S = [s₀, s₁, ..., sₙ₋₁] be the sensor float array.
Let W = [w₀, w₁, ..., wₘ₋₁] be the watermark bytes.
Let bᵢⱼ = (wᵢ >> j) & 1 be the j-th bit of watermark byte i.

Embed:  s̃ₖ = float32_from_bits( bits(sₖ) & (~1) | bᵢⱼ )
        where k = 8i + j

Extract: bᵢⱼ = bits(s̃ₖ) & 1
```

---

### auth.rs — BLAKE3 Authentication Token

**Why BLAKE3 over SHA-256:**

| Property | SHA-256 | BLAKE3 |
|---|---|---|
| Speed (single core) | ~500 MB/s | ~3+ GB/s |
| Parallelism | None | Tree-based, native parallel |
| Output size | 256 bits | 256 bits (extendable) |
| Security | 128-bit | 128-bit |
| Standard | NIST FIPS 180 | IETF (2024 draft) |

For 5G IoT devices authenticating thousands of packets per second, the 6× speed
improvement is architecturally significant.

**Token structure:**

```
token = BLAKE3(device_id ‖ secret_key ‖ watermarked_payload ‖ timestamp_u64_le)
```

The timestamp is a 64-bit Unix epoch (seconds) appended as 8 little-endian bytes.
It serves as the nonce, ensuring token uniqueness across time.

---

### crypto.rs — ChaCha20-Poly1305

**Why ChaCha20 over AES-256:**

AES requires hardware acceleration (AES-NI instruction set) to be fast. Most IoT
microcontrollers (ESP32, STM32, Raspberry Pi Zero) do NOT have AES-NI. On these
devices, software AES is slow. ChaCha20 is an ARX cipher (Add, Rotate, XOR) that
is fast in pure software on any 32-bit processor.

**AEAD guarantee:** The Poly1305 tag (16 bytes appended to ciphertext) authenticates
both the ciphertext and any associated data. Any single-bit modification to the
ciphertext body causes `decrypt()` to return an error — this is the outer integrity
check, complementing the inner watermark check.

**Packet format:**

```
[12 bytes: nonce][N bytes: ciphertext][16 bytes: Poly1305 tag]
```

The nonce is generated fresh for every packet using OS-provided randomness.

---

### replay.rs — Timestamp Window

Replay attacks resend a previously captured valid packet. SecureMark5G prevents this
by requiring the embedded timestamp to be within 30 seconds of the server's current
clock. An attacker capturing a packet at time T cannot replay it after T + 30s.

The window is configurable via `REPLAY_WINDOW_SECONDS`. Set lower for higher security,
higher for networks with poor time synchronization.

---

## Security Properties

| Attack | Defender | How |
|---|---|---|
| Eavesdropping | ChaCha20 | Ciphertext reveals nothing without the key |
| Replay | Timestamp window | Packets expire in 30 seconds |
| Tamper (payload) | Watermark verify | Extracted fingerprint mismatches |
| Tamper (ciphertext) | Poly1305 AEAD tag | Decryption fails before watermark check |
| Impersonation | BLAKE3 token | Token requires knowledge of secret_key |
| Fake device | Watermark registry | Device fingerprint not in registry |

---

## Dependency Graph

```
securemark5g (lib)
├── blake3 = "1.5"             ← BLAKE3-team/BLAKE3 (official)
├── chacha20poly1305 = "0.10"  ← RustCrypto/AEADs
├── pyo3 = "0.21"              ← PyO3/pyo3
├── thiserror = "1.0"          ← standard Rust error library
├── serde = "1.0"              ← serialization (future use)
├── serde_json = "1.0"         ← JSON output for benchmarks
└── hex = "0.4"                ← token hex display
```

---

## Performance Architecture

All five stages (embed, token, encrypt, transmit, verify) share one contiguous
memory buffer. There are zero heap allocations between stages on the device side.
This is the key reason for the µs-scale latency vs the Python baseline's ms-scale.

Rust's ownership model guarantees no buffer is read after it is mutated, eliminating
a class of memory-safety bugs common in C IoT implementations.

---

## IEEE Paper Mapping

| Paper section | Codebase location |
|---|---|
| Abstract | `paper/abstract.md` |
| Introduction | `paper/lit_survey.md` (background) |
| Literature Survey | `paper/lit_survey.md` |
| Proposed Method (Sec. III) | `src/watermark.rs` + `src/auth.rs` + `src/crypto.rs` |
| Algorithm (equations) | This file (mathematical notation above) |
| Implementation (Sec. IV) | All of `src/` + `python/` |
| Results (Sec. V) | `paper/results/` — CSV + PNG files |
| Security Analysis (Sec. VI) | Security Properties table above → `python/attack_test.py` |
| Conclusion | `paper/proposed_method.md` |

---

## ⚖️ License

This architecture and the associated codebase are licensed under the **Apache 2.0 License**.
