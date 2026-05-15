# SecureMark5G — Literature Survey

## Section II: Related Work

### 2.1 5G Authentication Protocols

The 3GPP Release 15 specification introduces the **5G-AKA (Authentication and Key Agreement)**
protocol as the primary mechanism for subscriber authentication in 5G networks [1]. 5G-AKA
uses a challenge-response scheme based on symmetric keys stored in the Universal Subscriber
Identity Module (USIM), providing mutual authentication between the UE and the network.
However, 5G-AKA does not address the integrity of application-layer payload data transmitted
after the authentication handshake — a gap exploited in man-in-the-middle and replay attacks
targeting IoT device fleets.

**Limitation:** Once a 5G session is established, application-layer data packets carry no
device-origin proof beyond the session key. A compromised session key allows an adversary to
inject arbitrary payloads that pass all network-layer security checks.

### 2.2 Digital Watermarking in IoT

LSB steganographic watermarking has been studied extensively in multimedia security
(images, audio, video) [2, 3]. Its application to IoT sensor data is recent and sparse.
Panah et al. [4] proposed watermarking for medical IoT streams, but used a non-cryptographic
XOR scheme without replay protection. Garg and Kim [5] applied reversible watermarking to
industrial sensor telemetry but did not evaluate performance on constrained hardware.

**Gap addressed:** No existing work embeds device fingerprints directly into the LSBs of
float32 sensor readings and combines this with a cryptographic token and AEAD encryption in
a single unified pipeline.

### 2.3 Cryptographic Primitives for Constrained Devices

**SHA-256** is the most widely deployed hash function in IoT security stacks, yet it achieves
only ~500 MB/s single-core throughput on modern hardware and lacks native parallelism [6].
**BLAKE3**, introduced in 2020 [7], achieves 3+ GB/s through a Merkle-tree structure
enabling parallel hashing — a significant advantage for IoT gateways processing thousands
of device packets per second.

**AES-GCM** dominates authenticated encryption in TLS and IoT protocols but requires
hardware AES-NI instructions to be competitive. Most embedded processors (ESP32, STM32,
Raspberry Pi Zero) lack AES-NI. **ChaCha20-Poly1305** (RFC 8439) [8] is an ARX cipher
(Add, Rotate, XOR) delivering fast constant-time software execution on any 32-bit platform
without hardware acceleration — making it ideal for 5G IoT deployments.

### 2.4 Rust for Systems Security

Memory safety bugs (buffer overflows, use-after-free) account for ~70% of CVEs in C/C++
security libraries [9]. Rust's ownership model eliminates these at compile time without
garbage collection overhead — critical for latency-sensitive 5G applications.
The RustCrypto project [10] provides audited implementations of BLAKE3, ChaCha20, and
related primitives used in this work.

### 2.5 Summary of Gaps

| Property | 5G-AKA | Existing IoT WM | SecureMark5G |
|---|---|---|---|
| Device auth | ✓ | ✗ | ✓ |
| Payload watermark | ✗ | ✓ (partial) | ✓ (float LSB) |
| Replay protection | ✓ | ✗ | ✓ (30s window) |
| AEAD encryption | ✓ | ✗ | ✓ |
| Unified pipeline | ✗ | ✗ | ✓ (zero-copy) |
| Rust implementation | ✗ | ✗ | ✓ |
| Open source | ✗ | partial | ✓ (Apache 2.0) |

---

## References

[1] 3GPP TS 33.501, "Security architecture and procedures for 5G system," 2023.  
[2] R. G. van Schyndel, et al., "A digital watermark," ICIP 1994.  
[3] I. J. Cox, et al., "Digital Watermarking and Steganography," Morgan Kaufmann, 2007.  
[4] A. S. Panah, et al., "On the properties of non-media digital watermarking," IEEE Access, 2016.  
[5] S. Garg and J. Kim, "Watermarking techniques for IIoT streams," IEEE IoTJ, 2021.  
[6] NIST, "SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions," 2015.  
[7] J. O'Connor, et al., "BLAKE3: one function, fast everywhere," IACR ePrint 2020/667.  
[8] Y. Nir and A. Langley, "ChaCha20 and Poly1305 for IETF Protocols," RFC 8439, 2018.  
[9] M. Gaynor, "Memory safety in C/C++: A historical perspective," CVE Analysis, 2022.  
[10] RustCrypto Contributors, "RustCrypto: Cryptographic Algorithms," GitHub, 2024.
