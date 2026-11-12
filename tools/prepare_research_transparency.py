"""Remove the original illustration's near-white matte, retaining colored wisps.

The original PNG is never changed. Requires Pillow and NumPy.
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'assets/images/human-ai-head-network-share-20261112.png'
output = ROOT / 'assets/images/research-illustration-alpha-20261112.png'
rgb = np.asarray(Image.open(source).convert('RGB'), dtype=np.float64)
minimum = rgb.min(axis=2)
chroma = rgb.max(axis=2) - minimum

# Unmatte against white before applying alpha, to avoid white fringes.
alpha = np.clip((255 - minimum) * 4, 0, 255)
foreground = 255 - np.divide((255 - rgb) * 255, alpha[:, :, None],
                             out=np.full_like(rgb, 255), where=alpha[:, :, None] > 0)
# The source's blank paper has 0-2 channel levels of chroma. Suppress that
# residual grain smoothly; colored strokes keep their original appearance.
paper = minimum >= 245
alpha[paper] *= np.clip((chroma[paper] - 2) / 4, 0, 1)
rgba = np.dstack((np.rint(foreground).clip(0, 255), np.rint(alpha))).astype('uint8')
rgba[rgba[:, :, 3] == 0, :3] = 0
Image.fromarray(rgba, 'RGBA').save(output, optimize=True)
print(f'Saved transparent source: {output.name}')
