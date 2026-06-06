"""
Week 3 — 2D convolution + Sobel edges from scratch (numpy only).

PROBLEM
-------
1. Implement 2D cross-correlation/convolution with zero padding.
2. Use it to compute Sobel gradients and an edge-magnitude image.
3. (Bonus) Show a Gaussian blur is separable: blur with a 1D kernel twice.

Run:  python w3_convolution.py
"""
import numpy as np


def conv2d(img, kernel):
    """Valid 'same'-size 2D convolution with zero padding."""
    img = np.asarray(img, float)
    k = np.asarray(kernel, float)
    kh, kw = k.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(img, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant")
    out = np.zeros_like(img)
    # True convolution flips the kernel; for symmetric kernels it doesn't matter.
    kf = k[::-1, ::-1]
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            out[i, j] = np.sum(padded[i:i + kh, j:j + kw] * kf)
    return out


def sobel_edges(img):
    Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    Ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    gx = conv2d(img, Kx)
    gy = conv2d(img, Ky)
    return np.hypot(gx, gy), np.arctan2(gy, gx)


def gaussian_1d(sigma, radius=None):
    if radius is None:
        radius = int(3 * sigma)
    x = np.arange(-radius, radius + 1)
    g = np.exp(-(x ** 2) / (2 * sigma ** 2))
    return g / g.sum()


if __name__ == "__main__":
    # Synthetic image: bright square on dark background -> strong edges at borders.
    img = np.zeros((20, 20))
    img[6:14, 6:14] = 1.0

    mag, ang = sobel_edges(img)
    print("max edge magnitude:", round(mag.max(), 3))
    # Edges should be strongest on the square's border, ~zero in flat regions.
    assert mag[10, 10] < 1e-9            # interior is flat
    assert mag[6, 10] > 1.0             # top border has a strong edge

    # Separable Gaussian: 2D blur == two 1D passes
    g = gaussian_1d(1.5)
    G2d = np.outer(g, g)
    sep = conv2d(conv2d(img, g[None, :]), g[:, None])
    full = conv2d(img, G2d)
    assert np.allclose(sep, full, atol=1e-9)
    print("Convolution, Sobel, and separability checks OK")
