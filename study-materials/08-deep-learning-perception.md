# Week 8 — Deep Learning for Perception

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

## 8. BEV transformer architectures — *deep dive*

Multi-camera 3D perception increasingly happens in a shared **bird's-eye-view**
grid. The hard part is **lifting 2D image features to 3D** — a pixel is a *ray*,
not a point, so depth is ambiguous. Every method is a different answer to "how do
I resolve depth." Two paradigms:

- **Forward / "push" (Lift-Splat-Shoot, BEVDet):** predict a **per-pixel depth
  distribution**, take the outer product with the context feature, and **splat**
  the result into a voxel/BEV grid using the camera calibration. No queries; depth
  is explicit but only softly supervised.
  - *Lift:* per-pixel categorical depth × feature → points along each ray.
  - *Splat:* scatter into BEV cells with sum-pooling (the **cumsum trick** does
    this efficiently for variable points per cell).
  - *Shoot:* a BEV CNN head does detection/segmentation.
  - **BEVDepth** adds explicit LiDAR depth supervision because implicit depth is weak.
- **Backward / "pull" (BEVFormer, DETR3D):** start from **BEV (or object) queries**,
  project their 3D reference points into the images, and **sample** features back.
  No explicit depth needed; calibration is baked into the projection step.

**BEVFormer** is the most-asked architecture:
- **Spatial cross-attention:** each BEV-grid query lifts to a vertical pillar of 3D
  reference points, projects them into whichever cameras they hit, and uses
  **deformable attention** to sample only those locations — sparse, so it scales to
  multi-camera high-res inputs (dense global attention would be infeasible).
- **Temporal self-attention:** current BEV queries attend to the **previous
  timestep's BEV features** (warped by ego-motion) — a recurrent BEV memory that
  gives velocity cues and resolves occlusion.

**DETR3D / query-based detection:** sparse object queries predict a 3D reference
point, project to images, sample features, and iteratively refine. **Set
prediction + Hungarian (bipartite) matching** removes NMS, at the cost of slower,
sometimes unstable convergence early in training.

**Fusion & where it's going:** LiDAR/radar rasterize naturally into the same BEV
grid, so **BEVFusion** concatenates/attends across modalities in BEV. BEV's
weakness is that it **flattens the z-axis** (bad for tall/overhanging structure and
arbitrary shapes), which is why the field is shifting toward **3D occupancy
prediction** that restores height.

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

### BEV transformer questions

??? Why transform perception into BEV instead of working in image space?
BEV is **metric, ego-centric, and fusion-friendly**: scale is roughly constant (unlike perspective images where it varies with depth), every sensor — multi-camera, LiDAR, radar — rasterizes into the **same top-down grid**, it's temporally consistent across frames, and the output is directly consumable by tracking and planning. The core challenge is that **lifting 2D pixels to 3D is depth-ambiguous** — a pixel is a ray, not a point — so every BEV method is essentially a different way to resolve depth.

??? Compare forward-projection (lift) vs. backward-projection (query) BEV methods.
**Forward / "push" (LSS, BEVDet):** predict a per-pixel **depth distribution**, multiply by the feature, and **splat** points into the BEV grid via calibration. Depth is explicit but only softly supervised (hence BEVDepth adds LiDAR depth supervision). **Backward / "pull" (BEVFormer, DETR3D):** start from **BEV/object queries**, project their 3D reference points into the images, and **sample** features back — no explicit depth needed, but it's more sensitive to calibration/extrinsic error since projection is baked in. Push is intuitive and parallel; pull is sparse and scales well to many cameras.

??? Walk me through Lift-Splat-Shoot.
**Lift:** for each pixel predict a **categorical distribution over depth bins** and a context feature; their outer product places soft features at every candidate depth along the ray. **Splat:** use camera intrinsics/extrinsics to scatter those points into a BEV grid and **sum-pool** per cell — done efficiently with the **cumulative-sum trick** so you avoid a slow scatter-add over variable numbers of points per cell. **Shoot:** a BEV CNN head produces the final detection/segmentation. The depth *distribution* (not a single value) keeps it differentiable and hedges depth uncertainty so gradients flow to all bins.

