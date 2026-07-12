# Zipline — Aerial Perception: Detailed Answers

> Full worked answers to every question in the
> [Week 12 question bank](12-zipline-aerial-perception-interview.md). Read this as
> the "what would a strong senior/staff answer actually say" companion. Where a topic
> already has a deep-dive in Week 12 Part B, this links rather than repeats.
>
> Through-line for every answer: **state the failure mode and whether it's a hazard.**
> A false "deliver here" can drop a package on a person, pool, or power line — so name
> the operating point and the asymmetric cost of errors.

---

# A1 — 3D Reconstruction & Multi-View Geometry

## A1.1 — SfM pipeline end to end; where it breaks on aerial imagery

**The pipeline:**
1. **Feature detection + description** — SIFT/SuperPoint per image.
2. **Matching** — nearest-neighbor in descriptor space + Lowe's ratio test, then
   geometric verification (RANSAC on the fundamental matrix) per image pair.
3. **Geometric verification / track building** — chain consistent matches across many
   images into *tracks* (one 3D point seen in N views).
4. **Initialization** — pick a good initial pair (wide enough baseline, many inliers),
   estimate relative pose from the essential matrix, triangulate seed points.
5. **Incremental registration** — register new images via PnP against known 3D points,
   triangulate new points, repeat.
