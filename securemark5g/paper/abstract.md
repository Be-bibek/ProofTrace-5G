# SecureMark5G — Abstract

**Title:** SecureMark5G: A Rust-Powered Lightweight Watermark-Assisted Cryptographic Authentication Protocol for Secure 5G IoT Networks

**Authors:** Bibek Das, Guru Nanak Institute of Technology, ECE Department

---

## Abstract

The rapid proliferation of Internet of Things (IoT) devices in fifth-generation (5G) networks
has exposed critical vulnerabilities in existing authentication frameworks, particularly
susceptibility to replay attacks, data tampering, and device impersonation. Existing
protocols such as 5G-AKA rely solely on cryptographic hashing and symmetric encryption,
offering no mechanism to detect payload tampering at the data-origin level after decryption.

This paper presents **SecureMark5G**, a novel lightweight authentication middleware that fuses
**Least Significant Bit (LSB) steganographic watermarking** with **BLAKE3-based token
authentication** and **ChaCha20-Poly1305 authenticated encryption** in a unified zero-copy
Rust pipeline. The watermark — a device-unique fingerprint embedded invisibly in sensor
float values — provides a forensic integrity check that persists even if an adversary
compromises the outer encryption layer.

We implement the protocol as an open-source Rust crate with Python bindings (via PyO3) and
evaluate it against an AES-256-GCM + SHA-256 Python baseline on 1,000 packet iterations.
SecureMark5G achieves an average authentication latency of **12 µs** (vs. 87 µs baseline),
a **7.3× speedup**, **5.5× lower memory usage**, and a tamper detection rate of **97%**
(vs. 62% for hash-only schemes). The replay detection rate achieves 100% within a 30-second
timestamp window.

These results demonstrate that combining steganographic watermarking with modern
cryptographic primitives in a zero-copy Rust implementation delivers both the speed required
for 5G URLLC latency constraints (< 1 ms) and a novel security property not achievable by
encryption alone.

**Index Terms:** 5G security, IoT authentication, LSB watermarking, BLAKE3, ChaCha20, Rust,
zero-copy pipeline, replay attack prevention, data integrity.
