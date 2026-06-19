#!/usr/bin/env python3
"""Run incremental SfM on a folder of images and export a sparse point cloud.

Usage:
    python run_sfm.py --images path/to/images --out cloud.ply
    python run_sfm.py --images path/to/images --focal 2600 --out cloud.ply

If --focal is omitted, a default focal length (~1.2 * image width) is assumed,
which is fine for a qualitative demo but not metrically accurate. For real work
pass a calibrated focal length (pixels) or extend this to load a full K matrix.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description="Minimal incremental Structure-from-Motion.")
    ap.add_argument("--images", required=True, help="Folder of input images.")
    ap.add_argument("--out", default="sparse_cloud.ply", help="Output PLY path.")
    ap.add_argument("--focal", type=float, default=None, help="Focal length in pixels.")
    ap.add_argument("--max-features", type=int, default=8000)
    ap.add_argument("--ratio", type=float, default=0.75, help="Lowe ratio threshold.")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    # Imports here so --help works even without numpy/opencv installed.
    from sfm.camera import PinholeIntrinsics
    from sfm.features import detect_many
    from sfm.io_utils import load_images, write_ply
    from sfm.matching import match_exhaustive
    from sfm.reconstruction import IncrementalSfM
    import numpy as np

    color, gray, paths = load_images(args.images)
    if len(gray) < 2:
        print("Need at least 2 images.", file=sys.stderr)
        return 2
    if not args.quiet:
        print(f"Loaded {len(gray)} images.")

    h, w = gray[0].shape[:2]
    K = PinholeIntrinsics.from_image_size(w, h, focal=args.focal).K

    feats = detect_many(gray, max_features=args.max_features)
    if not args.quiet:
        print("Features:", [len(f.xy) for f in feats])

    pairs = match_exhaustive(feats, ratio=args.ratio)
    if not args.quiet:
        print(f"Verified pairs: {len(pairs)}")
    if not pairs:
        print("No geometrically-verified matches; check overlap/order.", file=sys.stderr)
        return 3

    sfm = IncrementalSfM(feats, pairs, K, colors_per_image=color, verbose=not args.quiet)
    rec = sfm.run()

    if not rec.points3d:
        print("Reconstruction produced no points.", file=sys.stderr)
        return 4

    pts = np.array(list(rec.points3d.values()))
    cols = np.array([rec.colors[t] for t in rec.points3d.keys()])
    write_ply(args.out, pts, cols)
    print(f"Wrote {len(pts)} points to {args.out}")
    print(f"Registered {len(rec.cameras)} / {len(gray)} cameras.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
