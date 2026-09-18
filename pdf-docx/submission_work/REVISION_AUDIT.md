# SecureMark-Med Revision Audit

This document records the exact changes made to the manuscript to address technical discrepancies, formatting requirements, and academic tone adjustments before final submission.

## 1. Writing & Tone
- **Abstract & Intro:** Removed hyperbolic claims ("indelible", "tamper localization", "real-world 5G deployability").
- **Hardware Profile:** Removed references to "AES-NI" (an Intel specification) in the context of ARM-based Raspberry Pi devices, replacing it with the more accurate "hardware-accelerated cryptography".

## 2. Cryptographic Alignment
- **Replay Protection Reality:** Audited the `securemark5g/src/replay.rs` file. Verified that it only implements timestamp age validation. 
  - **Action Taken:** Removed the "nonce cache" from `Algorithm 1` and all related text. Downgraded the feature claim from "Replay Defense" to "Freshness Check/Stale-Packet Rejection" across the paper and `Table 1`.
- **Benchmarking Baseline:** Clarified that the `RSA-2048` benchmark presented in Fig 1 represents "asymmetric key encapsulation" overhead rather than serving as an equivalent bulk-encryption payload cipher.

## 3. Reproducibility Adjustments
- **Environment:** Corrected false claims regarding the Python `cryptography` library.
  - **Action Taken:** Explicitly stated that core primitives run in Rust (`blake3` v1.5, `chacha20poly1305` v0.10) and are exposed via `pyo3` Python bindings.
- **Latency Disclaimers:** Clarified that the 100-iteration warm-up reduces "startup/initialization effects" (removing false claims about CPU frequency scaling). Explicitly stated that reported timing isolates local cryptographic execution, excluding network I/O and watermarking overhead.

## 4. Clinical Claims
- **Diagnostic Fidelity:** Removed all instances of the scientifically unsound phrase "zero diagnostic degradation."
  - **Action Taken:** Replaced with "negligible pixel-level distortion" and "high structural fidelity", supported by the >51.4 dB PSNR empirical tests.
- **Figure 3 Labeling:** Explicitly labeled the image in Figure 3 as a separate, illustrative 128x128 sample to resolve discrepancies with the full 512x512 data claims in Table 2, removing the unsupported claim that the 88.17 dB PSNR is universally "expected for smaller payloads."

## 5. Bibliography & References
- **[7] Abirami & Malathy (2024)**: Updated DOI to `10.1080/00051144.2025.2460877`.
- **[8] Mahmood et al. (2025)**: Updated DOI to `10.1109/ACCESS.2025.3574477`.
- **[9] Singh et al. (2025)**: Updated DOI to `10.1038/s41598-025-11023-9`.
- **[10] Jasim & Hadi (2025)**: Updated DOI to `10.1109/ACCESS.2025.3546723`.
- **[11] Balas et al. (2024)**: Replaced entirely with a verified IoT benchmarking paper: *Bühler et al., "Benchmarking of Symmetric Cryptographic Algorithms on a Deeply Embedded System," IFAC-PapersOnLine 55(4) (2022).*
- **[13] RFC 8439**: Maintained formatting for the ChaCha20-Poly1305 citation.
