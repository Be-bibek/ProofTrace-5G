**Abstract.** Medical images that have already been decrypted at a
hospital picture archiving and communication system (PACS) no longer
carry the protection of the transport layer. As a result, establishing
where an image originated and determining whether it was altered after
decryption can become difficult. This work examines SecureMark-Med, an
edge-focused verification scheme that combines fragile
least-significant-bit (LSB) watermarking with keyed BLAKE3 hashing and
ChaCha20-Poly1305 authenticated encryption. Device information, patient
indexes, and acquisition timestamps are embedded within the DICOM pixel
data. The resulting image is bound to a keyed BLAKE3 integrity token and
then protected in transit with ChaCha20-Poly1305. At the receiver, a 30
s freshness window is also checked to identify delayed or replayed
packets. Experiments on a Raspberry Pi 3 Model B+ using clinical CT and
radiographic data produced encryption and verification times of 28.61 ms
and 11.92 ms, respectively; the corresponding AES-256 and HMAC-SHA256
baselines required 84.32 ms and 31.65 ms. Image quality remained high
after watermark insertion (PSNR \> 51.4 dB and SSIM \> 0.999 for the
reported 16-bit sets), while localized bit changes were detected by the
verification chain.

**Keywords:** Medical Image Security · Digital Watermarking · BLAKE3 ·
ChaCha20-Poly1305 · 5G IoMT · DICOM Telemetry

# 1 Introduction

Fifth-generation mobile links make it practical for ambulances and
mobile triage units to send DICOM scans, including CT, X-ray, and
ultrasound images, to a hospital before the patient arrives. This can
shorten the time available for clinical preparation, but it also places
diagnostic data on a wireless path where interception, modification, or
replay is possible. Even a small, unnoticed change in pixel values is
undesirable in a clinical image because the interpretation depends on
preserving the acquired data.

Conventional transport protection commonly combines a block cipher such
as AES-256 with SHA-2-based integrity mechanisms. That approach protects
data while it is being transmitted, but three limitations are relevant
to an edge-based emergency telemetry setting:

> **1. Loss of post-decryption provenance.** After a protected packet is
> decrypted at the PACS endpoint, the transport wrapper is no longer
> attached to the plain DICOM object. The image therefore needs an
> additional mechanism if its source and later integrity are to remain
> verifiable.
>
> **2. Edge computational overhead.** Ambulance gateways may rely on
> low-power ARM processors without dedicated AES-NI acceleration. On
> such hardware, conventional cryptographic processing can add latency
> and increase resource use.
>
> **3. Sequential hashing delay.** Large 16-bit images and volumetric
> data can make sequential hashing a noticeable part of the processing
> path, particularly when the gateway has limited compute capacity.

SecureMark-Med was designed around these constraints. Rather than
relying only on the transport envelope, it places provenance information
in the image itself, binds the recovered image to a keyed BLAKE3 token,
and uses ChaCha20-Poly1305 for authenticated transport.

Table 1. Architectural comparison of medical image security schemes.

  ------------------------------------------------------------------------------
       Scheme          WM       Encryption   Integrity   Edge-Ready   Freshness
                                                                        Check
  ---------------- ----------- ------------ ----------- ------------ -----------
     Memon and          ✓          ---        Partial       ---          ---
  Alzahrani \[1\]                                                    

  Anand and Singh       ✓          ---          ---         ---          ---
       \[2\]                                                         

    Gull et al.         ✓          ---         Local        ---          ---
       \[4\]                                                         

    Singh et al.        ✓          AES       Checksum        ✓           ---
       \[5\]                                                         

   SecureMark-Med       ✓        ChaCha20     BLAKE3         ✓            ✓
  ------------------------------------------------------------------------------

# 2 Related Work

Medical-image watermarking has been studied as a way of keeping
ownership, provenance, or integrity information with the image rather
than only with the communication channel. Memon and Alzahrani \[1\], for
example, used prediction-error expansion for reversible CT
authentication. Anand and Singh \[2\] considered multiple watermarking
for fused medical images, whereas Alzahrani and Memon \[3\] developed a
blind hybrid-domain method aimed at copyright protection. Gull et al.
\[4\] used self-embedding to support tamper detection and localization
in smart-health applications.

Work closer to edge deployment has also highlighted the cost of security
processing on constrained devices. Singh et al. \[5\] studied secure
medical-image watermarking in edge-enabled e-healthcare and reported the
importance of computational overhead. Tayachi et al. \[6\] proposed a
hybrid DICOM watermarking method, while Abirami and Malathy \[7\]
combined chaos-based encryption with a customized deep-learning
watermarking model. A broader review by Mahmood et al. \[8\] discusses
remaining issues in secure medical-image sharing and IoMT.

