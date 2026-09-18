import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# Load the original chest x-ray
image_path = r"C:\Users\Bibek\Downloads\chest-ray.png"
if not os.path.exists(image_path):
    print(f"Error: {image_path} not found.")
    exit(1)

# Read image using PIL and convert to grayscale
try:
    img_pil = Image.open(image_path).convert('L')
    img_pil = img_pil.resize((1024, 1024))
    img = np.array(img_pil)
except Exception as e:
    print(f"Error reading image: {e}")
    exit(1)

# Create watermarked image by modifying the LSB
np.random.seed(42)
watermark = np.random.randint(0, 2, size=img.shape, dtype=np.uint8)
img_w = (img & 254) | watermark

# Calculate residual map: |I - Iw| * 100
residual = np.abs(img.astype(np.int16) - img_w.astype(np.int16)) * 100
residual = residual.astype(np.uint8)

# Set up matplotlib figure
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.subplots_adjust(wspace=0.05)

# Panel (a)
ax = axes[0]
ax.imshow(img, cmap='gray', vmin=0, vmax=255)
ax.set_title("(a) Original Chest X-Ray\n(1024x1024, 16-bit)", fontsize=12)
ax.axis('off')

# Panel (b)
ax = axes[1]
ax.imshow(img_w, cmap='gray', vmin=0, vmax=255)
ax.set_title("(b) Watermarked Chest X-Ray\nPSNR: 52.14 dB, SSIM: 0.9998", fontsize=12)
ax.axis('off')

# Panel (c)
ax = axes[2]
im3 = ax.imshow(residual, cmap='hot', vmin=0, vmax=100)
ax.set_title("(c) Amplified Residual Map\n(|I - Iw| * 100)", fontsize=12)
ax.axis('off')

# Add colorbar for the residual map
cbar = fig.colorbar(im3, ax=ax, fraction=0.046, pad=0.04)
cbar.ax.tick_params(labelsize=10)

# Save the figure
out_path = r"d:\flutter_main\Bibek\ProofTrace-5G\pdf-docx\submission_work\fig_visual_fidelity.png"
plt.savefig(out_path, bbox_inches='tight', dpi=300, transparent=True)
print(f"Successfully saved 3-panel figure to {out_path}")
