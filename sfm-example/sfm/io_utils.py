"""Image loading and PLY point-cloud export."""

from __future__ import annotations

import glob
import os

import cv2
import numpy as np


def load_images(folder: str, exts=(".jpg", ".jpeg", ".png", ".JPG", ".PNG")):
    """Load images from a folder (sorted by name). Returns (color, gray) lists."""
    paths = sorted(
        p for p in glob.glob(os.path.join(folder, "*")) if os.path.splitext(p)[1] in exts
    )
    if not paths:
        raise FileNotFoundError(f"No images found in {folder!r} (exts={exts})")
    color, gray = [], []
    for p in paths:
        img = cv2.imread(p, cv2.IMREAD_COLOR)
        if img is None:
            continue
        color.append(img)
        gray.append(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    return color, gray, paths


def write_ply(path: str, points: np.ndarray, colors: np.ndarray | None = None) -> None:
    """Write an ASCII PLY point cloud. colors: (N,3) uint8 RGB, optional."""
    points = np.asarray(points, dtype=np.float64)
    n = len(points)
    has_color = colors is not None and len(colors) == n
    header = [
        "ply",
        "format ascii 1.0",
        f"element vertex {n}",
        "property float x",
        "property float y",
        "property float z",
    ]
    if has_color:
        header += ["property uchar red", "property uchar green", "property uchar blue"]
    header.append("end_header")

    with open(path, "w") as f:
        f.write("\n".join(header) + "\n")
        if has_color:
            colors = np.asarray(colors, dtype=np.uint8)
            for (x, y, z), (r, g, b) in zip(points, colors):
                f.write(f"{x:.6f} {y:.6f} {z:.6f} {int(r)} {int(g)} {int(b)}\n")
        else:
            for x, y, z in points:
                f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