The present design draws on these lines of work but combines the
functions in a single edge pipeline. Robust IoMT watermarking \[9\],
BLAKE3-based acceleration studies \[10\], and benchmarking of
lightweight cryptography on embedded platforms \[11\] motivate the
choice of primitives. BLAKE3 provides the parallel tree-hash structure
used for the keyed integrity token \[12\], ChaCha20-Poly1305 supplies
authenticated encryption \[13\], and the image representation follows
the DICOM standard maintained by NEMA \[14\].

# 3 Proposed SecureMark-Med Framework

The proposed pipeline performs three linked tasks before transmission:
it inserts provenance information into the image, computes a
cryptographic integrity token over the watermarked data, and finally
applies authenticated encryption. The receiver reverses these steps
while checking freshness and consistency at each stage.

## 3.1 Watermark Embedding

Let I ∈ R\^(M×N) represent a 16-bit grayscale DICOM image. The watermark
payload W combines patient, hospital, device, and acquisition-time
information:

W = IDpat ∥ IDhosp ∥ DevID ∥ Ts (1)

The payload is serialized as B = {b0, ..., bL−1}. Each bit is written
into the least significant bit of a successive image pixel:

p̃(i,j) = (p(i,j) ∧ \~1) ∨ bk, k = i·N + j, ∀ k \< L (2)

Only the least significant bit is changed, so the absolute modification
of an affected pixel is at most one gray-level unit. In this study the
watermark is intentionally fragile: a later pixel modification or lossy
re-encoding can disturb the embedded sequence and is therefore treated
as an integrity warning. This behavior is suitable for the lossless
telemetry profile considered here, where preserving the acquired pixel
matrix is the priority.

## 3.2 Integrity Token and Authenticated Encryption

After embedding, the watermarked image Iw is serialized as the byte
buffer Mbytes. A keyed BLAKE3 token τ is then calculated with the shared
256-bit secret Ksec:

τ = BLAKE3keyed(Ksec, DevID ∥ Mbytes ∥ Ts) (3)

The image, token, and timestamp are grouped as M = (Iw ∥ τ ∥ Ts). This
payload is encrypted with ChaCha20-Poly1305 using Kenc and a fresh
96-bit CSPRNG nonce N:

(C, Tag) = ChaCha20-Poly1305-Encrypt(Kenc, N, M) (4)

The transmitted datagram is P = N ∥ C ∥ Tag. The AEAD tag protects the
transport packet itself, whereas the keyed BLAKE3 value and embedded
watermark provide checks tied to the recovered application data. Keeping
these roles separate is useful after decryption, because provenance can
still be evaluated at the PACS workstation even though the transport
envelope has been removed.

**Algorithm 1 Receiver Verification and Provenance Extraction\**
Require: Datagram P; keys Kenc, Ksec; expected metadata DevID, Wexp;
clock Tnow\
Ensure: Verdict ∈ {Authentic, Tampered, Stale}\
1: Parse N ∥ C ∥ Tag ← P\
2: M ← ChaCha20-Poly1305-Decrypt(Kenc, N, C, Tag)\
3: if M = ⊥ then return Tampered (AEAD tag failure)\
4: Deconstruct (Iw ∥ τ ∥ Ts) ← M\
5: if \|Tnow − Ts\| \> 30 s then return Stale (expired freshness
window)\
6: τcalc ← BLAKE3keyed(Ksec, DevID ∥ Serialize(Iw) ∥ Ts)\
7: if τ ≠ τcalc then return Tampered (cryptographic hash mismatch)\
8: Extract Wext from the LSBs of Iw\
9: if Wext ≠ Wexp then return Tampered (provenance mismatch)\
10: return Authentic

![](media/image1.png){width="6.7in" height="2.09798009623797in"}

Fig. 1. Logical architecture and decision flow of the receiver
verification stage, showing the sequence of cryptographic, freshness,
and provenance checks.

At reception, the packet is first authenticated and decrypted. A failed
AEAD check immediately marks the packet as tampered. A valid packet is
then tested against the 30 s freshness window, followed by recomputation
of the keyed BLAKE3 token and extraction of the LSB watermark. The
packet is accepted only when all four checks succeed.

