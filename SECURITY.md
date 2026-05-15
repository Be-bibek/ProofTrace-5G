# SecureMark5G — Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in SecureMark5G, please do NOT open a
public GitHub issue. Instead:

1. Email: bibekdas1055@gmail.com
2. Subject line: `[SECUREMARK5G] Vulnerability Report`
3. Include: description, reproduction steps, severity assessment, proposed fix (if any)
4. You will receive a response within 48 hours
5. We will credit you in the release notes unless you prefer anonymity

---

## Cryptographic Design Decisions

### Hash Function: BLAKE3

BLAKE3 was chosen over SHA-256, SHA-3, and HMAC-SHA256 for the following reasons:

- **Speed:** BLAKE3 achieves 3+ GB/s on modern hardware vs SHA-256's ~500 MB/s,
  reducing authentication overhead on resource-constrained IoT devices.
- **Security:** BLAKE3 provides 128-bit security against collision and preimage
  attacks — identical to SHA-256.
- **Key derivation:** BLAKE3's `keyed_hash` mode provides MAC functionality without
  a separate HMAC construction.
- **Parallelism:** The Merkle-tree structure allows multi-threaded hashing on
  devices with multiple cores.

**NOT suitable for password hashing:** BLAKE3 is designed to be fast, which is
the wrong property for password storage. Use Argon2id for passwords.

### Encryption: ChaCha20-Poly1305

ChaCha20-Poly1305 (RFC 8439) was chosen over AES-256-GCM for IoT deployment:

- **No hardware dependency:** ChaCha20 is an ARX cipher (Add, Rotate, XOR) that
  runs efficiently in pure software. AES requires AES-NI hardware acceleration to
  be competitive — most IoT microcontrollers lack it.
- **Nonce misuse resistance:** The 96-bit random nonce space reduces the probability
  of nonce reuse to negligible levels across device fleets.
- **AEAD guarantee:** The Poly1305 authentication tag covers both ciphertext and
  associated data. Any modification causes decryption to fail deterministically.
- **Constant-time:** The RustCrypto implementation executes in constant time,
  eliminating timing side channels.

**Nonce:** Generated fresh from OS randomness for every packet via `OsRng`.
Never reuse a nonce with the same key. The current implementation generates a
new nonce per `encrypt()` call automatically.

### Watermark: LSB Steganography

The LSB watermarking layer is NOT a cryptographic primitive. It is a forensic
integrity mechanism. Its properties:

- **Invisibility:** LSB changes to float32 sensor values alter the reading by
  ±1.2 × 10⁻⁷, below any real sensor's noise floor.
- **Fragility (by design):** Payload tampering is detected because modifying any
  byte of the sensor data corrupts the LSB embedding.
- **Not secret:** The watermarking algorithm is public. Security comes from the
  device fingerprint value being unknown to attackers, not from the algorithm.

---

## Known Limitations

### Limitations of the Watermark Layer

1. **No forward secrecy:** The device fingerprint is static. If an attacker learns
   the fingerprint value (not the embedding algorithm), they could forge watermarks.
   Mitigation: rotate watermark strings periodically using the BLAKE3 key derivation
   mode with a session key.

2. **Capacity constraint:** Each float32 sample carries one bit. For a 32-byte
   watermark you need 256 float samples. Devices sending fewer than 256 sensor
   readings per packet must use a shorter watermark.

3. **Analog noise:** On extremely noisy sensors, random LSB flips from measurement
   noise could cause false positive tamper detections. Calibrate the noise floor
   before deployment.

### Limitations of the Replay Window

4. **Clock synchronization required:** The 30-second replay window assumes that
   device and server clocks are synchronized within ±15 seconds. Use NTP or a
   time-sync protocol on your 5G network. Without clock sync, replay protection
   may reject legitimate packets or fail to catch replays.

5. **Window size trade-off:** A smaller window (e.g., 5 seconds) provides stronger
   replay protection but requires tighter clock sync. The 30-second default is
   conservative for research demonstrations.

### Limitations of the PyO3 Bindings

6. **GIL:** Python function calls into Rust acquire the GIL on return. For
   high-throughput applications (>10,000 packets/second from Python), call
   `securemark5g.device_send` from multiple threads or use `asyncio` with
   `loop.run_in_executor`.

---

## Key Management

SecureMark5G does not manage keys — that is the application's responsibility.

**Required keys per device:**
- `secret_key` (32 bytes) — used for BLAKE3 token generation; device-unique
- `enc_key` (32 bytes) — used for ChaCha20 encryption; may be fleet-wide or device-unique

**Recommendations:**
- Generate keys with a cryptographically secure RNG: `secrets.token_bytes(32)` in Python
  or `OsRng` in Rust.
- Store keys in hardware secure elements (TPM, SE050, ATECC608) on IoT devices.
- Never hardcode keys in source code. Use environment variables or a secrets manager.
- Rotate keys when a device is compromised or decommissioned.

---

## What This Project Is NOT

SecureMark5G is a **research prototype** demonstrating the protocol.

It is NOT:
- A production-hardened security library (use libsodium or rustls for production)
- A key management system
- A certificate authority or PKI
- Resistant to side-channel attacks on all hardware (it is constant-time in software
  but not on hardware with variable-time multiply units — see chacha20poly1305 docs)
- Audited by a third-party security firm

For IEEE publication and academic research, these limitations must be disclosed in
the paper's Conclusion or Limitations section.

---

## Security Audit Status

| Component | Status |
|---|---|
| BLAKE3 crate | Formally reviewed by the BLAKE3 authors |
| chacha20poly1305 crate | Audited by NCC Group (see RustCrypto/AEADs audit reports) |
| LSB watermark module | Research code, not audited |
| PyO3 bindings | Not audited |

---

## Threat Model

**Assumed adversary capabilities:**
- Can intercept all 5G network traffic (passive eavesdropping)
- Can inject, modify, replay, and drop packets (active man-in-the-middle)
- Does NOT know the device's secret_key or enc_key
- Does NOT know the exact watermark value embedded in the data
- Does NOT have physical access to the IoT device

**Outside the threat model:**
- Adversaries with physical access to the device (hardware attacks)
- Adversaries who have extracted keys from a compromised device
- Quantum adversaries (BLAKE3 and ChaCha20 provide 128-bit quantum security via
  Grover's algorithm — considered sufficient for near-term 5G deployment horizons)

---

## Dependency Security

All cryptographic dependencies are from the RustCrypto project or the BLAKE3 team.
These are widely-used, actively maintained, and have received external security reviews.

To audit current dependency versions:

---

## ⚖️ License

This security policy and the SecureMark5G codebase are licensed under the **Apache 2.0 License**. See the [LICENSE](LICENSE) file for complete details.
