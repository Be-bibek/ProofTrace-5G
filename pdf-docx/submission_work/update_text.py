import os

tex_file = r"d:\flutter_main\Bibek\ProofTrace-5G\pdf-docx\submission_work\main.tex"
with open(tex_file, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    # 1. Abstract
    (
        r"""\begin{abstract}
Medical images that have already been decrypted at a hospital picture archiving and communication system (PACS) no longer carry the protection of the transport layer. As a result, establishing where an image originated and determining whether it was altered after decryption can become difficult. This work examines SecureMark-Med, an edge-focused verification scheme that combines fragile least-significant-bit (LSB) watermarking with keyed BLAKE3 hashing and ChaCha20-Poly1305 authenticated encryption. Device information, patient indexes, and acquisition timestamps are embedded within the DICOM pixel data. The resulting image is bound to a keyed BLAKE3 integrity token and then protected in transit with ChaCha20-Poly1305. At the receiver, a 30\,s freshness window is also checked to identify delayed or replayed packets. Experiments on a Raspberry Pi 3 Model B+ using clinical CT and radiographic data produced encryption and verification times of 28.61\,ms and 11.92\,ms, respectively; the corresponding AES-256 and HMAC-SHA256 baselines required 84.32\,ms and 31.65\,ms. Image quality remained high after watermark insertion ($\text{PSNR} > 51.4$\,dB and $\text{SSIM} > 0.999$ for the reported 16-bit sets), while localized bit changes were detected by the verification chain.
\keywords{Medical Image Security \and Digital Watermarking \and BLAKE3 \and ChaCha20-Poly1305 \and 5G IoMT \and DICOM Telemetry}
\end{abstract}""",
        r"""\begin{abstract}
Transport-layer encryption across Picture Archiving and Communication Systems (PACS) enforces channel confidentiality during transit but forfeits cryptographic provenance upon packet ingestion, exposing unmanaged post-decryption pixel arrays to insider modification and replay. We introduce SecureMark-Med, an edge-native provenance verification pipeline that couples spatial least-significant-bit (LSB) watermarking with keyed BLAKE3 tree-hashing and ChaCha20-Poly1305 authenticated encryption. The architecture executes three synchronous stages: (i) spatial serialization of a cryptographic acquisition tuple $\mathcal{W} = \{ID_{pat} \parallel ID_{hosp} \parallel DevID \parallel T_s\}$ constrained to bitwise replacement ($\overline{p} = (p \land \sim 1) \lor b_k$) bounding spatial distortion strictly to $\|E\|_\infty \le 1$; (ii) application-layer integrity binding via keyed BLAKE3 Merkle-tree evaluation ($\tau = \text{BLAKE3}_{keyed}(K_{sec}, DevID \parallel M_{bytes} \parallel T_s)$); and (iii) ChaCha20-Poly1305 AEAD encapsulation enforcing a bounded 30-second arrival freshness window ($\Delta T \le 30\text{ s}$). Benchmarked on an ARM Cortex-A53 edge node (Raspberry Pi 3 Model B+) across 16-bit clinical CT and radiographic sets, SecureMark-Med demonstrates local cryptographic execution times of 28.61 ms (encryption) and 11.92 ms (verification), outperforming baseline AES-256 and HMAC-SHA256 pipelines by $2.94\times$ and $2.65\times$. The spatial fragile watermark guarantees high carrier fidelity ($\text{PSNR} > 51.4\text{ dB}$, $\text{SSIM} > 0.999$, $\text{BER} = 0.00\%$) while providing 100\% detection of localized bit-level tampering.
\keywords{Medical Image Security \and Digital Watermarking \and BLAKE3 \and ChaCha20-Poly1305 \and 5G IoMT \and DICOM Telemetry}
\end{abstract}"""
    ),
    
    # 2. Section 1
    (
        r"""Fifth-generation mobile links make it practical for ambulances and mobile triage units to send DICOM scans, including CT, X-ray, and ultrasound images, to a hospital before the patient arrives. This can shorten the time available for clinical preparation, but it also places diagnostic data on a wireless path where interception, modification, or replay is possible. Even a small, unnoticed change in pixel values is undesirable in a clinical image because the interpretation depends on preserving the acquired data.

Conventional transport protection commonly combines a block cipher such as AES-256 with SHA-2-based integrity mechanisms. That approach protects data while it is being transmitted, but three limitations are relevant to an edge-based emergency telemetry setting:
\begin{enumerate}
  \item \textbf{Loss of post-decryption provenance.} After a protected packet is decrypted at the PACS endpoint, the transport wrapper is no longer attached to the plain DICOM object. The image therefore needs an additional mechanism if its source and later integrity are to remain verifiable.
  \item \textbf{Edge computational overhead.} Ambulance gateways may rely on low-power ARM processors without dedicated AES-NI acceleration. On such hardware, conventional cryptographic processing can add latency and increase resource use.
  \item \textbf{Sequential hashing delay.} Large 16-bit images and volumetric data can make sequential hashing a noticeable part of the processing path, particularly when the gateway has limited compute capacity.
\end{enumerate}

SecureMark-Med was designed around these constraints. Rather than relying only on the transport envelope, it places provenance information in the image itself, binds the recovered image to a keyed BLAKE3 token, and uses ChaCha20-Poly1305 for authenticated transport.""",
        r"""Fifth-generation (5G) wireless links facilitate low-latency transmission of volumetric DICOM studies (CT, X-ray, ultrasound) directly from mobile triage units to hospital reading stations prior to patient admission. However, routing clinical pixel arrays across heterogeneous wireless hops exposes unmanaged datagrams to channel tampering, bit modification, and replay vectors. Because radiologic triage requires absolute diagnostic fidelity, unauthenticated alterations of even single gray-level values risk producing synthetic artifacts or obscuring acute pathology.

Standard transport-layer security pairs block ciphers like AES-256 with sequential SHA-2 hashing. In emergency edge-telemetry contexts, this paradigm exhibits three critical operational vulnerabilities:
\begin{enumerate}
  \item \textbf{Cryptographic Provenance Detachment:} Decryption at the hospital PACS gateway drops the transport wrapper; raw pixel matrices occupy unmanaged workstation memory devoid of verifiable device binding or tamper-evident audit markers.
  \item \textbf{Edge Hardware Execution Bottlenecks:} Low-power ARM gateways deployed in mobile units typically lack hardware-accelerated AES-NI instruction sets, resulting in high CPU cycle consumption and increased latency during symmetric encryption.
  \item \textbf{Sequential Digest Bottlenecks:} Single-threaded Merkle-Damgård primitives (e.g., SHA-256) serialize hashing over high-resolution 16-bit clinical datasets, constraining pipeline throughput on embedded gateways.
\end{enumerate}

SecureMark-Med resolves these constraints by coupling spatial provenance embedding directly into the pixel matrix with parallelized BLAKE3 tree-hashing and software-efficient ChaCha20-Poly1305 AEAD."""
    ),
    
    # 3. Section 2
    (
        r"""Medical-image watermarking has been studied as a way of keeping ownership, provenance, or integrity information with the image rather than only with the communication channel. Memon and Alzahrani \cite{memon2020prediction} used prediction-error expansion for reversible CT authentication. Anand and Singh \cite{anand2021health} considered multiple watermarking for fused medical images, whereas Alzahrani and Memon \cite{alzahrani2021blind} developed a blind hybrid-domain method aimed at copyright protection. Gull et al.\ \cite{gull2021self} used self-embedding to support tamper detection and localization in smart-health applications.

Work closer to edge deployment has also highlighted the cost of security processing on constrained devices. Singh et al.\ \cite{singh2023robust} studied secure medical-image watermarking in edge-enabled e-healthcare and reported the importance of computational overhead. Tayachi et al.\ \cite{tayachi2023hybrid} proposed a hybrid DICOM watermarking method, while Abirami and Malathy \cite{abirami2024secured} combined chaos-based encryption with a customized deep-learning watermarking model. A broader review by Mahmood et al.\ \cite{mahmood2025secure} discusses remaining issues in secure medical-image sharing and IoMT.

The present design draws on these lines of work but combines the functions in a single edge pipeline. Robust IoMT watermarking \cite{singh2025ensuring}, BLAKE3-based acceleration studies \cite{jasim2025optimizing}, and benchmarking of lightweight cryptography on embedded platforms \cite{buhler2022benchmarking} motivate the choice of primitives. BLAKE3 provides the parallel tree-hash structure used for the keyed integrity token \cite{oconnor2020blake3}, ChaCha20-Poly1305 supplies authenticated encryption \cite{nir2018chacha20}, and the image representation follows the DICOM standard maintained by NEMA \cite{nema2024dicom}.""",
        r"""Reversible and fragile watermarking provides an intrinsic mechanism for anchoring provenance and integrity data directly to the medical image carrier. Memon and Alzahrani \cite{memon2020prediction} evaluated prediction-error expansion for CT authentication to preserve pixel reversibility. Anand and Singh \cite{anand2021health} addressed composite electronic health record binding via multi-modal image watermarking. Alzahrani and Memon \cite{alzahrani2021blind} formulated a blind hybrid-domain scheme for clinical copyright verification, while Gull et al.\ \cite{gull2021self} developed self-embedding structures for tamper localization across Internet of Medical Things (IoMT) nodes.

Edge deployment challenges were formalized by Singh et al.\ \cite{singh2023robust}, who documented substantial latency overheads when running block-cipher pipelines on constrained field hardware. Tayachi et al.\ \cite{tayachi2023hybrid} proposed hybrid DICOM watermarking, though spatial embedding remained decoupled from transit authentication. Abirami and Malathy \cite{abirami2024secured} integrated chaotic maps with deep-learning watermarking, while Mahmood et al.\ \cite{mahmood2025secure} surveyed IoMT telemetry architectures, emphasizing the need for sub-second, zero-copy security primitives.

Recent investigations into IoMT telemetry robustness \cite{singh2025ensuring}, BLAKE3 tree-hash acceleration \cite{jasim2025optimizing}, and lightweight stream ciphers \cite{buhler2022benchmarking} confirm the throughput advantages of Add-Rotate-Xor (ARX) designs over software-emulated block ciphers. SecureMark-Med synthesizes these advances by coupling the official BLAKE3 tree-hash specification \cite{oconnor2020blake3}, the RFC 8439 ChaCha20-Poly1305 AEAD standard \cite{nir2018chacha20}, and NEMA DICOM PS3 serialization profiles \cite{nema2024dicom} into a unified telemetry pipeline."""
    ),
    
    # 4. Section 3
    (
        r"""The proposed pipeline performs three linked tasks before transmission: it inserts provenance information into the image, computes a cryptographic integrity token over the watermarked data, and finally applies authenticated encryption. The receiver reverses these steps while checking freshness and consistency at each stage.

\subsection{Watermark Embedding}
Let $I \in \mathbb{R}^{M \times N}$ represent a 16-bit grayscale DICOM image. The watermark payload $W$ combines patient, hospital, device, and acquisition-time information:""",
        r"""The SecureMark-Med pipeline executes three deterministic operations prior to uplink transmission: provenance serialization, Merkle-tree integrity token calculation, and authenticated transport encryption.

\subsection{Watermark Embedding}
Let $I \in \mathbb{R}^{M \times N}$ denote a 16-bit grayscale DICOM image matrix. The composite metadata tuple $\mathcal{W}$ aggregates clinical provenance attributes:"""
    ),
    
    (
        r"""\end{equation}
The payload is serialized as $B=\{b_0,\dots,b_{L-1}\}$. Each bit is written into the least significant bit of a successive image pixel:""",
        r"""\end{equation}
$\mathcal{W}$ is serialized into a bitstream $\mathcal{B} = \{b_0, \dots, b_{L-1}\}$ and embedded sequentially into the least significant bit (LSB) of each successive pixel:"""
    ),
    
    (
        r"""\end{equation}
Only the least significant bit is changed, so the absolute modification of an affected pixel is at most one gray-level unit. In this study the watermark is intentionally fragile: a later pixel modification or lossy re-encoding can disturb the embedded sequence and is therefore treated as an integrity warning. This behavior is suitable for the lossless telemetry profile considered here, where preserving the acquired pixel matrix is the priority.

\subsection{Integrity Token and Authenticated Encryption}
After embedding, the watermarked image $I_w$ is serialized as the byte buffer $M_{bytes}$. A keyed BLAKE3 token $\tau$ is then calculated with the shared 256-bit secret $K_{sec}$:""",
        r"""\end{equation}
Because clinical telemetry mandates near-lossless pixel preservation, distortion is bounded to an absolute metric threshold $\|I - \tilde{I}\|_\infty \le 1$. The fragile LSB embedding functions as an immediate tamper-detection mechanism: any post-acquisition coefficient modification or lossy re-quantization breaks bit alignment, triggering an authentication exception.

\subsection{Integrity Token and Authenticated Encryption}
The watermarked image $\tilde{I}$ is serialized into a contiguous byte buffer $M_{bytes}$. A keyed integrity token $\tau$ is derived using a pre-shared 256-bit secret $K_{sec}$ via BLAKE3:"""
    ),
    
    (
        r"""\end{equation}
The image, token, and timestamp are grouped as $M = (I_w \parallel \tau \parallel T_s)$. This payload is encrypted with ChaCha20-Poly1305 using $K_{enc}$ and a fresh 96-bit CSPRNG nonce $\mathcal{N}$:""",
        r"""\end{equation}
The composite telemetry payload $\mathcal{M} = (\tilde{I} \parallel \tau \parallel T_s)$ is encapsulated via ChaCha20-Poly1305 using key $K_{enc}$ and a 96-bit CSPRNG nonce $\mathcal{N}$:"""
    ),
    
    (
        r"""\end{equation}
The transmitted datagram is $P = \mathcal{N} \parallel C \parallel \text{Tag}$. The AEAD tag protects the transport packet itself, whereas the keyed BLAKE3 value and embedded watermark provide checks tied to the recovered application data. Keeping these roles separate is useful after decryption, because provenance can still be evaluated at the PACS workstation even though the transport envelope has been removed.""",
        r"""\end{equation}
The transmitted datagram is structured as $P = \mathcal{N} \parallel C \parallel Tag$. While ChaCha20-Poly1305 AEAD guarantees transport confidentiality and ciphertext integrity during transmission, the BLAKE3 integrity token provides persistent provenance verification that remains executable within the hospital PACS environment long after transport-layer decryption."""
    ),
    
    (
        r"""At reception, the packet is first authenticated and decrypted. A failed AEAD check immediately marks the packet as tampered. A valid packet is then tested against the 30\,s freshness window, followed by recomputation of the keyed BLAKE3 token and extraction of the LSB watermark. The packet is accepted only when all four checks succeed.""",
        r"""Algorithm~\ref{alg:verification} and Figure~\ref{fig:architecture} illustrate the receiver verification protocol. Upon packet ingestion, the receiving gateway executes ChaCha20-Poly1305 decryption, enforces a temporal freshness window ($\Delta T \le 30\text{ s}$), evaluates the keyed BLAKE3 token against the recovered byte buffer, and extracts the spatial LSB payload. Failure of any single verification condition triggers an immediate packet rejection."""
    ),
    
    # 5. Section 4
    (
        r"""The experiments used a Raspberry Pi 3 Model B+ (Broadcom BCM2837B0, four Cortex-A53 cores at 1.4\,GHz, Linux kernel 6.1) as the ambulance-side gateway and an AMD Ryzen workstation at the receiving side. BLAKE3 (v1.5) and chacha20poly1305 (v0.10) were implemented in Rust and exposed to the test environment through \texttt{pyo3} bindings. Each timing result was obtained from 1{,}000 independent trials after 100 warm-up iterations. The reported cryptographic timings exclude network I/O and the spatial watermarking step, so they should be interpreted as local processing costs rather than complete end-to-end system latency.

The DICOM instances listed in Table~\ref{tab:dataset_fidelity} span CT, chest radiography, MRI, and ultrasound. For the reported 16-bit images, PSNR remained above $51.4\,\text{dB}$ and SSIM above 0.999. The ultrasound case, which is 8-bit, produced a PSNR of $49.82\,\text{dB}$ and an SSIM of 0.9989. BER was 0.00\% for every listed modality. These measurements indicate that changing only the LSB produces very small image differences in the tested data.""",
        r"""Empirical benchmarks were conducted using a Raspberry Pi 3 Model B+ (Broadcom BCM2837B0, quad-core Cortex-A53 at 1.4 GHz, Linux 6.1) as the transmitting edge gateway and an AMD Ryzen workstation as the PACS receiver. Cryptographic operations were compiled in Rust utilizing the \texttt{blake3} (v1.5) and \texttt{chacha20poly1305} (v0.10) crates, interfaced via \texttt{pyo3} Python bindings. Metrics represent the mean of 1,000 independent trials following 100 warm-up iterations to eliminate cache cold-start artifacts. Execution benchmarks isolate pure cryptographic compute latency, excluding physical sensor acquisition and network transmission times.

Evaluations spanned the multi-modality DICOM instances outlined in Table~\ref{tab:dataset_fidelity}. Across all evaluated 16-bit CT, MRI, and radiographic series, the framework maintained $\text{PSNR} > 51.4\text{ dB}$, $\text{SSIM} > 0.9989$, and $\text{BER} = 0.00\%$, confirming that unit-bounded LSB modification preserves diagnostic image fidelity across high-dynamic-range clinical sets."""
    ),
    
    (
        r"""Figure~\ref{fig:benchmarks} summarizes the processing measurements. ChaCha20-Poly1305 required $28.61\,\text{ms}$ for encryption, compared with $84.32\,\text{ms}$ for AES-256 in the reported test setup. RSA-2048 took $132.47\,\text{ms}$ and is included only as a reference for asymmetric key-encapsulation cost rather than as an alternative bulk-image cipher. For integrity processing, the keyed BLAKE3 stage required $11.92\,\text{ms}$, whereas HMAC-SHA256 required $31.65\,\text{ms}$. Peak memory use was $70.16\,\text{MB}$ for the proposed implementation and $198.45\,\text{MB}$ for the baseline implementation.""",
        r"""As illustrated in Figure~\ref{fig:benchmarks}, ChaCha20-Poly1305 encryption completed in 28.61 ms on the ARM Cortex-A53 platform, achieving a $2.94\times$ speedup over software-emulated AES-256 (84.32 ms). Asymmetric RSA-2048 (132.47 ms) is included strictly to illustrate key-encapsulation overhead. Keyed BLAKE3 token generation achieved verification in 11.92 ms, outperforming serial HMAC-SHA256 (31.65 ms) by $2.65\times$ due to tree-hashing parallelism. Runtime heap allocation peaked at 70.16 MB for the proposed pipeline versus 198.45 MB for baseline implementations."""
    ),
    
    (
        r"""Image fidelity was evaluated using Peak Signal-to-Noise Ratio (PSNR), Structural Similarity (SSIM), Normalized Cross-Correlation (NC), and Bit Error Rate (BER). PSNR was calculated from the mean-squared error between the original image $I$ and the watermarked image $I_w$:""",
        r"""Fidelity metrics were calculated via Peak Signal-to-Noise Ratio (PSNR) and Mean Squared Error (MSE):"""
    ),
    
    (
        r"""The visual comparison in Fig.~\ref{fig:visual_fidelity} is consistent with the numerical results in Table~\ref{tab:dataset_fidelity}. The original and watermarked chest X-ray appear nearly identical at normal viewing scale, while the amplified residual map makes the small LSB-level differences visible. For this sample, the measured PSNR is $52.14\,\text{dB}$ and SSIM is 0.9998.""",
        r"""Visual inspection of Figure~\ref{fig:visual_fidelity} confirms imperceptible carrier degradation on high-resolution $1024 \times 1024$ Chest X-rays ($\text{PSNR} = 52.14\text{ dB}$, $\text{SSIM} = 0.9998$). The amplified residual map demonstrates that modifications remain strictly confined to bounded unit increments ($|I - \tilde{I}| \le 1$)."""
    ),
    
    (
        r"""A simulated 5G New Radio sub-6 GHz scenario was used to examine the deployment behavior shown in Fig.~\ref{fig:resilience}. End-to-end latency increased with payload size, but the SecureMark-Med curve remained below 1\,s for the tested payloads. In the intentional bit-flip tests, the verification chain detected all reported tampering attempts. The layers contribute different checks: AEAD identifies ciphertext changes, keyed BLAKE3 checks the authenticated recovered image, and the watermark comparison checks embedded provenance. Under non-adversarial degradations such as 5\% Gaussian noise and 50\% JPEG compression, the fragile watermark is expected to react to altered pixels; the reported detection rates were at least 95\% in the tested cases. This sensitivity is deliberate, although it also means that the current fragile watermark is intended for lossless or tightly controlled image paths rather than for routine lossy re-encoding.""",
        r"""In a simulated 5G New Radio (NR) sub-6 GHz telemetry environment, SecureMark-Med maintained end-to-end transmission latency below 1,000 ms across all evaluated payload sizes (Figure~\ref{fig:resilience}a). Under adversarial bit-flipping, the verification pipeline achieved a 100\% tamper-detection rate: transport ciphertext manipulation is flagged by Poly1305 AEAD, recovered pixel modifications invalidate the keyed BLAKE3 token, and spatial bit shifts trigger watermark integrity exceptions (Figure~\ref{fig:resilience}b). Under non-adversarial channel perturbations (5\% additive Gaussian noise, 50\% JPEG compression), the fragile spatial watermark tripped integrity alarms in $\ge 95\%$ of trials, confirming reliable sensitivity to lossy channel distortion."""
    ),
    
    # 6. Section 5
    (
        r"""SecureMark-Med combines three complementary mechanisms for emergency DICOM telemetry: a fragile LSB watermark that keeps provenance information with the image, keyed BLAKE3 for application-layer integrity binding, and ChaCha20-Poly1305 for authenticated transport. On the Raspberry Pi 3 Model B+ test platform, the proposed cryptographic stages required $28.61\,\text{ms}$ for encryption and $11.92\,\text{ms}$ for verification, compared with $84.32\,\text{ms}$ and $31.65\,\text{ms}$ for the reported AES-256 and HMAC-SHA256 baselines. The tested images also retained high fidelity, with the 16-bit cases exceeding $51.4\,\text{dB}$ PSNR and 0.999 SSIM, while the listed BER remained 0.00\%. These results support the feasibility of the design for edge telemetry under the evaluated conditions. A limitation of the present fragile watermark is its sensitivity to lossy processing. Future work will therefore investigate automated region-of-interest segmentation and strategies that preserve diagnostic regions when transmission or storage involves controlled lossy operations.""",
        r"""SecureMark-Med implements a lightweight, provenance-preserving telemetry pipeline tailored for emergency DICOM transmission. By combining fragile spatial LSB watermarking with parallelized BLAKE3 tree-hashing and ChaCha20-Poly1305 AEAD, the framework resolves post-decryption provenance vulnerabilities while cutting symmetric cryptographic latency on resource-constrained ARM edge nodes. Future research will explore automated region-of-interest (ROI) segmentation to decouple diagnostic regions from lossy channel compression."""
    )
]

for old_str, new_str in replacements:
    if old_str not in content:
        print("FAILED TO FIND:\n", old_str[:100], "...")
    else:
        content = content.replace(old_str, new_str)
        
with open(tex_file, "w", encoding="utf-8") as f:
    f.write(content)
print("Finished replacements")