6. **Bundle adjustment** — jointly refine all poses + points by minimizing
   reprojection error (see [Week 12 §B1](12-zipline-aerial-perception-interview.md#b1-bundle-adjustment-with-a-pose-prior)).
7. **Dense MVS** — after sparse SfM gives poses, run multi-view stereo for a dense
   cloud → mesh / DSM.

**Where it breaks on aerial survey imagery:**
- **Repetitive texture** (rows of identical roofs, crop fields, parking lots) →
  ambiguous matches; the ratio test throws away good matches *and* lets in wrong ones.
  Mitigate with geometric priors (you roughly know pose) to restrict the match search.
- **Large baselines / near-nadir geometry** — consecutive frames can have very
  *short* baselines (high overlap) giving weak triangulation (small parallax → huge
  depth uncertainty), while cross-strip pairs have large baselines with big appearance
  change. You need both, scheduled deliberately (overlap design).
- **Low parallax on flat ground** → near-degenerate triangulation; depth is poorly
  constrained exactly where you most need accurate ground elevation.
- **Scale / drift** — pure SfM is up-to-scale and accumulates drift over a long strip.
  Aerial wins here: fold the **GPS/IMU/RTK pose prior** into BA to make it metric and
  georeferenced and kill drift.
- **Moving objects / transient content** (cars, shadows, vegetation in wind) violate
  the static-scene assumption — see A1.10.
- **Illumination/atmospheric** differences between strips or flights hurt matching →
  use illumination-robust features and radiometric normalization.

## A1.2 — SfM vs MVS vs NeRF/3DGS for a backyard prior

- **SfM** recovers *sparse* structure + camera poses. It's the front end — you almost
  always run it (or use known poses) first. Not a final product on its own.
- **MVS (e.g. SGM, PatchMatch stereo)** takes known poses → *dense* depth/point cloud
  → DSM/mesh. Mature, robust, well-understood error characteristics, scales cheaply,
  and gives you a metric mesh you can measure clearances on. **This is the production
  default** for "I need geometry I can put numbers on at fleet scale."
- **NeRF** — great novel-view synthesis and implicit surfaces, but slow to train,
  per-scene, and historically poor on metric thin-structure geometry; mostly a
  research/visualization tool here.
- **3D Gaussian Splatting** — fast, high-quality novel views, increasingly used; but
  it's a radiance representation, not a clean metric surface, and extracting reliable
  meshes/clearances is still finicky. Promising but I'd pilot it, not bet the safety
  case on it.

**Decision:** for a *reusable geometric prior you measure against* (slope, clearance,
hazard heights), classical **SfM→MVS→DSM/DTM** is the right production choice because
its failure modes are understood and it produces metric surfaces directly. I'd track
3DGS for the cases where photometric realism helps (e.g. rendering training data or
human review), and adopt it only with a validated mesh-extraction + eval story. This
is exactly the "not-research, ship robust" judgment the role asks for.

## A1.3 — F vs E vs homography; when homography suffices

- **Fundamental matrix `F`** (3×3, rank 2): `x'ᵀ F x = 0`. Relates pixel
  correspondences in **uncalibrated** cameras. Encodes epipolar geometry; maps a point
  in one image to an epipolar *line* in the other. 7 DoF.
- **Essential matrix `E = K'ᵀ F K = [t]ₓR`**: same constraint on **calibrated**
  (normalized-ray) cameras. Decomposes into relative rotation + translation
  (translation up to scale). 5 DoF.
- **Homography `H`** (3×3): `x' = H x`, an exact point-to-point map (not point-to-line).

**When a homography suffices** (and you should prefer it — fewer DoF, more stable):
- The scene is **planar** (or effectively planar — e.g. flat ground, a wall, a
  facade), OR
- The camera undergoes **pure rotation** (no translation), so there's no parallax.

For aerial work over flattish ground a homography (or ground-plane rectification)
is often enough for stitching/orthomosaics; but anything with real 3D relief
(buildings, trees) needs full epipolar geometry + triangulation. A useful test:
fit both H and F via RANSAC and compare inlier support / residuals (the "GRIC"-style
model-selection idea) to decide if the scene is degenerate-planar.

## A1.4 — Fusing a pose prior into bundle adjustment

Covered in full in
[Week 12 §B1](12-zipline-aerial-perception-interview.md#b1-bundle-adjustment-with-a-pose-prior).
Summary of the key points to say out loud:
- Add a residual `r = Log(C̄ⱼ⁻¹ Cⱼ) ∈ ℝ⁶` per camera (SE(3) tangent space), weighted by
  the pose covariance `Σ_pose`.
- Total cost = `Σ reprojection²_Σ + Σ ‖r‖²_{Σ_pose}` with robust kernels on reprojection.
- **Weighting is everything:** RTK-fixed → tight translation prior → fixes absolute
  scale + georeferencing → eliminates monocular scale ambiguity and drift. Loose GPS →
  soft regularizer/seed. Units must be consistent (pixels vs meters/radians) or BA
  silently biases toward whichever residual is mis-scaled.
- Result: metric, georeferenced reconstruction keyed to a street address — what a
  world model needs.

## A1.5 — Satellite imagery → metric elevation; DSM vs DTM

Full deep-dive:
[Week 12 §B2](12-zipline-aerial-perception-interview.md#b2-dsm-vs-dtm--and-why-landing-cares).
Key points:
- Multi-view stereo across overlapping frames → dense cloud → rasterize to a **DSM**
  (top of everything).
- Filter non-ground returns (cloth-simulation / morphological / learned classifier) +
  interpolate → **DTM** (bare ground).
- **nDSM = DSM − DTM** = object height above ground — the most useful layer for
  delivery (clearance).
- Landing needs **DTM** (true surface + slope) *and* **nDSM** (canopy/obstacle
  clearance). A flat patch under a tree is not deliverable. The classic trap is
  quoting only the DSM and forgetting the canopy hides the ground.
- For *satellite specifically* (vs drone), expect coarser GSD (0.3–0.5 m), stereo from
  along-track pairs or multiple passes, and rational polynomial camera (RPC) models
  instead of pinhole — mention RPC refinement / bias correction.

## A1.6 — Bundle adjustment: what's optimized, sparsity, Schur

Full deep-dive in
[Week 12 §B1](12-zipline-aerial-perception-interview.md#b1-bundle-adjustment-with-a-pose-prior).
The three-sentence version: BA minimizes total reprojection error over all camera
params and 3D points. Its Hessian `JᵀJ` is sparse because each observation touches
exactly one camera and one point, giving block-diagonal camera (`U`) and point (`V`)
blocks with sparse coupling (`W`). The **Schur complement** eliminates the millions of
points (cheap 3×3 `V⁻¹` inverses) into a small reduced camera system `(U − W V⁻¹ Wᵀ)Δc`,
which is what makes BA tractable at scale (Ceres/g2o/GTSAM all do this).

## A1.7 — Registering a fresh survey to an existing model (change detection)

Goal: align today's reconstruction to the stored prior so you can diff them.

**Approaches, coarse→fine:**
1. **Georeference both** (you have GPS/RTK) → they're already roughly aligned in a
   common ENU/UTM frame. Often gets you within a meter for free.
2. **Feature-based global alignment** — FPFH or learned 3D descriptors + RANSAC to get
   a coarse rigid transform when georeferencing is weak.
3. **ICP refinement** — point-to-plane ICP (see
   [Week 12 §C1](12-zipline-aerial-perception-interview.md#c1-point-to-plane-icp-robust))
   for the final fine alignment. Use **trimmed/robust** ICP because the scenes
   genuinely differ (that's the point — you're detecting change), so a vanilla ICP
   would try to "explain" real changes as misalignment.
4. **Learned registration** (e.g. deep closest point / correspondence networks) when
   overlap is low or initialization is poor.

**Then detect change:** compute cloud-to-cloud / DSM difference (M3C2 is the standard
robust metric), threshold by *expected* noise, and **semantically gate** it — a 2 m
positive change that's labeled "tree" is canopy growth; the same change labeled
"structure" is a new shed that changes deliverability. Output a change mask + updated
hazard layer, and flag large/critical changes for re-validation.

**Pitfall to name:** ICP converges to local minima; always seed it with the
georeferenced/feature-based coarse alignment, never from identity on shifted clouds.

## A1.8 — Monocular scale ambiguity and how to resolve it

Monocular SfM recovers structure only **up to an unknown global scale** (and, from a
single essential matrix, translation only up to scale): you can't tell a small scene
up close from a big scene far away from images alone.

Ways to resolve it, ranked by what's available in this deployment:
- **Metric pose prior (best here):** GPS/RTK gives camera positions in meters → BA
  recovers absolute scale directly. This is the dominant fix for aerial.
- **Known baseline / stereo rig:** a calibrated two-camera baseline gives metric depth.
- **IMU fusion (visual-inertial):** gravity + accelerometer integration observes scale
  (the trick that makes VIO metric).
- **Known object / GCP:** a ground control point or an object of known size in view.
- **Known camera height above ground / altimeter:** scales the ground plane.
- **LiDAR or depth sensor:** directly metric.

For Zipline you lean on **RTK pose + (optionally) IMU**, which is why your
reconstructions can be metric and georeferenced rather than arbitrary-scale.

## A1.9 — Robust estimation with 50% outliers; threshold choice

**RANSAC** samples minimal sets, fits, counts inliers within a threshold, keeps the
best, refits. With 50% outliers (`w = 0.5`) and a minimal set of `s` points, iterations
for success prob `p`: `N = log(1−p) / log(1 − wˢ)`. For `s=4` (homography), `w=0.5`,
`p=0.99` → `N ≈ 72`; for `s=8` (F) it explodes (~1177) — a reason to prefer minimal
solvers (5-point E).

- **RANSAC** uses a hard inlier threshold — sensitive to the choice; too tight loses
  inliers, too loose accepts outliers.
- **MSAC/LO-RANSAC** soften this (truncated quadratic cost; local optimization on the
  inlier set) — usually strictly better, free to adopt.
- **MAGSAC++** *marginalizes over the threshold* — you avoid picking `σ` by hand; great
  when you don't know the noise scale. My default for production fundamental/homography
  estimation.
- **LMedS** needs no threshold but breaks down past 50% outliers — fine as a fallback
  for ≤50%, not for high-contamination matching.

**Picking the threshold principledly:** don't eyeball pixels. Model the inlier residual
as Gaussian with std `σ` (your keypoint localization noise, often ~1 px scaled by
octave). The squared reprojection error is then χ²-distributed, so set the threshold at
a confidence quantile: `t² = χ²_{k}(0.95)·σ²` (k = error dimension, e.g. 2 for point
distance, ~3.84·σ² for a 1-DoF epipolar distance). This ties the threshold to a
*probability of rejecting an inlier* rather than a magic number — and MAGSAC removes
even that choice.

## A1.10 — Moving objects violating the static-scene assumption

Cars, people, pets, blowing vegetation, and moving shadows break the "one rigid world"
assumption and corrupt both matching and triangulation.

**Defenses, layered:**
- **Robust BA + RANSAC** already downweight a *minority* of moving points as outliers —
  sufficient when dynamics are sparse.
- **Semantic masking:** run segmentation first and **exclude dynamic classes**
  (vehicles, people, animals) from feature extraction/matching — cheap and effective,
  and you're already segmenting for the world model.
- **Multi-view / temporal consistency:** a static point reprojects consistently across
  many frames; a moving point won't triangulate to a stable 3D location → reject tracks
  with high reprojection residual or short temporal support.
- **Capture-time mitigation:** survey when activity is low; fuse multiple passes and
  keep the **temporally stable median** surface (a moving car appears in one pass, not
  the consensus).
- **Treat dynamics as their own output:** don't just discard them — "a car is usually
  parked here" / "people frequently in this area" is *deliverability-relevant* prior
  information, not noise.

---

# A2 — Semantic Segmentation & Learned Perception

## A2.1 — Segmentation of deliverable surfaces; safety-driven design

**Class design driven by the decision, not by what's easy to label.** Group classes by
their effect on delivery:
- **Landable:** grass, dirt, concrete/pavement, deck.
- **Hard no / hazard:** pool/water, vehicle, power line, trampoline, people/pets,
  steep roof, dense canopy.
- **Context:** fence, building footprint, road (helps reason about access/setbacks).

**How safety changes the model:**
- **Asymmetric loss / class weighting:** missing a pool is catastrophic; misclassifying
  grass-as-dirt is harmless. Weight the loss (or use focal loss) so false-negatives on
  hazard classes are punished hardest. Hazards are also *rare* → class imbalance, so
  weighting/oversampling/hard-negative mining is mandatory.
- **Recall-biased operating point on hazards:** tune thresholds per class — high recall
  on pools/lines/people even at the cost of precision; a false hazard just refuses a
  good yard, a missed hazard is an incident.
- **Eval reflects this:** report **per-class** recall on hazards separately with a hard
  gate (see A5.3), not just mean IoU.
- **Uncertainty:** output calibrated confidence; route low-confidence regions to human
  review rather than guessing.

**Architecture:** a strong encoder (DINOv2/ViT or ConvNeXt backbone) + segmentation
head (UPerNet/Mask2Former), tiled for resolution (A2.2). Nothing exotic — robustness
and eval discipline matter more than architecture novelty here.

## A2.2 — Aerial segmentation: scale variation and tiny objects

Aerial frames are huge (tens of MP) and objects span orders of magnitude (a power line
is a few pixels wide; a roof is thousands). You can't feed a full frame at native res,
and downsampling destroys the thin safety-critical structures.

**Techniques:**
- **Tiling with overlap:** cut the image into overlapping tiles (e.g. 512–1024 px,
  10–25% overlap), infer per tile, then **blend** overlaps (average logits or weighted
  feathering) to avoid seams. Overlap prevents objects on tile borders from being cut.
- **Multi-scale inference:** run several scales and fuse — captures both the thin lines
  and the large regions.
- **Context vs resolution tradeoff:** thin objects need fine resolution *and* context
  (a line is only recognizable along its length). Use dilated/atrous convolutions or
  attention for a large receptive field without downsampling away the detail.
- **Preserve GSD:** normalize all imagery to a consistent ground-sample-distance so the
  model sees objects at a consistent pixel size — otherwise a "car" is 20 px in one
  flight and 60 in another.
- **Test-time tricks:** sliding-window with Gaussian weighting toward tile centers;
  flip/rotate TTA for the hard classes.
- **Targeted sampling in training:** oversample tiles containing rare/thin classes so
  the model actually sees enough power-line pixels.

## A2.3 — Fusing 2D semantics into a 3D world model

Full deep-dive in
[Week 12 §B3](12-zipline-aerial-perception-interview.md#b3-projecting-2d-semantics-into-the-3d-model-multi-view-label-fusion).
The points to hit:
- Project each 3D primitive into every camera that sees it; **occlusion-test against
  the rendered depth** (the #1 bug — otherwise you paint roof labels onto the ground
  behind it).
- Fuse **soft probabilities** (not argmax) via a weighted log-opinion pool; weight each
  view by angle/range/blur/mask-confidence.
- Argmax for the label, **keep entropy as an uncertainty layer** feeding deliverability
  and active learning.
- **Disagreement is signal:** high-entropy regions → request a re-fly or human label.
  For thin hazards use **recall-biased fusion**: if any trusted view says "power line,"
  flag it.

## A2.4 — Little labeled data in a new region: bootstrapping

Lots of unlabeled aerial imagery, few labels. Ladder of techniques, cheapest first:
- **Foundation models / transfer:** start from a self-supervised aerial/RGB backbone
  (DINOv2) — strong features with little fine-tuning data. **SAM** for promptable masks
  to massively speed up annotation (click → mask → human verifies).
- **Self-supervised pretraining** on your own unlabeled imagery (masked autoencoding /
  contrastive) so the backbone is in-domain before any labels.
- **Weak / free labels:** OpenStreetMap, cadastral parcels, building footprints, road
  networks, land-use rasters → noisy labels for buildings/roads/water you can pretrain
  on, then refine. NDVI from multispectral gives free vegetation masks.
- **Active learning:** label the points the model is *most uncertain or
  most-disagreeing-across-views* about (you already have entropy from A2.3) — maximizes
  label value per human-hour.
- **Synthetic data / sim:** render labeled scenes for rare classes (power lines!) where
  real labels are scarce; mind the sim-to-real gap (domain randomization).
- **Semi-supervised:** pseudo-labeling / consistency regularization (FixMatch-style) to
  exploit the unlabeled bulk.

**Sequence I'd propose:** SSL/foundation backbone → weak labels for common classes →
SAM-assisted human labeling on an active-learning-selected set → semi-supervised
fine-tuning → targeted synthetic for thin hazards.

## A2.5 — Domain shift to a new country

New vegetation, roof materials, building styles, road markings, climate/lighting → a
US-trained model silently degrades.

**Detect it (before it causes incidents):**
- **Input-distribution monitoring:** feature-space drift detection (e.g. distance of
  embeddings to the training distribution, energy/Mahalanobis OOD scores) flags imagery
  the model hasn't seen anything like.
- **Confidence/entropy monitoring:** rising prediction entropy or collapsing
  class distributions on the new region is an early warning.
- **Proxy metrics without labels:** multi-view label *inconsistency* (A2.3) and
  geometric-vs-semantic disagreement spike under domain shift.
- **Spot-check labeling:** truth a small stratified sample in the new region to *measure*
  the drop rather than guess.

**Adapt without full relabeling:**
- **Unsupervised domain adaptation** (adversarial feature alignment / self-training with
  pseudo-labels on the new domain).
- **SSL fine-tuning** on the new region's unlabeled imagery to re-align the backbone.
- **Active learning:** label only the highest-value new-domain examples.
- **Style/appearance normalization** (radiometric calibration, color/CycleGAN-style
  transfer) to reduce the gap before retraining.
- **Don't auto-ship to a new region until the per-hazard recall gate passes** on local
  validation — gate first, expand second.

## A2.6 — Modeling learned customer drop preferences

The question: where does *this customer* want the package, learned at scale, layered on
top of "where is it safe."

**Framing — a learned cost/utility surface over the yard, combined with the safety
surface:**
- **Inputs:** the geometric + semantic world model (where's the door, driveway, deck,
  shade), historical drop outcomes, explicit customer choices, and aggregate priors
  ("most people want it near the back door, on a hard surface, not on grass").
- **Best frame: ranking / learned scoring over candidate drop points** — produce a
  utility score per safe candidate and pick the argmax, rather than hard
  classification. Ranking handles "several acceptable spots, some preferred" naturally
  and degrades gracefully.
- **Cold start:** with no history for a new customer, fall back to a **population prior**
  (preferences learned across customers conditioned on yard features) and personalize
  as feedback arrives — a hierarchical/empirical-Bayes shrinkage from population →
  individual.
- **Safety dominates preference:** preference only *selects among* points the safety
  surface already deems deliverable. Never let a learned preference override a hazard
  gate. The final drop point = argmax(preference) subject to deliverability ≥ threshold.
- **Feedback loop:** delivery success + (where available) customer correction signals
  retrain the preference model — close the loop, the same theme as eval (B6).

---

# A3 — Cloud-side Pipeline / World Models

## A3.1 — Full offboard onboarding pipeline

Design the system that takes a new address from "signed up" to "safe to serve." Stages
(also summarized in
[Week 12 Part D](12-zipline-aerial-perception-interview.md#part-d--behavioral--system-design-framing)):

1. **Ingest** — pull satellite + schedule/collect an aerial survey; store raw imagery +
   metadata (camera pose, GSD, timestamp, sensor calibration) in immutable,
   content-addressed storage. Everything downstream is reproducible from this.
2. **Reconstruct** — SfM/MVS seeded with the pose prior → dense cloud → **DSM/DTM/nDSM**;
   compute slope/roughness layers. Cache the dense product keyed by (address,
   imagery-version).
3. **Segment** — tiled semantic segmentation → 2D masks → **fuse into the 3D model**
   with occlusion-tested multi-view fusion (A2.3) → semantic 3D + uncertainty layer.
4. **Score deliverability** — derive geometric+semantic features → **calibrated
   confidence** + recommended drop point(s) (A3.3, B4, C5).
5. **Validate** — automated gates (geometric consistency, per-hazard recall, calibration
   checks) + a **human-review queue** for low-confidence / high-entropy / high-change
   sites (A5).
6. **Publish** — emit a **versioned prior** (geometry + semantics + drop point +
   confidence + provenance) to the fleet-facing store; record the model/data versions
   that produced it.
7. **Operate + close the loop** — track staleness; field outcomes (success/abort/
   incident) flow back as labels and trigger re-validation/re-fly.

**Cross-cutting:** orchestration (a DAG per site), idempotent reproducible stages,
cost-per-site budget, observability, and rollback. Emphasize that each stage emits a
**versioned, debuggable artifact** because it's safety-critical.

## A3.2 — Onboard interface; precompute split; staleness

**What the onboard stack gets:** a compact, validated **prior**, not raw imagery —
georeferenced geometry (DTM/nDSM or a clearance map), a semantic/hazard layer, the
recommended drop point + a no-fly/keep-out mask, and a **confidence + freshness stamp**.

**Offboard vs onboard split:**
- **Offboard (expensive, slow-changing, global context):** dense reconstruction,
  large-model segmentation, deliverability scoring, change detection across surveys.
  You have unlimited compute and the full survey — do the heavy lifting here.
- **Onboard (real-time, live, local):** use the prior as a **strong prior to validate
  and refine against live sensors**, detect *discrepancies* (something new in the yard),
  and make the final safety call. The aircraft must handle the world having changed.

**The trust/override contract (the senior-signal part):** define exactly what happens
when the prior and live perception disagree. Live perception of a *hazard* should be
able to **abort** even if the prior said "safe" (fail-safe toward not delivering). The
prior raises confidence and handles what onboard can't see well, but it is not allowed
to override a live hazard detection.

**Staleness:** the world changes (tree grows, shed built, pool installed). Mitigations:
- **Freshness stamp + expiry** on every prior; force re-validation past an age/season.
- **Change-triggered refresh:** new satellite/aerial passes run change detection (A1.7);
  significant change in the drop corridor invalidates the prior and re-queues survey +
  re-scoring.
- **Onboard discrepancy feedback:** when aircraft repeatedly see the yard differ from
  the prior, flag it for re-survey — the fleet itself is a change sensor.

## A3.3 — Deliverability confidence: build + calibrate

Full deep-dive in
[Week 12 §B4](12-zipline-aerial-perception-interview.md#b4-deliverability-confidence--building-and-calibrating-it).
Hit these:
- **Features:** largest inscribed clearance radius (C5), min 3D clearance along the
  descent corridor, slope/roughness, canopy coverage, semantic hazards + distances,
  prior staleness, reconstruction uncertainty.
- **Model:** GBT or small MLP — interpretable and gate-able.
- **Calibration is the deliverable:** fit **isotonic regression**/Platt so a 0.9 score
  means ~90% truly safe; verify with a reliability diagram + ECE. Raw classifier scores
  are not probabilities.
- **Operating point under asymmetric cost:** choose `τ` to bound the **false-accept
  rate** (`P(hazard | predicted-safe) ≤ ε_safety`), not to max F1; everything below `τ`
  routes to human review / re-fly. Set `ε_safety` *with the safety team* — it's a
  product/safety decision, not a hyperparameter.

## A3.4 — Coordinate frames; ground point into aircraft frame

Full deep-dive in
[Week 12 §B5](12-zipline-aerial-perception-interview.md#b5-coordinate-frames--getting-a-ground-point-into-the-aircraft-frame).
The chain: `WGS84 → ECEF → ENU/UTM → body → camera`. The bug list to recite:
- **Datum/geoid mismatch** — GPS height is **ellipsoidal**, maps/DSMs often
  **orthometric (MSL)**; mixing them = tens of meters vertical error → fatal for
  clearance. Convert via the geoid model and *know which height your DSM uses*.
- **float32 ECEF** — magnitudes ~6.4e6 m quantize to ~0.5 m in float32; do the
  subtract-to-local-origin in **float64**, then drop to float32 in the small ENU frame.
- **UTM zone boundaries / lon-lat axis-order** swaps.
- **Rotation conventions** — active vs passive, `R` vs `Rᵀ`, quaternion order — state
  your convention before writing transform code.

---

# A4 — Production MLE / Systems

## A4.1 — When is SOTA worth productionizing vs robust classical?

This is the role's core judgment call ("not a research role"). My decision framework:

- **Start from the requirement, not the technique.** What accuracy/latency/cost does
  the *delivery decision* actually need? If classical MVS already meets the clearance
  accuracy budget, a fancier method is a liability, not an upgrade.
- **Weigh by reliability and failure-mode understanding, not novelty.** In a
  safety-critical system, a method whose failure modes you understand and can bound beats
  a higher-mean-accuracy method that fails unpredictably. Classical methods win on
  debuggability and predictability.
- **Total cost of ownership:** training cost, per-site inference cost at fleet scale,
  maintainability, reproducibility, and the eval/monitoring you'd have to build. SOTA
  often carries hidden operational tax.
- **Adopt SOTA when it clears a bar classical can't,** and only with: (a) a measured win
  on *your* validation incl. per-hazard slices, (b) bounded/understood failure modes,
  (c) an eval + rollback story. e.g. 3DGS only if it materially improves a metric you
  need *and* you've solved metric mesh extraction + validation.
- **De-risk with a pilot / shadow deployment:** run the new method in shadow against the
  incumbent on real traffic, compare on the gated metrics, then graduate. Never
  hot-swap the safety path.

Concrete framing: "I'd use the simplest method that meets the safety-validated bar, and
I'd let a SOTA method earn its way into production by beating that bar on held-out
hazard recall with understood failure modes — not because it's state of the art."

## A4.2 — Compute for hundreds of thousands of zones

Scaling reconstruction + segmentation across the whole customer base.

- **Batch vs streaming:** **batch** for the bulk (initial onboarding, periodic
  re-surveys) — embarrassingly parallel per site, schedule on spot/preemptible GPUs to
  cut cost. **Streaming/on-demand** for the latency-sensitive path (a new signup that
  needs to be served soon) on a smaller reserved pool. Two tiers, different SLAs.
- **Per-site as the unit of parallelism:** each address is an independent DAG → trivially
  horizontally scalable; orchestrate with a workflow engine; make stages idempotent and
  content-addressed so retries are free and dedup is automatic.
- **GPU scheduling:** separate the GPU-bound stages (segmentation, learned depth) from
  CPU-bound ones (classical MVS, rasterization, filtering); right-size instances per
  stage; bin-pack GPU jobs; autoscale on queue depth. Use mixed precision; batch tiles.
- **Cost per site is a tracked metric.** Know `$/site` and optimize it: cache dense
  products, skip re-reconstruction when imagery is unchanged, downsample where the
  decision tolerates it, reserve the expensive pipeline for sites that need it.
- **Incremental updates:** when new imagery lands, **only recompute the affected region/
  stage** (change-detection-gated), not the whole site from scratch — re-segment changed
  tiles, re-fuse, re-score. This is the difference between linear and quadratic ops cost
  over the fleet's lifetime.
- **Storage:** content-addressed artifact store with provenance; tiered (hot for active
  sites, cold for archives).

## A4.3 — Versioning model + data + priors for reproducibility & rollback

Safety-critical → you must reproduce and roll back any shipped prior.

- **Version everything that affects an output:** raw imagery (immutable,
  content-addressed), model weights, training dataset snapshot, the *code/config* of
  each pipeline stage, and the generated prior. Bind them with IDs.
- **Provenance / lineage on every prior:** the published prior carries the exact
  {imagery hash, model version, dataset version, pipeline commit} that produced it, so
  any field artifact is fully reproducible and auditable.
- **Reproducibility:** deterministic, idempotent stages keyed by input hashes →
  re-running the recorded versions reproduces the prior bit-for-bit (or within a
  documented tolerance).
- **Rollback:** priors are versioned and **immutable**; "rolling back" means
  re-publishing a known-good prior version to the fleet — fast, because you never
  mutate in place. A bad model release → revert the model pointer and re-publish
  previously validated priors.
- **Gated promotion:** new model/pipeline versions go through the validation gates (A5)
  in shadow before any prior they generate is allowed to ship. Tie it to the eval
  dashboards so promotion is a checklist, not a vibe.

---

# A5 — Evaluation & Validation (safety-critical)

## A5.1 — Building a validation set with no 3D ground truth

Full deep-dive in
[Week 12 §B6](12-zipline-aerial-perception-interview.md#b6-evaluation-when-there-is-no-3d-ground-truth).
The complementary signals:
- **Held-out views:** reconstruct from a subset, measure **reprojection / photometric
  consistency** on held-out frames — geometrically wrong models don't reproject cleanly.
- **LiDAR/RTK spot-checks:** truth a small, diverse sample → bound the population (DTM
  RMSE, canopy-height error, cloud-to-cloud distance); don't truth everything.
- **Self-consistency across independent surveys:** agreement where the world is
  unchanged; disagreement localizes change *or* error.
- **Synthetic/sim truth:** you own the geometry → unlimited labeled 3D for stress tests
  (thin structures, low texture).
- **Task-level proxy (the real metric):** field delivery success/abort/incident rates
  vs predicted deliverability — close the loop.

## A5.2 — Field-reliability metrics; FN/FP tradeoff; operating point

"Behaves reliably in the field" must be defined as **decision-level, safety-weighted**
metrics, not just IoU/RMSE:

- **Per-hazard recall** (did we catch every pool/line/person?) — the metric that maps to
  incidents. This is the headline.
- **False-accept rate** = `P(actually-hazard | we said deliver)` — the catastrophic
  error; bound it explicitly.
- **False-reject / coverage** = fraction of genuinely-good yards we refuse — the
  operational friction cost; minimize *subject to* the safety bound.
- **Calibration** (ECE / reliability diagram) — confidences must mean what they say
  because thresholds are set on them.

**The asymmetry:** a missed hazard (deliver into a pool/onto a person) is catastrophic
and possibly irreversible; a false hazard merely refuses a deliverable yard. So you do
**not** optimize F1 or accuracy. You **bound the false-accept rate at a
safety-team-set `ε_safety`** and then maximize coverage under that constraint. Set the
operating point on a precision/recall (or ROC) curve at the threshold meeting the bound;
everything riskier routes to human review or re-survey rather than auto-deliver. Make
explicit that `ε_safety` is owned by the safety case, not chosen to hit a launch metric.

## A5.3 — Regression where the mean improves but a rare class degrades

Aggregate IoU/accuracy is dominated by common classes (grass, roof) and can rise while
**power-line or pool recall falls** — a silent safety regression.

**Defenses:**
- **Sliced metrics with hard gates:** track each safety-critical class's recall
  *separately*; a release **cannot ship** if any hazard-class recall regresses beyond a
  tiny tolerance, regardless of mean metrics. Non-negotiable gate, not a soft target.
- **Fixed regression/golden set:** a curated, version-pinned set rich in rare hazards
  (continuously grown by hard-example mining from the field). Every candidate model runs
  it; compare per-class against the incumbent.
- **Per-class confusion + worst-case, not just averages:** report tail metrics (worst
  site, worst class) and trends, surfaced on a dashboard reviewers actually look at.
- **Stratified eval:** by region/season/yard-type so a gain in one stratum can't mask a
  loss in another.
- **Statistical care:** rare classes have few examples → use confidence intervals so you
  don't chase noise, but err toward *not shipping* on ambiguous hazard regressions.

## A5.4 — Power lines / thin structures specifically

Thin, low-texture, often sky-backed → MVS triangulates them poorly and segmentation
misses them, yet they're a top flight hazard. Treat them as a **dedicated sub-problem**:

**Reconstruction/detection:**
- **Don't rely on generic MVS.** Use **line/curve-specialized detectors** (catenary
  fitting — power lines hang in a known curve shape, a strong geometric prior) and
  dedicated thin-structure segmentation models trained with oversampled line pixels.
- **Multi-view line consensus:** detect lines per view and triangulate the *curves*
  across views; the catenary constraint regularizes the otherwise weak 3D estimate.
- **Fuse priors:** utility/infrastructure GIS data (where poles/lines are likely),
  multispectral cues, and known pole locations to bias detection.
- **Recall-biased fusion (A2.3):** any trusted view saying "line" flags it.

**Eval/guarantee:**
- **Separate per-hazard recall metric for lines** with a **hard ship gate** (A5.3) and a
  curated thin-structure regression set (real + synthetic, since real labels are scarce).
- **Synthetic stress tests:** render lines at varied thickness/contrast/background to
  measure the detection limit, then keep aircraft clear of that limit with a safety
  margin.
- **Conservative default:** in regions where line detection confidence is low, **inflate
  keep-out volumes / refuse low-altitude corridors** rather than assume clear. Fail safe.
- **Onboard backstop:** the prior flags likely line corridors; onboard perception +
  conservative geometry provide the last line of defense. Never single-point-of-failure
  a safety-critical hazard on one offboard model.

---

# A6 — Coding

All solved with runnable Python in
[Week 12 Part C](12-zipline-aerial-perception-interview.md#part-c--solved-coding-problems):
robust point-to-plane ICP (C1), normalized-DLT homography + RANSAC (C2), z-buffered
point-cloud projection (C3), DLT triangulation (C4), largest inscribed empty circle =
max clearance (C5), connected-component drop zones (C6). Practice articulating the
*complexity* and *failure modes* of each, not just the code.

---

## Final framing for the interview

Every answer above lands on the same three beats — say them explicitly:
1. **The technique** (show you know the standard method and its alternatives).
2. **The failure mode** (where it breaks, especially on aerial/satellite data).
3. **The safety consequence + operating point** (asymmetric cost; bound the
   false-accept; gate the rare hazards; fail safe; close the loop).

That third beat is what separates a senior/staff answer from a textbook recital and is
exactly what Zipline's safety-critical, ship-it-at-scale mandate is screening for.
