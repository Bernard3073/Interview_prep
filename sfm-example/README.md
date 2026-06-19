# Minimal Incremental Structure-from-Motion (Python)

A small, readable SfM pipeline that takes a folder of overlapping images and
produces camera poses + a sparse 3D point cloud. Written as a **teaching
implementation** to accompany the interview-prep notes
([Week 10](../study-materials/10-zipline-aerial-perception-interview.md),
[Week 11](../study-materials/11-zipline-aerial-perception-answers.md)) — it favours
clarity over robustness. It is the same pipeline that, scaled up and fed aerial
survey imagery + GPS/IMU pose priors, builds the geometric world models discussed
in those notes.

> Not COLMAP. Use this to *understand and explain* SfM; use COLMAP/OpenMVG for
> production reconstructions.

## What it does

```
images ──► SIFT features ──► ratio-test matching + RANSAC fundamental-matrix
        ──► feature tracks (union-find) ──► two-view init (essential matrix)
        ──► triangulation ──► incremental PnP registration ──► sparse bundle
        adjustment ──► sparse_cloud.ply
```

Each stage maps to a study-notes talking point:

| Stage | Module | Notes ref |
|-------|--------|-----------|
| Detect/describe | `sfm/features.py` | features & descriptors |
| Match + verify | `sfm/matching.py` | Lowe ratio, RANSAC F |
| Tracks | `sfm/tracks.py` | multi-view correspondences |
| Pose / triangulate | `sfm/geometry.py` | essential matrix, DLT triangulation |
| Bundle adjustment | `sfm/bundle.py` | reprojection error, sparse Jacobian (Schur idea) — Week 10 §B1 |
| Driver | `sfm/reconstruction.py` | incremental SfM (Week 10 A1.1) |

## Install

```bash
cd sfm-example
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Quick start — no dataset needed

The synthetic demo exercises the geometry + bundle-adjustment core (numpy/scipy
only, **no images, no OpenCV**). It builds a known scene, perturbs it, and shows BA
driving the reprojection error back down:

```bash
python tools/synthetic_demo.py
```

Expected output (approx):

```
Scene: 8 cameras, 120 points, 960 observations.
Reprojection RMSE before BA:    ~5-15 px
Reprojection RMSE after  BA:    ~0.00 px
Median 3D point error after BA: ~0.00 (world units)
RESULT: PASS
```

## Run on your own images

Provide 5–30 photos of a static scene with good overlap (move ~15–30° between
shots; avoid pure rotation — you need translation/parallax):

```bash
python run_sfm.py --images path/to/images --out cloud.ply
# pass a calibrated focal length (pixels) for better geometry:
python run_sfm.py --images path/to/images --focal 2600 --out cloud.ply
```

Open `cloud.ply` in MeshLab / CloudCompare / Open3D to inspect the result.

## Tests

```bash
pip install pytest && python -m pytest -q
# or, without pytest:
python tests/test_geometry.py
```

## Known limitations (deliberately — these are the interview talking points)

- **Exhaustive O(n²) matching** — fine for tens of images; at scale use an
  image-retrieval shortlist (vocabulary tree / global descriptors).
- **No loop closure / pose-graph** — drift accumulates over long sequences; a real
  system adds loop detection and global BA, or anchors to GPS/IMU pose priors
  (which also fixes the scale ambiguity — see Week 10 §B1, A1.8).
- **Assumes a static scene** — moving objects are only handled implicitly via RANSAC
  outlier rejection; production adds semantic masking of dynamic classes (A1.10).
- **Uncalibrated default intrinsics** — pass `--focal`, or extend `io_utils` to load
  a full calibrated `K` (and distortion) for metric accuracy.
- **Sparse output only** — this gives the SfM skeleton (poses + sparse points); a
  dense cloud / mesh / DSM needs a follow-on MVS stage (Week 10 A1.2, B2).

## Layout

```
sfm-example/
├── run_sfm.py              # CLI: images -> sparse_cloud.ply
├── requirements.txt
├── sfm/
│   ├── camera.py           # intrinsics + pose container
│   ├── features.py         # SIFT detect/describe
│   ├── matching.py         # ratio test + RANSAC fundamental matrix
│   ├── tracks.py           # union-find multi-view tracks
│   ├── geometry.py         # essential matrix, pose, triangulation, reprojection
│   ├── bundle.py           # sparse bundle adjustment (scipy.least_squares)
│   ├── reconstruction.py   # incremental SfM driver
│   └── io_utils.py         # image loading + PLY export
├── tools/
│   └── synthetic_demo.py   # runs the BA core with no images/OpenCV
└── tests/
    └── test_geometry.py    # numpy/scipy unit tests
```
