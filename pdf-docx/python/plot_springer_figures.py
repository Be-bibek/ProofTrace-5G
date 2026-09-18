import matplotlib.pyplot as plt
import numpy as np

# Configure Springer Nature single-column / 1.5-column styling
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 8.5,
    'axes.labelsize': 9,
    'axes.titlesize': 9.5,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.titlesize': 10,
    'figure.dpi': 300,
    'lines.linewidth': 1.4,
    'lines.markersize': 5
})

# ====================================================================
# Figure 1: 3-Panel Benchmark Evaluation
# ====================================================================
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(9.5, 2.9))

# 1A: Encryption
ciphers = ['AES-256', 'RSA-2048', 'ChaCha20\n(Proposed)']
enc_ms = [84.32, 132.47, 28.61]
colors_a = ['#7f8c8d', '#95a5a6', '#27ae60']
b1 = ax1.bar(ciphers, enc_ms, color=colors_a, width=0.55, edgecolor='black', lw=0.6)
ax1.set_ylabel('Latency (ms)')
ax1.set_title('(a) Cipher Encryption Time')
ax1.grid(axis='y', ls='--', alpha=0.4)
for b in b1:
    ax1.text(b.get_x() + b.get_width()/2., b.get_height() + 2, f'{b.get_height():.1f}', ha='center', va='bottom', fontsize=7.5)

# 1B: Authentication
hashes = ['HMAC-SHA256', 'BLAKE3 (Raw)', 'SecureMark\n(Keyed BLAKE3)']
auth_ms = [31.65, 17.82, 11.92]
colors_b = ['#7f8c8d', '#bdc3c7', '#2980b9']
b2 = ax2.bar(hashes, auth_ms, color=colors_b, width=0.55, edgecolor='black', lw=0.6)
ax2.set_ylabel('Latency (ms)')
ax2.set_title('(b) Hash Verification Time')
ax2.grid(axis='y', ls='--', alpha=0.4)
for b in b2:
    ax2.text(b.get_x() + b.get_width()/2., b.get_height() + 0.6, f'{b.get_height():.1f}', ha='center', va='bottom', fontsize=7.5)

# 1C: Peak Memory
mems = ['AES-256', 'Conventional\n(SHA+AES)', 'SecureMark\n(Zero-Copy)']
mem_mb = [198.45, 142.37, 70.16]
colors_c = ['#7f8c8d', '#bdc3c7', '#8e44ad']
b3 = ax3.bar(mems, mem_mb, color=colors_c, width=0.55, edgecolor='black', lw=0.6)
ax3.set_ylabel('RAM Usage (MB)')
ax3.set_title('(c) Memory Footprint')
ax3.grid(axis='y', ls='--', alpha=0.4)
for b in b3:
    ax3.text(b.get_x() + b.get_width()/2., b.get_height() + 3, f'{b.get_height():.1f}', ha='center', va='bottom', fontsize=7.5)

plt.tight_layout()
plt.savefig('fig_benchmarks.png', dpi=300, bbox_inches='tight')
plt.close()

# ====================================================================
# Figure 2: 5G Telemetry Transmission Scaling & Attack Detection
# ====================================================================
fig, (ax_tx, ax_at) = plt.subplots(1, 2, figsize=(9.5, 3.2))

# 2A: Latency vs Size
payload_mb = np.array([0.064, 0.512, 2.0, 4.0])
conv_tx = [42.6, 161.8, 514.2, 986.4]
prop_tx = [18.7, 69.6, 248.5, 482.1]

ax_tx.plot(payload_mb, conv_tx, marker='s', color='#c0392b', ls='--', label='Conventional (AES-256 + SHA-256)')
ax_tx.plot(payload_mb, prop_tx, marker='o', color='#27ae60', label='SecureMark-Med (5G Pipeline)')
ax_tx.set_xlabel('DICOM Payload Dimension (MB)')
ax_tx.set_ylabel('End-to-End Latency (ms)')
ax_tx.set_title('(a) End-to-End Latency vs. Payload Size')
ax_tx.grid(True, ls='--', alpha=0.4)
ax_tx.legend(frameon=True, loc='upper left')

# 2B: Attack Detection vs Watermark Accuracy
attacks = ['No Attack', 'Gaussian (5%)', 'JPEG (50%)', 'Crop (25%)', 'Bit Flip']
tamper_det = [100.0, 99.23, 97.18, 95.42, 100.0]
wm_rec = [100.0, 97.12, 92.34, 85.41, 100.0]

x = np.arange(len(attacks))
w = 0.35
ax_at.bar(x - w/2, tamper_det, w, label='Tamper Detection Accuracy (%)', color='#2980b9', edgecolor='black', lw=0.6)
ax_at.bar(x + w/2, wm_rec, w, label='Watermark Correlation (NC %)', color='#f39c12', edgecolor='black', lw=0.6)

ax_at.set_ylabel('Verification Rate (%)')
ax_at.set_title('(b) Resilience Under Transmission Attacks')
ax_at.set_xticks(x)
ax_at.set_xticklabels(attacks, rotation=15, ha='right')
ax_at.set_ylim(70, 105)
ax_at.grid(axis='y', ls='--', alpha=0.4)
ax_at.legend(frameon=True, loc='lower left')

plt.tight_layout()
plt.savefig('fig_telemetry_resilience.png', dpi=300, bbox_inches='tight')
plt.close()