??? Explain spatial cross-attention and temporal self-attention in BEVFormer.
**Spatial cross-attention:** each BEV-grid query lifts to a **vertical pillar of 3D reference points**, projects them into whichever cameras they fall in, and uses **deformable attention** to sample features at just those hit locations (averaged over overlapping views). It's sparse because dense global attention over multi-camera high-res features is computationally infeasible. **Temporal self-attention:** the current BEV queries attend to the **previous timestep's BEV features**, aligned by ego-motion — a recurrent BEV memory that supplies velocity cues and helps with occlusion.

??? Why deformable attention rather than vanilla attention in these models?
Vanilla attention is **quadratic** in the number of tokens; over several high-resolution camera feature maps that's intractable. **Deformable attention** has each query attend to only a **small set of learned sampling offsets** around its reference point, giving roughly linear cost while still focusing on the relevant image regions — which is exactly what's needed when a BEV query only projects to a few pixels in a few views.

??? How does DETR3D avoid dense BEV grids and NMS?
It uses **sparse object queries**: each predicts a 3D reference point, projects it into the images, samples features, and **iteratively refines** the box. Training uses **set prediction with Hungarian (bipartite) matching** — one prediction is matched to one ground-truth object — so duplicate boxes don't arise and **NMS is unnecessary**. The trade-off is slower, sometimes unstable convergence early on because the matching can be noisy before queries specialize.

??? How critical is camera calibration to BEV methods, and how do you handle drift?
Very — backward-projection methods **bake intrinsics/extrinsics into the projection**, so extrinsic error directly displaces where features land in BEV and smears objects (worst on moving targets). Mitigations: **per-frame/online calibration**, feeding extrinsics as network input, robustness augmentation (perturbing extrinsics during training), temporal fusion to average out noise, and online extrinsic estimation/monitoring with health checks. Forward-projection methods are somewhat more tolerant but still calibration-dependent.

??? What are BEV's main weaknesses, and why is the field moving to occupancy prediction?
BEV **flattens the z-axis**, so it loses vertical structure — poor for tall, overhanging, or oddly shaped objects — and it assumes a usable ground plane, quantizes space into a grid, and degrades at long range. **3D occupancy networks** predict whether each voxel in a full 3D grid is occupied (and its semantics), **restoring height** and representing **arbitrary/unknown shapes** without box priors — which is why occupancy has become the natural successor to flat BEV detection.

??? Design a multi-camera 3D detection system for a drone — which paradigm and why?
Clarify constraints first: **FOV coverage, range, compute budget, and calibration stability** on a vibrating airframe. For tight embedded budgets I'd lean **query-based (BEVFormer/DETR3D)** for its sparse, scalable attention and clean multi-camera overlap handling, with **temporal fusion** for velocity/occlusion — but if extrinsics drift badly in flight I'd favor a **forward-projection** approach (less sensitive to projection error) or add online calibration. Add **explicit depth supervision** if any depth/LiDAR source exists, fuse modalities in BEV, and budget latency via deformable sampling counts, BEV resolution, and INT8/TensorRT deployment. Validate with **nuScenes-style mAP/NDS** (NDS being a composite of mAP plus translation/scale/orientation/velocity/attribute errors).

## Resources
- Stanford **CS231n** (CNNs for visual recognition) — notes + lectures.
- Papers: ResNet, Faster R-CNN, YOLO, U-Net, Mask R-CNN, PointNet, PointPillars, DETR.
- *Dive into Deep Learning* (d2l.ai) for hands-on.

➡ **Practice (solve in-site):** [w7_nms_iou.py](practice.html?p=rob-iou-nms), [w7_map.py](practice.html?p=rob-average-precision), [w7_bev_splat.py](practice.html?p=rob-bev-splat), [w7_bev_project.py](practice.html?p=rob-bev-project)
