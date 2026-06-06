/* AUTO-GENERATED from study-materials markdown by build_lectures.cjs.
   Edit the source there and rebuild, or edit this file directly. */
const LECTURES = {
  "1": {
    "title": "Week 1 — Math Foundations",
    "html": "<blockquote class=\"lec-callout\">The goal of week 1 is not to relearn all of math, but to make the handful of operations that show up <em>everywhere</em> in perception feel automatic: SVD, least squares, Gaussians, and iterative optimization.</blockquote>\n<hr>\n<h2 id=\"1-linear-algebra-you-actually-use\">1. Linear algebra you actually use</h2>\n<h3 id=\"vectors-matrices\">Vectors &amp; matrices</h3>\n<ul><li>A matrix is a <strong>linear map</strong>. <code>y = A x</code> sends vector <code>x</code> to <code>y</code>.</li><li><strong>Dot product</strong> <code>a·b = |a||b|cosθ</code> → projection, similarity, angle.</li><li><strong>Cross product</strong> <code>a×b</code> → a vector perpendicular to both; magnitude = area of parallelogram. In robotics it appears as the <strong>skew-symmetric matrix</strong> <code>[a]ₓ</code>:</li></ul>\n<pre class=\"lec-pre\"><code>        [  0  -a3   a2 ]\n[a]ₓ =  [  a3   0  -a1 ]      so that  a × b = [a]ₓ b\n        [ -a2  a1   0  ]</code></pre>\n<h3 id=\"eigen-decomposition\">Eigen-decomposition</h3>\n<ul><li><code>A v = λ v</code>: <code>v</code> is a direction unchanged by <code>A</code> (only scaled by <code>λ</code>).</li><li>For a <strong>symmetric</strong> matrix (e.g. a covariance), eigenvectors are orthogonal and eigenvalues are real → principal axes of an ellipsoid. This is the backbone of PCA and uncertainty visualization.</li></ul>\n<h3 id=\"singular-value-decomposition-svd-the-perception-workhorse\">Singular Value Decomposition (SVD) — <em>the</em> perception workhorse</h3>\n<pre class=\"lec-pre\"><code>A = U Σ Vᵀ          U, V orthogonal;  Σ diagonal ≥ 0 (singular values)</code></pre>\n<p>Why you keep meeting it:</p>\n<ul><li><strong>Solve homogeneous systems</strong> <code>A x = 0</code> (8-point algorithm, homography, triangulation): the solution is the right-singular vector of the <strong>smallest</strong> singular value (last column of <code>V</code>).</li><li><strong>Best rank-k approximation</strong> (Eckart–Young) → denoising, enforcing rank-2 on a fundamental matrix.</li><li><strong>Pseudo-inverse</strong> <code>A⁺ = V Σ⁺ Uᵀ</code> → least squares.</li><li><strong>Orthogonal Procrustes</strong>: best rotation aligning two point sets (used in ICP).</li></ul>\n<blockquote class=\"lec-callout\">Interview reflex: \"How do I solve <code>Ax = 0</code> with <code>x ≠ 0</code>?\" → SVD, take last column of <code>V</code>. \"How do I solve <code>Ax = b</code> overdetermined?\" → least squares.</blockquote>\n<hr>\n<h2 id=\"2-least-squares\">2. Least squares</h2>\n<p>Given <code>A x ≈ b</code> with more equations than unknowns, minimize <code>‖Ax − b‖²</code>.</p>\n<ul><li><strong>Normal equations:</strong> <code>x = (AᵀA)⁻¹ Aᵀ b</code>. Fast, but <code>AᵀA</code> squares the condition number → numerically worse.</li><li><strong>SVD / QR:</strong> more stable, preferred in practice.</li><li><strong>Weighted least squares:</strong> <code>min (Ax−b)ᵀ W (Ax−b)</code>; <code>W = Σ⁻¹</code> uses measurement covariance. This is exactly what filters and bundle adjustment do.</li></ul>\n<p><strong>Total least squares</strong> (errors in both <code>A</code> and <code>b</code>) → solved via SVD; this is how you fit a line/plane when <em>all</em> coordinates are noisy.</p>\n<hr>\n<h2 id=\"3-probability-for-estimation\">3. Probability for estimation</h2>\n<ul><li><strong>Bayes' rule:</strong> <code>p(x|z) ∝ p(z|x) p(x)</code> — posterior ∝ likelihood × prior. This is the entire conceptual basis of filtering and SLAM back-ends.</li><li><strong>Gaussian (normal) distribution:</strong> fully described by mean <code>μ</code> and covariance <code>Σ</code>. Closed under linear transforms and conditioning — <em>why</em> Kalman filters are Gaussian.<ul><li><code>x ~ N(μ, Σ)</code>, then <code>Ax+b ~ N(Aμ+b, AΣAᵀ)</code>.</li></ul></li><li><strong>Covariance matrix</strong> <code>Σ</code>: diagonal = variances, off-diagonal = correlation. Eigen-decomposition gives the uncertainty ellipse.</li><li><strong>Mahalanobis distance</strong> <code>d² = (x−μ)ᵀ Σ⁻¹ (x−μ)</code> — distance that accounts for correlation/scale. Used for gating/outlier rejection in data association.</li></ul>\n<hr>\n<h2 id=\"4-optimization-nonlinear-least-squares\">4. Optimization (nonlinear least squares)</h2>\n<p>Most perception \"solve\" steps minimize a sum of squared residuals <code>f(x) = Σ ‖rᵢ(x)‖²</code>.</p>\n<ul><li><strong>Gradient descent:</strong> <code>x ← x − α ∇f</code>. Simple, slow, needs step tuning.</li><li><strong>Gauss–Newton:</strong> linearize residuals <code>r(x+Δ) ≈ r + J Δ</code>, solve <code>JᵀJ Δ = −Jᵀ r</code>. Fast near the solution; can diverge far away.</li><li><strong>Levenberg–Marquardt:</strong> <code>(JᵀJ + λI) Δ = −Jᵀ r</code>. Interpolates between GN (λ→0) and gradient descent (λ→∞). The default for bundle adjustment / pose-graph.</li></ul>\n<blockquote class=\"lec-callout\">Know the GN normal equation cold — it's the same <code>JᵀJ Δ = −Jᵀ r</code> you'll write for EKF Jacobians, BA, ICP, and pose-graph optimization.</blockquote>\n<hr>\n<h2 id=\"interview-style-questions\">Interview-style questions</h2>\n<ol><li>When would you use the normal equations vs. SVD for least squares?</li><li>You have <code>Ax = 0</code>; how do you find a nontrivial <code>x</code>? Why the smallest singular value?</li><li>Why is the covariance matrix symmetric positive semi-definite? What do its eigenvectors mean?</li><li>Derive the Gauss–Newton update from a first-order Taylor expansion.</li><li>What's the geometric interpretation of Mahalanobis distance vs. Euclidean?</li></ol>\n<h2 id=\"resources\">Resources</h2>\n<ul><li><em>MIT 18.06</em> (Strang) lectures on SVD, least squares, eigenvalues.</li><li><em>Mathematics for Machine Learning</em> (Deisenroth) — Ch. 2–5, free PDF.</li><li>3Blue1Brown \"Essence of Linear Algebra\" for geometric intuition.</li></ul>\n<p>➡ <strong>Coding:</strong> <code>coding-practice/robotics/w1_least_squares.py</code>, <code>w1_covariance.py</code></p>",
    "toc": [
      {
        "level": 2,
        "txt": "1. Linear algebra you actually use",
        "id": "1-linear-algebra-you-actually-use"
      },
      {
        "level": 3,
        "txt": "Vectors & matrices",
        "id": "vectors-matrices"
      },
      {
        "level": 3,
        "txt": "Eigen-decomposition",
        "id": "eigen-decomposition"
      },
      {
        "level": 3,
        "txt": "Singular Value Decomposition (SVD) — *the* perception workhorse",
        "id": "singular-value-decomposition-svd-the-perception-workhorse"
      },
      {
        "level": 2,
        "txt": "2. Least squares",
        "id": "2-least-squares"
      },
      {
        "level": 2,
        "txt": "3. Probability for estimation",
        "id": "3-probability-for-estimation"
      },
      {
        "level": 2,
        "txt": "4. Optimization (nonlinear least squares)",
        "id": "4-optimization-nonlinear-least-squares"
      },
      {
        "level": 2,
        "txt": "Interview-style questions",
        "id": "interview-style-questions"
      },
      {
        "level": 2,
        "txt": "Resources",
        "id": "resources"
      }
    ]
  },
  "2": {
    "title": "Week 2 — 3D Geometry & Rigid-Body Transforms",
    "html": "<blockquote class=\"lec-callout\">Every robot question eventually becomes: <em>\"what frame is this in, and how do I get it into the frame I care about?\"</em> Master rotations and SE(3) and half of perception bookkeeping disappears.</blockquote>\n<hr>\n<h2 id=\"1-rotations-the-group-so-3\">1. Rotations — the group SO(3)</h2>\n<p>A rotation matrix <code>R</code> is 3×3 with:</p>\n<ul><li><code>RᵀR = I</code> (orthonormal columns), and</li><li><code>det(R) = +1</code> (right-handed, not a reflection).</li></ul>\n<p>It has <strong>3 degrees of freedom</strong> despite 9 entries (6 constraints). Columns of <code>R</code> are the axes of the rotated frame expressed in the original frame.</p>\n<h3 id=\"representations-trade-offs\">Representations &amp; trade-offs</h3>\n<div class=\"lec-table-wrap\"><table class=\"lec-table\"><thead><tr><th>Representation</th><th>DoF stored</th><th>Pros</th><th>Cons</th></tr></thead><tbody><tr><td>Rotation matrix</td><td>9</td><td>composes by matmul, no ambiguity</td><td>redundant, drifts off SO(3)</td></tr><tr><td>Euler angles (roll/pitch/yaw)</td><td>3</td><td>intuitive, minimal</td><td><strong>gimbal lock</strong>, order-dependent</td></tr><tr><td>Axis-angle (<code>θ·k̂</code>)</td><td>3</td><td>minimal, used in optimization</td><td>singular at θ=0 handling</td></tr><tr><td>Quaternion (<code>q = [w,x,y,z]</code>)</td><td>4</td><td>no gimbal lock, smooth slerp, cheap</td><td>unit-norm constraint, double cover (<code>q</code> ≡ <code>−q</code>)</td></tr></tbody></table></div>\n<p><strong>Gimbal lock:</strong> when two Euler axes align (e.g. pitch = 90°), you lose a DoF. This is why state estimators and IMUs use quaternions internally.</p>\n<hr>\n<h2 id=\"2-the-exponential-map-axis-angle-matrix\">2. The exponential map (axis-angle ↔ matrix)</h2>\n<p>Rotation by angle <code>θ</code> about unit axis <code>k̂</code> (Rodrigues' formula):</p>\n<pre class=\"lec-pre\"><code>R = I + sinθ [k̂]ₓ + (1 − cosθ) [k̂]ₓ²</code></pre>\n<ul><li><code>exp: so(3) → SO(3)</code> turns a 3-vector <code>ω = θk̂</code> (the <strong>Lie algebra</strong>) into a rotation matrix.</li><li><code>log: SO(3) → so(3)</code> goes back. These let you do calculus on rotations — the basis for optimizing over poses (you perturb in the tangent space <code>Δ ∈ ℝ³</code>).</li></ul>\n<blockquote class=\"lec-callout\">Interview gold: <em>\"How do you optimize over rotations without breaking orthonormality?\"</em> → parameterize updates in the tangent space (Lie algebra) and apply via the exponential map: <code>R ← R · exp([Δ]ₓ)</code>.</blockquote>\n<hr>\n<h2 id=\"3-quaternions-in-practice\">3. Quaternions in practice</h2>\n<ul><li>Unit quaternion <code>q = w + xi + yj + zk</code>, <code>‖q‖ = 1</code>.</li><li><strong>Composition</strong> of rotations = quaternion multiplication (Hamilton product).</li><li><strong>Rotate a vector:</strong> <code>v' = q v q⁻¹</code>.</li><li><strong>SLERP</strong> = constant-angular-velocity interpolation between orientations (smooth camera paths, IMU integration).</li><li>Pitfalls: normalize after updates; pick a hemisphere (<code>q</code> vs <code>−q</code>) for continuity; watch Hamilton vs JPL convention (ROS uses Hamilton, <code>[x,y,z,w]</code> ordering in messages!).</li></ul>\n<hr>\n<h2 id=\"4-rigid-body-transforms-se-3\">4. Rigid-body transforms — SE(3)</h2>\n<p>A pose = rotation + translation, stored as a 4×4 <strong>homogeneous</strong> matrix:</p>\n<pre class=\"lec-pre\"><code>       [ R   t ]          point:  X̃ = [X Y Z 1]ᵀ\nT  =   [ 0   1 ]          transform:  X̃' = T X̃</code></pre>\n<ul><li><strong>Compose</strong> by matmul: <code>T_world_cam = T_world_body · T_body_cam</code>.</li><li><strong>Invert:</strong> <code>T⁻¹ = [Rᵀ  −Rᵀt; 0 1]</code>.</li><li>Read the subscripts as a chain — <code>T_A_B</code> maps points <em>from frame B into frame A</em>. Adjacent subscripts must \"cancel\": <code>T_A_B · T_B_C = T_A_C</code>.</li></ul>\n<blockquote class=\"lec-callout\">Frame-naming discipline (<code>T_target_source</code>) eliminates an entire class of sign and ordering bugs. Use it religiously.</blockquote>\n<hr>\n<h2 id=\"5-common-frames-in-a-robot\">5. Common frames in a robot</h2>\n<ul><li><strong>World / map</strong> — fixed global frame.</li><li><strong>Body / base_link</strong> — robot center.</li><li><strong>Sensor frames</strong> — camera, LiDAR, IMU, each with an extrinsic <code>T_body_sensor</code> found by <strong>calibration</strong>.</li><li><strong>Camera optical frame</strong> — z-forward, x-right, y-down (REP-103 differs from the robot's x-forward body frame — a classic gotcha).</li></ul>\n<p><img class=\"lec-img\" src=\"study-materials/images/pinhole-camera.svg\" alt=\"SE(3) transform chain\" loading=\"lazy\"> <em>(Camera projection ties directly into next week — a point goes world → camera via <code>T_cam_world</code>, then camera → pixels via <code>K</code>.)</em></p>\n<hr>\n<h2 id=\"interview-style-questions\">Interview-style questions</h2>\n<ol><li>Why do quaternions avoid gimbal lock when Euler angles don't?</li><li>How would you optimize a camera pose over SO(3)/SE(3) while staying on the manifold?</li><li>Given <code>T_world_cam</code> and a point in world coordinates, write the transform to camera coordinates.</li><li>What's the inverse of a homogeneous transform — derive it, don't just invert 4×4.</li><li>ROS gives a quaternion as <code>[x,y,z,w]</code>; another lib expects <code>[w,x,y,z]</code>. What breaks and how do you catch it?</li></ol>\n<h2 id=\"resources\">Resources</h2>\n<ul><li><em>Modern Robotics</em> (Lynch &amp; Park), Ch. 3 — rotations, SE(3), screws. Free PDF + Coursera.</li><li><em>State Estimation for Robotics</em> (Barfoot), Ch. 6–7 — Lie groups for estimation.</li><li>Quaternion visualizer: eater.net/quaternions.</li></ul>\n<p>➡ <strong>Coding:</strong> <code>coding-practice/robotics/w2_rotations.py</code>, <code>w2_transform_chain.py</code></p>",
    "toc": [
      {
        "level": 2,
        "txt": "1. Rotations — the group SO(3)",
        "id": "1-rotations-the-group-so-3"
      },
      {
        "level": 3,
        "txt": "Representations & trade-offs",
        "id": "representations-trade-offs"
      },
      {
        "level": 2,
        "txt": "2. The exponential map (axis-angle ↔ matrix)",
        "id": "2-the-exponential-map-axis-angle-matrix"
      },
      {
        "level": 2,
        "txt": "3. Quaternions in practice",
        "id": "3-quaternions-in-practice"
      },
      {
        "level": 2,
        "txt": "4. Rigid-body transforms — SE(3)",
        "id": "4-rigid-body-transforms-se-3"
      },
      {
        "level": 2,
        "txt": "5. Common frames in a robot",
        "id": "5-common-frames-in-a-robot"
      },
      {
        "level": 2,
        "txt": "Interview-style questions",
        "id": "interview-style-questions"
      },
      {
        "level": 2,
        "txt": "Resources",
        "id": "resources"
      }
    ]
  },
  "3": {
    "title": "Week 3 — Camera Models & Classical Image Processing",
    "html": "<blockquote class=\"lec-callout\">How does a 3D world become a 2D array of pixels — and what can we recover from that array with filters before any learning is involved?</blockquote>\n<hr>\n<h2 id=\"1-the-pinhole-camera-model\">1. The pinhole camera model</h2>\n<p><img class=\"lec-img\" src=\"study-materials/images/pinhole-camera.svg\" alt=\"Pinhole camera model\" loading=\"lazy\"></p>\n<p>A 3D point <code>X_cam = (X, Y, Z)</code> in the camera frame projects to pixel <code>(u, v)</code>:</p>\n<pre class=\"lec-pre\"><code>u = fx · X/Z + cx\nv = fy · Y/Z + cy</code></pre>\n<p>In matrix form with homogeneous coordinates:</p>\n<pre class=\"lec-pre\"><code>        [ fx  0  cx ]\ns·x =   [ 0   fy cy ] · [R | t] · X_world      x = [u v 1]ᵀ\n        [ 0   0   1 ]\n        \\____ K ____/</code></pre>\n<ul><li><strong>K (intrinsics):</strong> focal lengths <code>fx, fy</code> (pixels), principal point <code>cx, cy</code>, optional skew. Properties of the camera + lens.</li><li><strong>[R | t] (extrinsics):</strong> where the camera is in the world (= <code>T_cam_world</code>).</li><li>The <code>1/Z</code> divide is the <strong>projective</strong> part — depth is lost; this is why a single image is ambiguous up to scale.</li></ul>\n<hr>\n<h2 id=\"2-lens-distortion\">2. Lens distortion</h2>\n<p>Real lenses bend rays. The standard (Brown–Conrady) model:</p>\n<ul><li><strong>Radial:</strong> <code>x_d = x(1 + k1 r² + k2 r⁴ + k3 r⁶)</code> — barrel/pincushion.</li><li><strong>Tangential:</strong> <code>p1, p2</code> terms from lens/sensor misalignment.</li></ul>\n<p>You <strong>undistort</strong> before doing geometry (or work in normalized coordinates). For wide-FOV/fisheye lenses use the fisheye (equidistant) model instead.</p>\n<hr>\n<h2 id=\"3-camera-calibration-zhang-s-method\">3. Camera calibration (Zhang's method)</h2>\n<p>Show the camera a planar checkerboard at several orientations:</p>\n<ol><li>Detect corners (known board geometry → known 3D, measured 2D).</li><li>Each view gives a homography board→image.</li><li>Solve linearly for <code>K</code>, then per-view <code>[R|t]</code>.</li><li>Refine everything + distortion by minimizing <strong>reprojection error</strong> (nonlinear least squares — your Week 1 Gauss–Newton/LM).</li></ol>\n<blockquote class=\"lec-callout\">Reprojection error (px) is the universal sanity metric: project known 3D points with your estimated params and measure pixel distance to detections. &lt; ~0.5 px is typically a good calibration.</blockquote>\n<hr>\n<h2 id=\"4-image-processing-fundamentals\">4. Image processing fundamentals</h2>\n<h3 id=\"convolution\">Convolution</h3>\n<p><img class=\"lec-img\" src=\"study-materials/images/convolution.svg\" alt=\"2D convolution\" loading=\"lazy\"></p>\n<pre class=\"lec-pre\"><code>out(i,j) = Σ_{m,n} kernel(m,n) · img(i+m, j+n)</code></pre>\n<ul><li><strong>Box / Gaussian blur</strong> — smoothing, noise reduction. Gaussian is <strong>separable</strong> (<code>G_2D = g_x · g_yᵀ</code>) → do two 1D passes, <code>O(2k)</code> instead of <code>O(k²)</code>.</li><li><strong>Padding &amp; borders</strong> matter (zero / reflect / replicate).</li></ul>\n<h3 id=\"gradients-edges\">Gradients &amp; edges</h3>\n<ul><li><strong>Sobel</strong> approximates <code>∂I/∂x</code>, <code>∂I/∂y</code>. Gradient magnitude <code>|∇I| = √(Gx²+Gy²)</code> and direction <code>atan2(Gy, Gx)</code>.</li><li><strong>Laplacian</strong> = second derivative → zero-crossings at edges (blob/edge detection).</li><li><strong>Canny</strong> = gradient + non-max suppression + hysteresis thresholding → clean thin edges.</li></ul>\n<h3 id=\"scale-space-pyramids\">Scale space &amp; pyramids</h3>\n<ul><li>Repeatedly blur + downsample → <strong>image pyramid</strong>. Lets detectors find features at multiple scales and enables coarse-to-fine matching/optical flow.</li><li><strong>Difference of Gaussians (DoG)</strong> approximates the scale-normalized Laplacian → basis of SIFT keypoint detection (next week).</li></ul>\n<h3 id=\"histograms-thresholding\">Histograms &amp; thresholding</h3>\n<ul><li>Histogram equalization for contrast; Otsu's method for automatic binary threshold.</li></ul>\n<hr>\n<h2 id=\"5-color-the-basics-you-ll-be-asked\">5. Color &amp; the basics you'll be asked</h2>\n<ul><li>RGB vs. grayscale vs. HSV (hue is robust to lighting for color segmentation).</li><li>Bayer pattern / demosaicing (raw sensor → RGB).</li><li>Image coordinates: <code>(row, col)</code> vs <code>(x=u, y=v)</code> — mixing them up is the #1 bug.</li></ul>\n<hr>\n<h2 id=\"interview-style-questions\">Interview-style questions</h2>\n<ol><li>Walk through projecting a 3D world point to a pixel, naming every matrix.</li><li>Why is a Gaussian blur separable and why does that matter for performance?</li><li>How does checkerboard calibration recover intrinsics? What's reprojection error?</li><li>Implement 2D convolution; what's the time complexity and how do you speed it up?</li><li>You see straight lines bowing outward at image edges — what's wrong and how do you fix it?</li><li>Difference between <code>fx</code> in pixels vs. focal length in mm?</li></ol>\n<h2 id=\"resources\">Resources</h2>\n<ul><li>Szeliski, <em>Computer Vision: Algorithms and Applications</em> — Ch. 2 (image formation), Ch. 3 (image processing). Free PDF.</li><li>First Principles of Computer Vision (Shree Nayar) YouTube series.</li><li>OpenCV calibration tutorial.</li></ul>\n<p>➡ <strong>Coding:</strong> <code>coding-practice/robotics/w3_convolution.py</code>, <code>w3_projection.py</code></p>",
    "toc": [
      {
        "level": 2,
        "txt": "1. The pinhole camera model",
        "id": "1-the-pinhole-camera-model"
      },
      {
        "level": 2,
        "txt": "2. Lens distortion",
        "id": "2-lens-distortion"
      },
      {
        "level": 2,
        "txt": "3. Camera calibration (Zhang's method)",
        "id": "3-camera-calibration-zhang-s-method"
      },
      {
        "level": 2,
        "txt": "4. Image processing fundamentals",
        "id": "4-image-processing-fundamentals"
      },
      {
        "level": 3,
        "txt": "Convolution",
        "id": "convolution"
      },
      {
        "level": 3,
        "txt": "Gradients & edges",
        "id": "gradients-edges"
      },
      {
        "level": 3,
        "txt": "Scale space & pyramids",
        "id": "scale-space-pyramids"
      },
      {
        "level": 3,
        "txt": "Histograms & thresholding",
        "id": "histograms-thresholding"
      },
      {
        "level": 2,
        "txt": "5. Color & the basics you'll be asked",
        "id": "5-color-the-basics-you-ll-be-asked"
      },
      {
        "level": 2,
        "txt": "Interview-style questions",
        "id": "interview-style-questions"
      },
      {
        "level": 2,
        "txt": "Resources",
        "id": "resources"
      }
    ]
  },
  "4": {
    "title": "Week 4 — Features & Multi-View Geometry",
    "html": "<blockquote class=\"lec-callout\">This is the heart of classical perception: find repeatable points, match them across images, and use the matches to recover camera motion and 3D structure.</blockquote>\n<hr>\n<h2 id=\"1-feature-detection\">1. Feature detection</h2>\n<p>A good keypoint is <strong>repeatable</strong> (found again under viewpoint/lighting change) and <strong>localizable</strong> (well-defined position).</p>\n<ul><li><strong>Harris corner:</strong> looks at the second-moment matrix <code>M = Σ ∇I ∇Iᵀ</code> over a window. Two large eigenvalues → corner; one → edge; none → flat. Response <code>R = det(M) − k·tr(M)²</code>.</li><li><strong>FAST:</strong> checks a ring of 16 pixels around a candidate — fast enough for real-time SLAM front-ends.</li><li><strong>Blob detectors (DoG / LoG):</strong> find scale + location → SIFT keypoints.</li></ul>\n<h2 id=\"2-feature-description-matching\">2. Feature description &amp; matching</h2>\n<ul><li><strong>SIFT:</strong> 128-D histogram-of-gradients descriptor; scale &amp; rotation invariant. Gold standard for accuracy (now patent-free).</li><li><strong>ORB:</strong> FAST + rotated BRIEF, binary descriptor; matched with <strong>Hamming distance</strong>. Fast, the default in ORB-SLAM.</li><li><strong>Matching:</strong> nearest neighbor in descriptor space; apply <strong>Lowe's ratio test</strong> (<code>d1 / d2 &amp;lt; 0.7..0.8</code>) to reject ambiguous matches; cross-check; then geometric verification with RANSAC.</li></ul>\n<h2 id=\"3-ransac-robust-fitting\">3. RANSAC — robust fitting</h2>\n<p>Matches contain outliers; least squares alone gets wrecked by them.</p>\n<pre class=\"lec-pre\"><code>repeat N times:\n    sample the minimal set (e.g. 4 pts for homography, 8 for F)\n    fit the model\n    count inliers (residual &lt; threshold)\nkeep the model with the most inliers; refit on all inliers</code></pre>\n<ul><li>Choose <code>N</code> from desired success prob <code>p</code> and inlier ratio <code>w</code>: <code>N = log(1−p) / log(1 − wˢ)</code>.</li><li>Variants: MSAC, PROSAC, LO-RANSAC.</li></ul>\n<blockquote class=\"lec-callout\">RANSAC shows up far beyond CV — plane fitting in point clouds, line fitting, any model-with-outliers situation. Know the loop and the <code>N</code> formula.</blockquote>\n<h2 id=\"4-epipolar-geometry-two-views\">4. Epipolar geometry (two views)</h2>\n<p><img class=\"lec-img\" src=\"study-materials/images/epipolar-geometry.svg\" alt=\"Epipolar geometry\" loading=\"lazy\"></p>\n<p>A 3D point seen in two cameras gives corresponding pixels <code>x ↔ x'</code>. They satisfy:</p>\n<pre class=\"lec-pre\"><code>x'ᵀ F x = 0          (fundamental matrix, uncalibrated, pixels)\nx'ᵀ E x = 0          (essential matrix, calibrated/normalized rays)\nE = K'ᵀ F K           E = [t]ₓ R</code></pre>\n<ul><li>A point in image 1 constrains its match in image 2 to lie on a line (the <strong>epipolar line</strong>) → reduces matching from 2D to 1D search.</li><li><strong>8-point algorithm</strong> estimates <code>F</code> linearly (SVD), with Hartley normalization; enforce rank-2 by zeroing the smallest singular value.</li><li><strong>5-point algorithm</strong> estimates <code>E</code> from calibrated cameras (minimal → great with RANSAC).</li><li>Decompose <code>E = [t]ₓR</code> → 4 solutions for <code>(R, t)</code>; pick the one with points in front of both cameras (cheirality). Translation is recovered <strong>up to scale</strong>.</li></ul>\n<h2 id=\"5-homography-planar-pure-rotation\">5. Homography (planar / pure rotation)</h2>\n<p><code>x' = H x</code> (3×3) relates two views of a <strong>plane</strong> or images under <strong>pure camera rotation</strong>. Uses: image stitching/panoramas, AR marker pose, ground-plane warps (bird's-eye view). Estimated from ≥4 correspondences (DLT + SVD).</p>\n<blockquote class=\"lec-callout\">Decision: planar scene or pure rotation → homography; general 3D scene with translation → fundamental/essential matrix.</blockquote>\n<h2 id=\"6-triangulation-pnp\">6. Triangulation &amp; PnP</h2>\n<ul><li><strong>Triangulation:</strong> given <code>x ↔ x'</code> and known camera matrices, recover the 3D point (linear DLT via SVD, then nonlinear refine of reprojection error).</li><li><strong>PnP (Perspective-n-Point):</strong> given known 3D points and their 2D projections, find the camera pose <code>(R, t)</code>. P3P (minimal, 3 pts) + RANSAC + nonlinear refine. This is how you <strong>relocalize</strong> against a known map.</li></ul>\n<h2 id=\"7-bundle-adjustment\">7. Bundle adjustment</h2>\n<p>The grand nonlinear least squares that jointly refines <strong>all camera poses and 3D points</strong> by minimizing total reprojection error:</p>\n<pre class=\"lec-pre\"><code>min Σ_i Σ_j ρ( ‖ x_ij − π(K, T_i, X_j) ‖² )</code></pre>\n<ul><li>Solved with LM; exploits <strong>sparsity</strong> (Schur complement) because each point sees few cameras. <code>ρ</code> is a robust (Huber) kernel to tame outliers.</li><li>The back-end of essentially every SfM / visual SLAM system.</li></ul>\n<hr>\n<h2 id=\"interview-style-questions\">Interview-style questions</h2>\n<ol><li>Harris vs. SIFT vs. ORB — when would you pick each?</li><li>What does <code>x'ᵀ F x = 0</code> mean geometrically? Why rank-2?</li><li>Why is monocular translation only recoverable up to scale? How do you fix the scale?</li><li>Homography vs. fundamental matrix — what scene geometry distinguishes them?</li><li>Derive how many RANSAC iterations you need for 50% inliers, 4-point model, 99% success.</li><li>What makes bundle adjustment tractable for thousands of points?</li></ol>\n<h2 id=\"resources\">Resources</h2>\n<ul><li>Hartley &amp; Zisserman, <em>Multiple View Geometry</em> — the bible (Ch. 9–11, 18).</li><li>Szeliski Ch. 7–8, 11.</li><li>Cyrill Stachniss \"Photogrammetry\" YouTube lectures (excellent, intuitive).</li></ul>\n<p>➡ <strong>Coding:</strong> <code>coding-practice/robotics/w4_ransac.py</code>, <code>w4_homography_fmatrix.py</code></p>",
    "toc": [
      {
        "level": 2,
        "txt": "1. Feature detection",
        "id": "1-feature-detection"
      },
      {
        "level": 2,
        "txt": "2. Feature description & matching",
        "id": "2-feature-description-matching"
      },
      {
        "level": 2,
        "txt": "3. RANSAC — robust fitting",
        "id": "3-ransac-robust-fitting"
      },
      {
        "level": 2,
        "txt": "4. Epipolar geometry (two views)",
        "id": "4-epipolar-geometry-two-views"
      },
      {
        "level": 2,
        "txt": "5. Homography (planar / pure rotation)",
        "id": "5-homography-planar-pure-rotation"
      },
      {
        "level": 2,
        "txt": "6. Triangulation & PnP",
        "id": "6-triangulation-pnp"
      },
      {
        "level": 2,
        "txt": "7. Bundle adjustment",
        "id": "7-bundle-adjustment"
      },
      {
        "level": 2,
        "txt": "Interview-style questions",
        "id": "interview-style-questions"
      },
      {
        "level": 2,
        "txt": "Resources",
        "id": "resources"
      }
    ]
  },
  "5": {
    "title": "Week 5 — State Estimation & Filtering",
    "html": "<blockquote class=\"lec-callout\">Sensors are noisy and arrive over time. Filtering fuses a motion model with measurements to maintain a best estimate <strong>and its uncertainty</strong>.</blockquote>\n<hr>\n<h2 id=\"1-the-recursive-bayes-filter\">1. The recursive Bayes filter</h2>\n<p>Everything below is a special case of:</p>\n<pre class=\"lec-pre\"><code>predict:  bel⁻(xₜ) = ∫ p(xₜ | xₜ₋₁, uₜ) bel(xₜ₋₁) dxₜ₋₁\nupdate:   bel(xₜ)  ∝ p(zₜ | xₜ) · bel⁻(xₜ)</code></pre>\n<ul><li><strong>Predict</strong> pushes belief through the <strong>motion model</strong> (uncertainty grows).</li><li><strong>Update</strong> multiplies in the <strong>measurement likelihood</strong> (uncertainty shrinks).</li><li>Different assumptions on these distributions → KF, EKF, UKF, particle filter.</li></ul>\n<hr>\n<h2 id=\"2-kalman-filter-linear-gaussian\">2. Kalman Filter (linear, Gaussian)</h2>\n<p><img class=\"lec-img\" src=\"study-materials/images/kalman-loop.svg\" alt=\"Kalman predict/update loop\" loading=\"lazy\"></p>\n<p>Assumes linear motion/measurement and Gaussian noise. State <code>x ~ N(x̂, P)</code>.</p>\n<pre class=\"lec-pre\"><code>Predict:   x̂⁻ = F x̂ + B u\n           P⁻  = F P Fᵀ + Q\nUpdate:    K   = P⁻ Hᵀ (H P⁻ Hᵀ + R)⁻¹      (Kalman gain)\n           x̂   = x̂⁻ + K (z − H x̂⁻)            (innovation = z − H x̂⁻)\n           P   = (I − K H) P⁻</code></pre>\n<ul><li><code>F</code> motion, <code>H</code> measurement, <code>Q</code> process noise, <code>R</code> measurement noise.</li><li><strong>Kalman gain</strong> <code>K</code> interpolates between prediction and measurement based on relative confidence: noisy sensor (<code>R</code> large) → trust prediction, and vice versa.</li><li>It is the <strong>optimal</strong> estimator under the linear-Gaussian assumptions.</li></ul>\n<blockquote class=\"lec-callout\">The whole filter is \"weighted average of prediction and measurement, weighted by their covariances.\" If you can say that, you understand it.</blockquote>\n<hr>\n<h2 id=\"3-extended-kalman-filter-ekf\">3. Extended Kalman Filter (EKF)</h2>\n<p>Real motion/measurement models are nonlinear. EKF <strong>linearizes</strong> them with Jacobians at the current estimate:</p>\n<pre class=\"lec-pre\"><code>x̂⁻ = f(x̂, u)                 F = ∂f/∂x |x̂\nz_pred = h(x̂⁻)               H = ∂h/∂x |x̂⁻\n(then same gain/update equations as KF, using F and H)</code></pre>\n<ul><li>Pros: cheap, ubiquitous (robot localization, VIO, GPS/IMU fusion).</li><li>Cons: linearization error → can diverge if highly nonlinear or poorly initialized; Jacobians are error-prone to derive.</li></ul>\n<h2 id=\"4-unscented-kalman-filter-ukf\">4. Unscented Kalman Filter (UKF)</h2>\n<p>Instead of linearizing, propagate a deterministic set of <strong>sigma points</strong> through the nonlinear function and recompute mean/covariance.</p>\n<ul><li>More accurate than EKF for strong nonlinearity, no Jacobians needed.</li><li>Slightly more compute; same Gaussian assumption.</li></ul>\n<h2 id=\"5-particle-filter-monte-carlo\">5. Particle Filter (Monte Carlo)</h2>\n<p>Represent the belief by <strong>weighted samples</strong> — handles non-Gaussian, multimodal beliefs (e.g. the \"kidnapped robot\" / global localization).</p>\n<pre class=\"lec-pre\"><code>for each particle: propagate via motion model (+noise)\nweight by measurement likelihood p(z|x)\nresample proportional to weight  (deal with particle depletion)</code></pre>\n<ul><li>Used in <strong>Monte Carlo Localization (AMCL)</strong> on known maps.</li><li>Cost grows with state dimension (curse of dimensionality) → great in 2D/3D pose, not for high-D states.</li></ul>\n<hr>\n<h2 id=\"6-making-filters-actually-work\">6. Making filters actually work</h2>\n<ul><li><strong>Tuning <code>Q</code> and <code>R</code>:</strong> too-small <code>R</code> → overconfident, ignores good sensor; too small <code>Q</code> → filter \"locks up\" and lags reality. Start from sensor datasheets.</li><li><strong>Innovation gating:</strong> reject measurements whose Mahalanobis distance is too large (outlier/false association).</li><li><strong>Consistency:</strong> check <strong>NEES/NIS</strong> — is the actual error consistent with the reported covariance? An \"optimistic\" filter (P too small) is dangerous.</li><li><strong>Observability:</strong> is the state even recoverable from the measurements? (e.g. monocular VIO scale needs motion/excitation).</li></ul>\n<hr>\n<h2 id=\"interview-style-questions\">Interview-style questions</h2>\n<ol><li>Derive the Kalman gain — what is it trading off?</li><li>EKF vs. UKF vs. particle filter: when does each break down?</li><li>What is the innovation, and how do you use it to reject outliers?</li><li>Your EKF diverges. List the things you'd check.</li><li>Why can't a particle filter scale to a 12-D state?</li><li>What does it mean for a filter to be \"inconsistent / overconfident\"?</li></ol>\n<h2 id=\"resources\">Resources</h2>\n<ul><li>Thrun, Burgard, Fox, <em>Probabilistic Robotics</em> — Ch. 2–4, 7–8 (the canonical text).</li><li>Roger Labbe, <em>Kalman and Bayesian Filters in Python</em> — free, interactive notebooks.</li><li>Cyrill Stachniss filtering lectures (YouTube).</li></ul>\n<p>➡ <strong>Coding:</strong> <code>coding-practice/robotics/w5_kalman_1d.py</code>, <code>w5_ekf_localization.py</code></p>",
    "toc": [
      {
        "level": 2,
        "txt": "1. The recursive Bayes filter",
        "id": "1-the-recursive-bayes-filter"
      },
      {
        "level": 2,
        "txt": "2. Kalman Filter (linear, Gaussian)",
        "id": "2-kalman-filter-linear-gaussian"
      },
      {
        "level": 2,
        "txt": "3. Extended Kalman Filter (EKF)",
        "id": "3-extended-kalman-filter-ekf"
      },
      {
        "level": 2,
        "txt": "4. Unscented Kalman Filter (UKF)",
        "id": "4-unscented-kalman-filter-ukf"
      },
      {
        "level": 2,
        "txt": "5. Particle Filter (Monte Carlo)",
        "id": "5-particle-filter-monte-carlo"
      },
      {
        "level": 2,
        "txt": "6. Making filters actually work",
        "id": "6-making-filters-actually-work"
      },
      {
        "level": 2,
        "txt": "Interview-style questions",
        "id": "interview-style-questions"
      },
      {
        "level": 2,
        "txt": "Resources",
        "id": "resources"
      }
    ]
  },
  "6": {
    "title": "Week 6 — SLAM, Odometry & Sensor Fusion",
    "html": "<blockquote class=\"lec-callout\">SLAM = <strong>S</strong>imultaneous <strong>L</strong>ocalization <strong>a</strong>nd <strong>M</strong>apping: build a map of an unknown environment while tracking your pose within it. It ties together geometry (Week 4) and estimation (Week 5).</blockquote>\n<hr>\n<h2 id=\"1-the-slam-problem-architecture\">1. The SLAM problem &amp; architecture</h2>\n<p>A modern SLAM system splits into:</p>\n<ul><li><strong>Front-end</strong> (data processing): feature extraction/tracking, data association, short-term motion estimation (odometry), loop-closure <em>detection</em>.</li><li><strong>Back-end</strong> (optimization): refine poses + map by minimizing error over a graph; apply loop closures.</li></ul>\n<p>The full posterior <code>p(x_{0:t}, m | z, u)</code> is intractable; we solve a MAP estimate via nonlinear least squares (a graph), not a filter, in most modern systems.</p>\n<hr>\n<h2 id=\"2-visual-odometry-vo\">2. Visual odometry (VO)</h2>\n<p>Estimate camera motion frame-to-frame:</p>\n<p><strong>Feature-based pipeline</strong></p>\n<ol><li>Detect + match features (ORB/SIFT) between frames.</li><li>Estimate relative pose: essential matrix (mono) or PnP (with known 3D / RGB-D).</li><li>Triangulate new points; track them.</li><li>Local <strong>bundle adjustment</strong> over a sliding window of keyframes.</li></ol>\n<p><strong>Direct methods</strong> (DSO, LSD-SLAM): skip features, minimize <strong>photometric error</strong> directly over pixel intensities. Better in low-texture, sensitive to brightness changes/calibration.</p>\n<ul><li>Mono VO has <strong>scale drift / unknown scale</strong>; stereo and RGB-D give metric scale.</li><li>VO is <em>odometry</em> (drifts over time); SLAM adds loop closure to correct drift.</li></ul>\n<hr>\n<h2 id=\"3-pose-graph-optimization-loop-closure\">3. Pose-graph optimization &amp; loop closure</h2>\n<p><img class=\"lec-img\" src=\"study-materials/images/slam-posegraph.svg\" alt=\"SLAM pose graph\" loading=\"lazy\"></p>\n<ul><li><strong>Nodes</strong> = poses (and/or landmarks). <strong>Edges</strong> = constraints (odometry between consecutive poses; loop closures between revisited places).</li><li>Each edge contributes a residual <code>‖ẑᵢⱼ ⊖ h(xᵢ, xⱼ)‖²_Σ</code>; minimize the sum with Gauss–Newton/LM (your Week 1 math, on the SE(3) manifold from Week 2).</li><li><strong>Loop closure</strong>: recognize a previously seen place (e.g. <strong>bag-of-words</strong> / DBoW2, or learned place recognition) → add an edge that snaps accumulated drift back into alignment.</li></ul>\n<p><strong>Factor graphs</strong> (g2o, GTSAM, Ceres) are the standard tooling — variables (poses/landmarks) connected by factors (measurements). They exploit sparsity for efficiency.</p>\n<hr>\n<h2 id=\"4-lidar-odometry-registration-icp\">4. LiDAR odometry &amp; registration (ICP)</h2>\n<p><strong>Iterative Closest Point</strong> aligns two point clouds:</p>\n<pre class=\"lec-pre\"><code>repeat:\n    for each point in source, find nearest point in target (kd-tree)\n    estimate R, t minimizing Σ ‖ R pᵢ + t − qᵢ ‖²   (closed form via SVD)\n    apply transform; check convergence</code></pre>\n<ul><li><strong>Point-to-point</strong> vs <strong>point-to-plane</strong> (uses surface normals → faster, more accurate on structured scenes).</li><li>Sensitive to initialization and outliers → use good init (IMU/odometry), reject far correspondences, downsample (voxel grid).</li><li>Real LiDAR SLAM: LOAM / LeGO-LOAM / LIO-SAM extract edge &amp; planar features and fuse IMU.</li></ul>\n<hr>\n<h2 id=\"5-visual-inertial-odometry-vio\">5. Visual-Inertial Odometry (VIO)</h2>\n<p>Fuse camera + IMU — complementary sensors:</p>\n<ul><li>IMU: high-rate, great short-term, but <strong>drifts</strong> (double-integrated bias/noise).</li><li>Camera: accurate but low-rate and scale-ambiguous (mono).</li><li>Together: metric scale, robustness to motion blur / fast motion, gravity gives roll/pitch observability.</li></ul>\n<p><strong>IMU preintegration</strong> summarizes many IMU samples between keyframes into a single relative-motion factor (so you don't re-integrate when the linearization point changes) — the key trick behind VINS-Mono, OKVIS, ORB-SLAM3.</p>\n<ul><li>Filter-based VIO (MSCKF) vs optimization-based (VINS-Mono): EKF efficiency vs smoother accuracy.</li></ul>\n<hr>\n<h2 id=\"6-fusion-patterns-gotchas\">6. Fusion patterns &amp; gotchas</h2>\n<ul><li><strong>Loosely vs tightly coupled</strong> fusion: combine independent pose estimates vs. jointly optimize raw measurements (tighter = more accurate, more complex).</li><li><strong>Time synchronization</strong> across sensors is critical (hardware trigger / PTP / TF timestamps). Bad sync looks like bad calibration.</li><li><strong>Extrinsic calibration</strong> between sensors must be known/estimated.</li></ul>\n<hr>\n<h2 id=\"interview-style-questions\">Interview-style questions</h2>\n<ol><li>Filter-based vs. optimization-based SLAM — trade-offs?</li><li>Why does monocular VO drift in scale and how do stereo/IMU/RGB-D fix it?</li><li>Walk through ICP. How do you make it robust and fast?</li><li>What is loop closure and why does it matter? How do you detect one?</li><li>Why preintegrate IMU measurements?</li><li>What's a factor graph and why is it the right structure for SLAM?</li></ol>\n<h2 id=\"resources\">Resources</h2>\n<ul><li>Cadena et al., <em>\"Past, Present, and Future of SLAM\"</em> (survey) — read once, twice.</li><li>Cyrill Stachniss SLAM course (YouTube) — graph SLAM, ICP, factor graphs.</li><li>ORB-SLAM3, VINS-Mono papers; GTSAM/Ceres tutorials.</li></ul>\n<p>➡ <strong>Coding:</strong> <code>coding-practice/robotics/w6_icp.py</code>, <code>w6_pose_graph.py</code></p>",
    "toc": [
      {
        "level": 2,
        "txt": "1. The SLAM problem & architecture",
        "id": "1-the-slam-problem-architecture"
      },
      {
        "level": 2,
        "txt": "2. Visual odometry (VO)",
        "id": "2-visual-odometry-vo"
      },
      {
        "level": 2,
        "txt": "3. Pose-graph optimization & loop closure",
        "id": "3-pose-graph-optimization-loop-closure"
      },
      {
        "level": 2,
        "txt": "4. LiDAR odometry & registration (ICP)",
        "id": "4-lidar-odometry-registration-icp"
      },
      {
        "level": 2,
        "txt": "5. Visual-Inertial Odometry (VIO)",
        "id": "5-visual-inertial-odometry-vio"
      },
      {
        "level": 2,
        "txt": "6. Fusion patterns & gotchas",
        "id": "6-fusion-patterns-gotchas"
      },
      {
        "level": 2,
        "txt": "Interview-style questions",
        "id": "interview-style-questions"
      },
      {
        "level": 2,
        "txt": "Resources",
        "id": "resources"
      }
    ]
  },
  "7": {
    "title": "Week 7 — Deep Learning for Perception",
    "html": "<blockquote class=\"lec-callout\">Classical geometry tells you <em>where</em>; learned models increasingly tell you <em>what</em>. Modern perception stacks combine both. Know the building blocks, the task formulations, and the metrics.</blockquote>\n<hr>\n<h2 id=\"1-cnn-building-blocks\">1. CNN building blocks</h2>\n<ul><li><strong>Convolution layer:</strong> learnable filters; weight sharing + locality → far fewer params than dense layers, translation equivariance.</li><li><strong>Receptive field:</strong> the input region one output neuron \"sees\" — grows with depth, stride, dilation. Must cover the object you want to detect.</li><li><strong>Pooling / strided conv:</strong> downsample, build invariance, enlarge receptive field.</li><li><strong>Batch norm:</strong> normalizes activations → faster, more stable training.</li><li><strong>Residual connections (ResNet):</strong> skip connections let very deep nets train (mitigate vanishing gradients).</li><li><strong>Activation:</strong> ReLU and variants.</li></ul>\n<blockquote class=\"lec-callout\">Be ready to compute output size: <code>out = (W − K + 2P)/S + 1</code>, and to reason about receptive field and parameter count.</blockquote>\n<hr>\n<h2 id=\"2-object-detection\">2. Object detection</h2>\n<p>Goal: bounding boxes + class labels.</p>\n<ul><li><strong>Two-stage (Faster R-CNN):</strong> region proposals → classify + refine. Accurate, slower.</li><li><strong>One-stage (YOLO, SSD, RetinaNet):</strong> predict boxes directly on a grid. Fast, real-time; RetinaNet's <strong>focal loss</strong> addresses foreground/background imbalance.</li><li><strong>Anchors:</strong> predefined box priors; modern <strong>anchor-free</strong> detectors (FCOS, CenterNet) and <strong>DETR</strong> (transformer, set prediction) drop them.</li><li><strong>Non-Max Suppression (NMS):</strong> remove duplicate overlapping boxes, keep the highest-confidence one per object (you'll implement this).</li></ul>\n<h2 id=\"3-segmentation\">3. Segmentation</h2>\n<ul><li><strong>Semantic segmentation:</strong> per-pixel class (no instances). <strong>U-Net</strong> / DeepLab (encoder–decoder, dilated convs, skip connections).</li><li><strong>Instance segmentation:</strong> per-object masks. <strong>Mask R-CNN</strong> = Faster R-CNN + mask head.</li><li><strong>Panoptic:</strong> unifies semantic (stuff) + instance (things).</li></ul>\n<h2 id=\"4-3d-perception\">4. 3D perception</h2>\n<ul><li><strong>LiDAR point clouds</strong> are unordered, sparse, irregular:<ul><li><strong>PointNet / PointNet++:</strong> operate directly on points with permutation-invariant pooling.</li><li><strong>Voxel/grid methods (VoxelNet, SECOND, PointPillars):</strong> voxelize → 3D/2D conv; PointPillars is the real-time favorite.</li></ul></li><li><strong>BEV (bird's-eye-view):</strong> project to top-down grid — natural for driving, fuses well across sensors.</li><li><strong>3D object detection</strong> outputs oriented 3D boxes (x,y,z,w,l,h,yaw).</li><li><strong>Depth estimation:</strong> monocular (learned) or stereo (cost-volume nets).</li></ul>\n<h2 id=\"5-sensor-fusion-with-learned-models\">5. Sensor fusion with learned models</h2>\n<ul><li><strong>Early / mid / late fusion</strong> of camera + LiDAR + radar.</li><li>Camera gives semantics/texture; LiDAR gives accurate geometry → fuse for robust 3D detection (e.g. project image features into BEV).</li><li>Requires accurate <strong>calibration + time sync</strong> (same themes as classical).</li><li>Transformer-based BEV fusion (BEVFormer, BEVFusion) is the current direction.</li></ul>\n<h2 id=\"6-metrics-know-these-cold\">6. Metrics — <em>know these cold</em></h2>\n<ul><li><strong>IoU</strong> (Intersection over Union): <code>area(∩) / area(∪)</code> — the matching criterion.</li><li><strong>Precision / Recall:</strong> <code>P = TP/(TP+FP)</code>, <code>R = TP/(TP+FN)</code>.</li><li><strong>AP / mAP:</strong> area under precision–recall curve, averaged over classes (and IoU thresholds, e.g. COCO mAP@[.5:.95]).</li><li><strong>Confusion matrix, F1</strong>, per-class IoU (mIoU) for segmentation.</li></ul>\n<h2 id=\"7-training-deployment-realities\">7. Training &amp; deployment realities</h2>\n<ul><li>Data augmentation, class imbalance, label noise, domain gap (sim→real).</li><li>Loss design: classification (cross-entropy/focal) + localization (L1/smooth-L1/ GIoU).</li><li>Deployment: quantization (INT8), pruning, TensorRT/ONNX, latency vs accuracy budgets on embedded GPUs. Robotics cares a lot about <strong>real-time</strong> inference.</li></ul>\n<hr>\n<h2 id=\"interview-style-questions\">Interview-style questions</h2>\n<ol><li>What is a receptive field and how do you enlarge it without losing resolution?</li><li>Implement IoU and NMS. What's the complexity of NMS?</li><li>One-stage vs. two-stage detectors — trade-offs?</li><li>How does PointNet handle the unordered nature of point clouds?</li><li>Define mAP precisely — how is the PR curve built?</li><li>How would you fuse a camera and a LiDAR for 3D detection? What can go wrong?</li><li>A model is accurate offline but too slow on the robot — what are your options?</li></ol>\n<h2 id=\"resources\">Resources</h2>\n<ul><li>Stanford <strong>CS231n</strong> (CNNs for visual recognition) — notes + lectures.</li><li>Papers: ResNet, Faster R-CNN, YOLO, U-Net, Mask R-CNN, PointNet, PointPillars, DETR.</li><li><em>Dive into Deep Learning</em> (d2l.ai) for hands-on.</li></ul>\n<p>➡ <strong>Coding:</strong> <code>coding-practice/robotics/w7_nms_iou.py</code>, <code>w7_map.py</code></p>",
    "toc": [
      {
        "level": 2,
        "txt": "1. CNN building blocks",
        "id": "1-cnn-building-blocks"
      },
      {
        "level": 2,
        "txt": "2. Object detection",
        "id": "2-object-detection"
      },
      {
        "level": 2,
        "txt": "3. Segmentation",
        "id": "3-segmentation"
      },
      {
        "level": 2,
        "txt": "4. 3D perception",
        "id": "4-3d-perception"
      },
      {
        "level": 2,
        "txt": "5. Sensor fusion with learned models",
        "id": "5-sensor-fusion-with-learned-models"
      },
      {
        "level": 2,
        "txt": "6. Metrics — *know these cold*",
        "id": "6-metrics-know-these-cold"
      },
      {
        "level": 2,
        "txt": "7. Training & deployment realities",
        "id": "7-training-deployment-realities"
      },
      {
        "level": 2,
        "txt": "Interview-style questions",
        "id": "interview-style-questions"
      },
      {
        "level": 2,
        "txt": "Resources",
        "id": "resources"
      }
    ]
  },
  "8": {
    "title": "Week 8 — Systems, ROS & Interview Prep",
    "html": "<blockquote class=\"lec-callout\">Algorithms are necessary but not sufficient. Robotics roles test whether you can build a <em>system</em>: real-time, multi-sensor, debuggable. This week wires it all together and rehearses the interview.</blockquote>\n<hr>\n<h2 id=\"1-ros-ros2-essentials\">1. ROS / ROS2 essentials</h2>\n<ul><li><strong>Nodes</strong> (processes), <strong>topics</strong> (pub/sub streams), <strong>services</strong> (request/reply), <strong>actions</strong> (long-running goals), <strong>parameters</strong>.</li><li><strong>Messages</strong>: typed; sensor_msgs (Image, PointCloud2, Imu), geometry_msgs (Pose, Transform), nav_msgs (Odometry).</li><li><strong>TF / tf2:</strong> the transform tree — keeps every frame's relationship over time so you can ask \"where was the LiDAR in the map frame at timestamp t?\" Learn <code>lookup_transform</code>, static vs dynamic transforms.</li><li><strong>Time &amp; sync:</strong> <code>message_filters</code> ApproximateTime/ExactTime to align multi-sensor messages; use sensor timestamps, not wall clock.</li><li><strong>ROS2 specifics:</strong> DDS middleware, QoS profiles (reliability/durability), lifecycle nodes, executors. Better for real-time/multi-robot than ROS1.</li><li><strong>Tooling:</strong> <code>rosbag</code> (record/replay — your best debugging friend), <code>rviz</code> (visualize), <code>rqt_graph</code>, <code>ros2 topic echo/hz</code>.</li></ul>\n<hr>\n<h2 id=\"2-real-time-c-systems-concerns\">2. Real-time &amp; C++ systems concerns</h2>\n<ul><li><strong>Latency &amp; throughput:</strong> perception runs in a pipeline; identify the bottleneck, budget per stage, measure (don't guess).</li><li><strong>Memory:</strong> avoid allocations in the hot loop; preallocate; pools/ring buffers; zero-copy where possible.</li><li><strong>Concurrency:</strong> threads for capture vs processing; lock-free / bounded queues; beware priority inversion. Understand data races and how to avoid them.</li><li><strong>C++ for robotics:</strong> RAII, <code>std::move</code>, smart pointers, <code>const</code> correctness, Eigen (fixed-size types, alignment), avoiding undefined behavior. PCL for point clouds, OpenCV for images.</li><li><strong>Determinism:</strong> real-time systems care about <em>worst-case</em>, not average.</li></ul>\n<hr>\n<h2 id=\"3-calibration-coordinate-frames-in-a-full-stack\">3. Calibration &amp; coordinate frames in a full stack</h2>\n<ul><li><strong>Intrinsic</strong> (per camera) + <strong>extrinsic</strong> (sensor-to-sensor / sensor-to-body).</li><li>Camera–LiDAR, camera–IMU (Kalibr), wheel odometry — each has a calibration procedure and failure mode.</li><li>A surprising fraction of \"perception bugs\" are actually frame/timestamp/ calibration bugs. Always verify the transform tree first.</li></ul>\n<hr>\n<h2 id=\"4-system-design-questions\">4. System design questions</h2>\n<p>Expect open-ended prompts like <em>\"Design the perception system for a delivery robot / warehouse AMR / L2 driving feature.\"</em> Structure your answer:</p>\n<ol><li><strong>Clarify</strong>: requirements, sensors available, compute budget, latency, safety, environment (indoor/outdoor, dynamic?).</li><li><strong>Sensors &amp; why</strong>: camera vs LiDAR vs radar vs ultrasonic; redundancy.</li><li><strong>Pipeline</strong>: capture → sync → calibration → detection/segmentation → tracking → localization/mapping → output to planning.</li><li><strong>Estimation/fusion</strong>: filter or factor graph; how sensors fuse.</li><li><strong>Failure handling</strong>: sensor dropout, degraded conditions (rain, low light), confidence/uncertainty, fallbacks, safety monitor.</li><li><strong>Eval &amp; metrics</strong>: how you measure success; logging; data pipeline for improvement.</li><li><strong>Compute/deployment</strong>: on-board vs offload, real-time budget.</li></ol>\n<blockquote class=\"lec-callout\">Show you think about edge cases, uncertainty, and safety — that's what separates a robotics engineer from someone who only knows the algorithms.</blockquote>\n<hr>\n<h2 id=\"5-behavioral-project-deep-dives\">5. Behavioral &amp; project deep-dives</h2>\n<ul><li>Prepare 3–4 <strong>STAR</strong> stories (Situation, Task, Action, Result): a hard debugging win, a design trade-off you made, a failure you learned from, cross-team work.</li><li>Be able to <strong>whiteboard your past projects' architecture</strong> end to end and defend every design choice (\"why EKF not factor graph?\", \"why this sensor?\").</li><li>Tie answers to measurable impact (latency cut, accuracy gained, drift reduced).</li></ul>\n<hr>\n<h2 id=\"6-mock-interview-plan-do-these-timed\">6. Mock interview plan (do these timed)</h2>\n<ul><li>[ ] <strong>Mock 1 — Coding:</strong> 2 LeetCode mediums in 45 min, talk aloud.</li><li>[ ] <strong>Mock 2 — Domain:</strong> geometry + estimation rapid-fire (use the interview-style questions in each lecture file).</li><li>[ ] <strong>Mock 3 — System design:</strong> 45-min \"design a perception pipeline for X\".</li><li>[ ] Record yourself or pair with a peer; review where you got stuck.</li></ul>\n<hr>\n<h2 id=\"final-week-checklist\">Final-week checklist</h2>\n<ul><li>[ ] Can derive: pinhole projection, Kalman gain, Gauss–Newton, epipolar constraint.</li><li>[ ] Can implement from scratch: convolution, RANSAC, IoU+NMS, 1D Kalman, ICP step.</li><li>[ ] Can whiteboard: a full VIO/SLAM pipeline and a learned 3D detection stack.</li><li>[ ] Frames/timestamps/calibration debugging story ready.</li><li>[ ] 3–4 STAR stories rehearsed.</li></ul>\n<h2 id=\"resources\">Resources</h2>\n<ul><li>ROS2 docs + \"ROS2 in 5 days\" tutorials.</li><li><em>Programming Robots with ROS</em> (O'Reilly).</li><li>\"Grokking the System Design Interview\" for structure (adapt to robotics).</li><li>Reread the survey papers and your own project notes.</li></ul>\n<p>➡ <strong>Coding:</strong> <code>coding-practice/robotics/w8_ring_buffer.py</code>, <code>w8_time_sync.py</code></p>",
    "toc": [
      {
        "level": 2,
        "txt": "1. ROS / ROS2 essentials",
        "id": "1-ros-ros2-essentials"
      },
      {
        "level": 2,
        "txt": "2. Real-time & C++ systems concerns",
        "id": "2-real-time-c-systems-concerns"
      },
      {
        "level": 2,
        "txt": "3. Calibration & coordinate frames in a full stack",
        "id": "3-calibration-coordinate-frames-in-a-full-stack"
      },
      {
        "level": 2,
        "txt": "4. System design questions",
        "id": "4-system-design-questions"
      },
      {
        "level": 2,
        "txt": "5. Behavioral & project deep-dives",
        "id": "5-behavioral-project-deep-dives"
      },
      {
        "level": 2,
        "txt": "6. Mock interview plan (do these timed)",
        "id": "6-mock-interview-plan-do-these-timed"
      },
      {
        "level": 2,
        "txt": "Final-week checklist",
        "id": "final-week-checklist"
      },
      {
        "level": 2,
        "txt": "Resources",
        "id": "resources"
      }
    ]
  }
};