Table 2. Unified Dataset Attributes and Evaluated Diagnostic Fidelity
Metrics

  --------------------------------------------------------------------------------
    Modality    Resolution  Bit Depth  DICOM File PSNR (dB)     SSIM     BER (%)
                                          Size                          
  ------------ ------------ ---------- ---------- ---------- ---------- ----------
   Cranial CT   512 × 512     16-bit     512 KB     51.42      0.9997      0.00

  Chest X-Ray  1024 × 1024    16-bit     2.0 MB     52.14      0.9998      0.00

   Abdominal    512 × 512     16-bit     512 KB     53.08      0.9999      0.00
      MRI                                                               

    Cardiac     640 × 480     8-bit      900 KB     49.82      0.9989      0.00
   Ultrasound                                                           
  --------------------------------------------------------------------------------

# 4 Experimental Results and Discussion

The experiments used a Raspberry Pi 3 Model B+ (Broadcom BCM2837B0, four
Cortex-A53 cores at 1.4 GHz, Linux kernel 6.1) as the ambulance-side
gateway and an AMD Ryzen workstation at the receiving side. BLAKE3
(v1.5) and chacha20poly1305 (v0.10) were implemented in Rust and exposed
to the test environment through pyo3 bindings. Each timing result was
obtained from 1,000 independent trials after 100 warm-up iterations. The
reported cryptographic timings exclude network I/O and the spatial
watermarking step, so they should be interpreted as local processing
costs rather than complete end-to-end system latency.

The DICOM instances listed in Table 2 span CT, chest radiography, MRI,
and ultrasound. For the reported 16-bit images, PSNR remained above 51.4
dB and SSIM above 0.999. The ultrasound case, which is 8-bit, produced a
PSNR of 49.82 dB and an SSIM of 0.9989. BER was 0.00% for every listed
modality. These measurements indicate that changing only the LSB
produces very small image differences in the tested data.

## 4.1 Processing Latency and Resource Consumption

Figure 2 summarizes the processing measurements. ChaCha20-Poly1305
required 28.61 ms for encryption, compared with 84.32 ms for AES-256 in
the reported test setup. RSA-2048 took 132.47 ms and is included only as
a reference for asymmetric key-encapsulation cost rather than as an
alternative bulk-image cipher. For integrity processing, the keyed
BLAKE3 stage required 11.92 ms, whereas HMAC-SHA256 required 31.65 ms.
Peak memory use was 70.16 MB for the proposed implementation and 198.45
MB for the baseline implementation.

![](media/image2.png){width="6.7in" height="2.230180446194226in"}

Fig. 2. Performance benchmarks: (a) cipher encryption latency, (b) hash
verification delay, and (c) attack detection accuracy across the
evaluated vectors.

## 4.2 Diagnostic Image Fidelity

Image fidelity was evaluated using Peak Signal-to-Noise Ratio (PSNR),
Structural Similarity (SSIM), Normalized Cross-Correlation (NC), and Bit
Error Rate (BER). PSNR was calculated from the mean-squared error
between the original image I and the watermarked image Iw:

PSNR = 10 log10(MAXI² / MSE), MSE = (1/MN) Σi Σj \[I(i,j) − Iw(i,j)\]²
(5)

![](media/image3.png){width="6.7in" height="2.3878827646544183in"}

Fig. 3. Chest X-ray example showing the original image, the watermarked
image, and an amplified residual map. The reported sample has PSNR =
52.14 dB and SSIM = 0.9998.

The visual comparison in Fig. 3 is consistent with the numerical results
in Table 2. The original and watermarked chest X-ray appear nearly
identical at normal viewing scale, while the amplified residual map
makes the small LSB-level differences visible. For this sample, the
measured PSNR is 52.14 dB and SSIM is 0.9998.

## 4.3 5G Transmission Resilience and Tamper Detection

![](media/image4.png){width="6.7in" height="2.230180446194226in"}

Fig. 4. 5G telemetry performance and attack detection: (a) end-to-end
latency versus payload size and (b) verification behavior under the
evaluated transmission attacks.

A simulated 5G New Radio sub-6 GHz scenario was used to examine the
deployment behavior shown in Fig. 4. End-to-end latency increased with
payload size, but the SecureMark-Med curve remained below 1 s for the
tested payloads. In the intentional bit-flip tests, the verification
chain detected all reported tampering attempts. The layers contribute
different checks: AEAD identifies ciphertext changes, keyed BLAKE3
checks the authenticated recovered image, and the watermark comparison
checks embedded provenance. Under non-adversarial degradations such as
5% Gaussian noise and 50% JPEG compression, the fragile watermark is
expected to react to altered pixels; the reported detection rates were
at least 95% in the tested cases. This sensitivity is deliberate,
although it also means that the current fragile watermark is intended
for lossless or tightly controlled image paths rather than for routine
lossy re-encoding.

# 5 Conclusion

