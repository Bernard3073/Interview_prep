"""
Week 7 — Average Precision (AP) for object detection.

PROBLEM
-------
Given detections (with scores) and ground-truth boxes for one class, compute the
precision-recall curve and Average Precision (AP) at a fixed IoU threshold, using
the standard "all-points" (area-under-PR-curve) interpolation.

This exercises the full evaluation logic: matching detections to GT by IoU, in
descending score order, counting TP/FP, accumulating, integrating.

Run:  python w7_map.py
"""
import numpy as np
from w7_nms_iou import iou


def average_precision(detections, gts, iou_thresh=0.5):
    """
    detections: list of (box, score).
    gts: list of boxes (ground truth for this class, one image).
    Returns (ap, precision_curve, recall_curve).
    """
    dets = sorted(detections, key=lambda d: -d[1])
    n_gt = len(gts)
    matched = [False] * n_gt
    tp = np.zeros(len(dets))
    fp = np.zeros(len(dets))

    for k, (box, _) in enumerate(dets):
        best_iou, best_j = 0.0, -1
        for j, g in enumerate(gts):
            i = iou(box, g)
            if i > best_iou:
                best_iou, best_j = i, j
        if best_iou >= iou_thresh and not matched[best_j]:
            tp[k] = 1
            matched[best_j] = True
        else:
            fp[k] = 1

    tp_cum = np.cumsum(tp)
    fp_cum = np.cumsum(fp)
    recall = tp_cum / max(n_gt, 1)
    precision = tp_cum / np.maximum(tp_cum + fp_cum, 1e-9)

    # All-points interpolation: AP = ∫ p(r) dr with precision monotonic-decreasing
    mrec = np.concatenate([[0], recall, [1]])
    mpre = np.concatenate([[0], precision, [0]])
    for i in range(len(mpre) - 2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i + 1])
    idx = np.where(mrec[1:] != mrec[:-1])[0]
    ap = np.sum((mrec[idx + 1] - mrec[idx]) * mpre[idx + 1])
    return ap, precision, recall


if __name__ == "__main__":
    gts = [[10, 10, 50, 50], [100, 100, 140, 140], [200, 50, 240, 90]]
    detections = [
        ([11, 9, 49, 51], 0.95),     # TP for gt0
        ([101, 102, 139, 138], 0.90),# TP for gt1
        ([60, 60, 90, 90], 0.85),    # FP (matches nothing)
        ([198, 52, 242, 88], 0.80),  # TP for gt2
        ([12, 12, 48, 48], 0.60),    # duplicate of gt0 -> FP
    ]
    ap, prec, rec = average_precision(detections, gts, iou_thresh=0.5)
    print("precision:", np.round(prec, 3))
    print("recall   :", np.round(rec, 3))
    print(f"AP@0.5 = {ap:.3f}")
    # 3/3 GT eventually found -> recall reaches 1.0
    assert abs(rec[-1] - 1.0) < 1e-9
    assert 0.8 < ap <= 1.0
    print("AP computation OK")
