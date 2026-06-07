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
*Click a question to reveal a model answer.*

??? What is a receptive field and how do you enlarge it without losing resolution?
The receptive field is the **region of the input that influences one output activation**; it grows with depth, kernel size, stride, and pooling. To enlarge it **without downsampling** (which loses spatial resolution) use **dilated/atrous convolutions**, encoder–decoder with skip connections (U-Net), larger kernels, or global-context/attention modules. It must be large enough that the network "sees" enough context to detect or segment big objects.

??? Implement IoU and NMS. What's the complexity of NMS?
**IoU** = intersection area / union area of two boxes (clamp overlap width/height to ≥0; `union = areaA + areaB − inter`). **NMS**: sort boxes by score descending, repeatedly take the top box, remove every remaining box with `IoU > threshold` against it, and continue. Complexity is **`O(n²)`** per class in the worst case (`O(n log n)` to sort + pairwise suppression). Variants: Soft-NMS (decay scores instead of deleting), matrix/cluster NMS for speed.

??? One-stage vs. two-stage detectors — trade-offs?
**Two-stage** (Faster R-CNN): region proposals then per-region classify/refine — higher accuracy (especially small objects) but slower and more complex. **One-stage** (YOLO/SSD/RetinaNet): predict directly on a dense grid — much faster and real-time, historically slightly less accurate until **focal loss** closed most of the gap. Robotics usually picks one-stage / anchor-free for latency; go two-stage when accuracy dominates and the latency budget allows.

??? How does PointNet handle the unordered nature of point clouds?
A point cloud is an **unordered set**, so the network must be **permutation-invariant**. PointNet applies a **shared MLP to each point independently**, then aggregates with a **symmetric function (max-pooling)** into a global feature — invariant to ordering. It also learns input/feature alignment (T-Nets). **PointNet++** adds hierarchical local grouping (sampling + ball query) to capture the local structure that vanilla PointNet misses.

??? Define mAP precisely — how is the PR curve built?
For one class, sort detections by confidence; sweeping the threshold, each detection is a **TP** (matches an unused GT with `IoU ≥ τ`) or **FP**, and you accumulate **precision** and **recall** to trace the PR curve. **AP** is the area under the (interpolated, monotonic-decreasing) PR curve. **mAP** is the mean AP over classes; COCO mAP also averages over IoU thresholds `0.5:0.05:0.95`. So it captures both localization quality and ranking.

??? How would you fuse a camera and a LiDAR for 3D detection? What can go wrong?
First **calibrate the extrinsics and time-sync** the sensors, then fuse — project LiDAR points into the image, or lift image features into a shared BEV/voxel space (early/mid/late fusion). LiDAR contributes accurate geometry, the camera contributes semantics/texture and longer range. What goes wrong: **calibration/extrinsic error and timestamp misalignment** (objects smear, worst on moving targets), differing FOV/resolution/sparsity, sensor dropout, and one modality dominating — so you need robust fusion and per-sensor failure handling.

??? A model is accurate offline but too slow on the robot — what are your options?
**Profile first** to find the real bottleneck, then: a smaller/efficient architecture (MobileNet, depthwise convs), **pruning + INT8 quantization** with TensorRT/ONNX, lower input resolution or frame rate, an ROI/cascade to skip background, run on a GPU/accelerator (Jetson, DLA), **knowledge distillation** to a smaller student, or temporal tricks (detect every Nth frame and track in between).

## Resources
- Stanford **CS231n** (CNNs for visual recognition) — notes + lectures.
- Papers: ResNet, Faster R-CNN, YOLO, U-Net, Mask R-CNN, PointNet, PointPillars, DETR.
- *Dive into Deep Learning* (d2l.ai) for hands-on.

➡ **Coding:** `coding-practice/robotics/w7_nms_iou.py`, `w7_map.py`
