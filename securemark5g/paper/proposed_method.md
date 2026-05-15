# SecureMark5G — Proposed Method

## Section III: System Design and Protocol

### 3.1 Protocol Overview

SecureMark5G implements a five-stage zero-copy Rust pipeline:

```
Sensor data (f32 array)
    │  watermark.rs
    ▼
LSB watermark embed — device fingerprint in float LSBs
    │  auth.rs
    ▼
BLAKE3 token — BLAKE3(device_id ‖ key ‖ watermarked_payload ‖ timestamp)
    │  crypto.rs
    ▼
ChaCha20-Poly1305 encrypt — AEAD seal
    │  5G channel
    ▼
Server: decrypt → timestamp → token → watermark verify
```

### 3.2 LSB Steganographic Watermark Embedding

Let S = [s₀, s₁, ..., sₙ₋₁] be the sensor float array (IEEE 754 float32).
Let W = [w₀, w₁, ..., wₘ₋₁] be the m-byte device fingerprint.
Let bᵢⱼ = (wᵢ >> j) & 1 be the j-th bit of watermark byte i.

**Embed:** s̃ₖ = float32_from_bits( bits(sₖ) & (~1) | bᵢⱼ ), where k = 8i + j

**Extract:** bᵢⱼ = bits(s̃ₖ) & 1

**Imperceptibility:** Max value change = 2⁻²³ ≈ 1.19 × 10⁻⁷ (below any sensor noise floor).

**Capacity:** 256-sample packet carries a 32-byte device UUID.

### 3.3 BLAKE3 Authentication Token

T = BLAKE3(device_id ‖ Ks ‖ S̃_bytes ‖ ts₆₄)

where Ks is the 32-byte device secret key and ts₆₄ is the UNIX timestamp (LE 64-bit nonce).

### 3.4 ChaCha20-Poly1305 Encryption

P = ChaCha20-Poly1305_Ke(S̃_bytes ‖ T ‖ ts₆₄)

Packet format: N (12B nonce) ‖ ciphertext ‖ Poly1305 tag (16B).
Nonce generated fresh per packet from OS randomness.

### 3.5 Server Verification

1. **Decrypt** — Poly1305 tag must be valid
2. **Replay** — |t_now − ts₆₄| ≤ 30s
3. **Token** — Recompute T′; verify T′ == T (constant-time)
4. **Watermark** — extract(S̃, m) == W_registered (optional deep check)

### 3.6 Security Properties

| Attack | Mechanism | Basis |
|---|---|---|
| Eavesdropping | ChaCha20 | IND-CPA |
| Replay | Timestamp window | Nonce freshness |
| Tamper | Poly1305 + watermark | Auth + steganography |
| Impersonation | BLAKE3 token | PRF security |
| Device forgery | Watermark registry | Fingerprint uniqueness |

### 3.7 Novelty Claims

1. First unified pipeline combining LSB float watermarking + BLAKE3 MAC + ChaCha20 AEAD in zero-copy Rust.
2. Watermark as secondary integrity channel independent of the outer AEAD.
3. BLAKE3 delivers 6× throughput vs SHA-256 at identical security level.
4. ChaCha20 runs constant-time in pure software — no AES-NI required (critical for ESP32/STM32).
