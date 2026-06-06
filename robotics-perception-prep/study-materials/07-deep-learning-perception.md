# Week 7 — Deep Learning for Perception

> Classical geometry tells you *where*; learned models increasingly tell you
> *what*. Modern perception stacks combine both. Know the building blocks, the
> task formulations, and the metrics.

---

## 1. CNN building blocks

- **Convolution layer:** learnable filters; weight sharing + locality → far fewer
  params than dense layers, translation equivariance.
- **Receptive field:** the input region one output neuron "sees" — grows with
  depth, stride, dilation. Must cover the object you want to detect.
- **Pooling / strided conv:** downsample, build invariance, enlarge receptive field.
- **Batch norm:** normalizes activations → faster, more stable training.
- **Residual connections (ResNet):** skip connections let very deep nets train
  (mitigate vanishing gradients).
- **Activation:** ReLU and variants.

> Be ready to compute output size: `out = (W − K + 2P)/S + 1`, and to reason about
> receptive field and parameter count.

---

## 2. Object detection

Goal: bounding boxes + class labels.

- **Two-stage (Faster R-CNN):** region proposals → classify + refine. Accurate,
  slower.
- **One-stage (YOLO, SSD, RetinaNet):** predict boxes directly on a grid. Fast,
  real-time; RetinaNet's **focal loss** addresses foreground/background imbalance.
- **Anchors:** predefined box priors; modern **anchor-free** detectors (FCOS,
  CenterNet) and **DETR** (transformer, set prediction) drop them.
- **Non-Max Suppression (NMS):** remove duplicate overlapping boxes, keep the
  highest-confidence one per object (you'll implement this).

## 3. Segmentation

- **Semantic segmentation:** per-pixel class (no instances). **U-Net** /
  DeepLab (encoder–decoder, dilated convs, skip connections).
- **Instance segmentation:** per-object masks. **Mask R-CNN** = Faster R-CNN +
  mask head.
- **Panoptic:** unifies semantic (stuff) + instance (things).

## 4. 3D perception

- **LiDAR point clouds** are unordered, sparse, irregular:
  - **PointNet / PointNet++:** operate directly on points with permutation-invariant
    pooling.
  - **Voxel/grid methods (VoxelNet, SECOND, PointPillars):** voxelize → 3D/2D conv;
    PointPillars is the real-time favorite.
- **BEV (bird's-eye-view):** project to top-down grid — natural for driving,
  fuses well across sensors.
- **3D object detection** outputs oriented 3D boxes (x,y,z,w,l,h,yaw).
- **Depth estimation:** monocular (learned) or stereo (cost-volume nets).

## 5. Sensor fusion with learned models

- **Early / mid / late fusion** of camera + LiDAR + radar.
- Camera gives semantics/texture; LiDAR gives accurate geometry → fuse for robust
  3D detection (e.g. project image features into BEV).
- Requires accurate **calibration + time sync** (same themes as classical).
- Transformer-based BEV fusion (BEVFormer, BEVFusion) is the current direction.

## 6. Metrics — *know these cold*

- **IoU** (Intersection over Union): `area(∩) / area(∪)` — the matching criterion.
- **Precision / Recall:** `P = TP/(TP+FP)`, `R = TP/(TP+FN)`.
- **AP / mAP:** area under precision–recall curve, averaged over classes (and IoU
  thresholds, e.g. COCO mAP@[.5:.95]).
- **Confusion matrix, F1**, per-class IoU (mIoU) for segmentation.

## 7. Training & deployment realities

- Data augmentation, class imbalance, label noise, domain gap (sim→real).
- Loss design: classification (cross-entropy/focal) + localization (L1/smooth-L1/
  GIoU).
- Deployment: quantization (INT8), pruning, TensorRT/ONNX, latency vs accuracy
  budgets on embedded GPUs. Robotics cares a lot about **real-time** inference.

---

## Interview-style questions
1. What is a receptive field and how do you enlarge it without losing resolution?
2. Implement IoU and NMS. What's the complexity of NMS?
3. One-stage vs. two-stage detectors — trade-offs?
4. How does PointNet handle the unordered nature of point clouds?
5. Define mAP precisely — how is the PR curve built?
6. How would you fuse a camera and a LiDAR for 3D detection? What can go wrong?
7. A model is accurate offline but too slow on the robot — what are your options?

## Resources
- Stanford **CS231n** (CNNs for visual recognition) — notes + lectures.
- Papers: ResNet, Faster R-CNN, YOLO, U-Net, Mask R-CNN, PointNet, PointPillars, DETR.
- *Dive into Deep Learning* (d2l.ai) for hands-on.

➡ **Coding:** `coding-practice/robotics/w7_nms_iou.py`, `w7_map.py`