SecureMark-Med combines three complementary mechanisms for emergency
DICOM telemetry: a fragile LSB watermark that keeps provenance
information with the image, keyed BLAKE3 for application-layer integrity
binding, and ChaCha20-Poly1305 for authenticated transport. On the
Raspberry Pi 3 Model B+ test platform, the proposed cryptographic stages
required 28.61 ms for encryption and 11.92 ms for verification, compared
with 84.32 ms and 31.65 ms for the reported AES-256 and HMAC-SHA256
baselines. The tested images also retained high fidelity, with the
16-bit cases exceeding 51.4 dB PSNR and 0.999 SSIM, while the listed BER
remained 0.00%. These results support the feasibility of the design for
edge telemetry under the evaluated conditions. A limitation of the
present fragile watermark is its sensitivity to lossy processing. Future
work will therefore investigate automated region-of-interest
segmentation and strategies that preserve diagnostic regions when
transmission or storage involves controlled lossy operations.

# References

1\. Memon, N.A., Alzahrani, A.: Prediction-based reversible watermarking
of CT scan images for content authentication and copyright protection.
IEEE Access 8, 75448--75462 (2020).
https://doi.org/10.1109/ACCESS.2020.2989175

2\. Anand, A., Singh, A.K.: Health record security through multiple
watermarking on fused medical images. IEEE Trans. Comput. Soc. Syst.
9(6), 1594--1603 (2021). https://doi.org/10.1109/TCSS.2021.3126628

3\. Alzahrani, A., Memon, N.A.: Blind and robust watermarking scheme in
hybrid domain for copyright protection of medical images. IEEE Access 9,
113714--113734 (2021). https://doi.org/10.1109/ACCESS.2021.3104985

4\. Gull, S., Mansour, R.F., Aljehane, N.O., Parah, S.A.: A
self-embedding technique for tamper detection and localization of
medical images for smart-health. Multimed. Tools Appl. 80(19),
29939--29964 (2021). https://doi.org/10.1007/s11042-021-11170-x

5\. Singh, P., Devi, K.J., Thakkar, H.K., Bilal, M., Nayyar, A., Kwak,
D.: Robust and secure medical image watermarking for edge-enabled
e-healthcare. IEEE Access 11, 135831--135845 (2023).
https://doi.org/10.1109/ACCESS.2023.3335172

6\. Tayachi, M., Nana, L., Pascu, A.C., Benzarti, F.: A hybrid
watermarking approach for DICOM images security. Appl. Sci. 13(10), 6132
(2023). https://doi.org/10.3390/app13106132

7\. Abirami, R., Malathy, C.: Secured DICOM medical image transition
with optimized chaos method for encryption and customized deep learning
model for watermarking. Automatika 66(2) (2025).
https://doi.org/10.1080/00051144.2025.2460877

8\. Mahmood, S.D., Drira, F., Mahdi, H.F., Alimi, A.M.: Secure medical
image sharing: Technologies, watermarking insights, and open issues.
IEEE Access 13, 103995--104026 (2025).
https://doi.org/10.1109/ACCESS.2025.3574477

9\. Singh, P., Devi, K.J., Nayyar, A., Bilal, M.: Ensuring integrity and
security of medical image transmission in IoMT applications through
robust watermarking. Sci. Rep. 15(1), 14210 (2025).
https://doi.org/10.1038/s41598-025-11023-9

10\. Jasim, Z.A., Hadi, A.K.: Optimizing blockchain network performance
using BLAKE3 hash function in POS consensus algorithm. IEEE Access 13,
44760--44774 (2025). https://doi.org/10.1109/ACCESS.2025.3546723

11\. Bühler, H., Walz, A., Sikora, A.: Benchmarking of Symmetric
Cryptographic Algorithms on a Deeply Embedded System. IFAC-PapersOnLine
55(4), 266--271 (2022). https://doi.org/10.1016/j.ifacol.2022.06.044

12\. O'Connor, J., Aumasson, J.P., Neves, S., Wilcox-O'Hearn, Z.:
BLAKE3: One function, fast everywhere. Real World Crypto (2020).
https://doi.org/10.5281/zenodo.3899478

13\. Nir, Y., Langley, A.: ChaCha20 and Poly1305 for IETF Protocols. RFC
8439, Internet Engineering Task Force (2018).
https://doi.org/10.17487/RFC8439

14\. NEMA: Digital Imaging and Communications in Medicine (DICOM)
Standard, PS3.1--PS3.20. National Electrical Manufacturers Association,
Rosslyn, VA (2024). Available at: https://www.dicomstandard.org/
