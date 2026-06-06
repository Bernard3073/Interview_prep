"""
Week 7 — IoU and Non-Maximum Suppression from scratch.

PROBLEM
-------
A very common ML-perception coding question. Implement:
  - iou(boxA, boxB) for axis-aligned boxes [x1, y1, x2, y2]
  - nms(boxes, scores, iou_thresh) returning kept indices

Run:  python w7_nms_iou.py
"""
import numpy as np


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def nms(boxes, scores, iou_thresh=0.5):
    """Greedy NMS. boxes: (N,4), scores: (N,). Returns list of kept indices."""
    idxs = list(np.argsort(scores)[::-1])     # high score first
    keep = []
    while idxs:
        cur = idxs.pop(0)
        keep.append(cur)
        idxs = [i for i in idxs if iou(boxes[cur], boxes[i]) <= iou_thresh]
    return keep


if __name__ == "__main__":
    # Two clusters of overlapping boxes -> NMS should keep one per cluster.
    boxes = np.array([
        [10, 10, 50, 50],     # cluster A
        [12, 11, 52, 49],     # overlaps A
        [11, 9,  48, 51],     # overlaps A
        [100, 100, 140, 140], # cluster B
        [102, 98, 138, 142],  # overlaps B
    ], float)
    scores = np.array([0.9, 0.85, 0.8, 0.95, 0.7])

    assert abs(iou(boxes[0], boxes[0]) - 1.0) < 1e-9
    assert iou(boxes[0], boxes[3]) == 0.0          # disjoint

    keep = nms(boxes, scores, iou_thresh=0.5)
    print("kept indices:", keep)
    assert sorted(keep) == [0, 3], f"expected one box per cluster, got {keep}"
    print("IoU + NMS OK")
