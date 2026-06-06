/* ============================================================
   Robotics & Perception Engineer — Interview Prep Curriculum
   8-week plan | Python + C++ | Intermediate
   Edit this file to add/remove topics. The tracker reads it directly.
   ============================================================ */

const CURRICULUM = [
  {
    week: 1,
    title: "Math Foundations",
    goal: "Rebuild the linear algebra, probability, and optimization muscles every perception algorithm leans on.",
    lecture: "study-materials/01-math-foundations.md",
    topics: [
      "Vectors, matrices, norms, dot/cross products",
      "Eigenvalues, eigenvectors, SVD (geometric meaning)",
      "Least squares (normal equations + SVD solution)",
      "Probability: Bayes rule, Gaussians, covariance",
      "Gradient descent, Gauss-Newton, Levenberg-Marquardt",
    ],
    leetcode: [
      { name: "Two Sum", url: "https://leetcode.com/problems/two-sum/", diff: "Easy", tag: "Arrays/Hash" },
      { name: "Maximum Subarray", url: "https://leetcode.com/problems/maximum-subarray/", diff: "Medium", tag: "DP/Kadane" },
      { name: "Product of Array Except Self", url: "https://leetcode.com/problems/product-of-array-except-self/", diff: "Medium", tag: "Arrays" },
    ],
    robotics: [
      { name: "Implement SVD-based least squares line fit", file: "coding-practice/robotics/w1_least_squares.py" },
      { name: "Covariance + Mahalanobis distance from scratch", file: "coding-practice/robotics/w1_covariance.py" },
    ],
  },
  {
    week: 2,
    title: "3D Geometry & Rigid-Body Transforms",
    goal: "Master rotations, quaternions, and SE(3) — the language of every robot pose.",
    lecture: "study-materials/02-3d-geometry-transforms.md",
    topics: [
      "Rotation matrices, properties of SO(3)",
      "Euler angles & gimbal lock",
      "Axis-angle and the exponential map",
      "Quaternions: composition, slerp, pitfalls",
      "Homogeneous coordinates & SE(3) transforms",
      "Frame conventions (body, world, camera, sensor)",
    ],
    leetcode: [
      { name: "Rotate Image", url: "https://leetcode.com/problems/rotate-image/", diff: "Medium", tag: "Matrix" },
      { name: "Spiral Matrix", url: "https://leetcode.com/problems/spiral-matrix/", diff: "Medium", tag: "Matrix" },
      { name: "Set Matrix Zeroes", url: "https://leetcode.com/problems/set-matrix-zeroes/", diff: "Medium", tag: "Matrix" },
    ],
    robotics: [
      { name: "Quaternion <-> rotation matrix <-> Euler converters", file: "coding-practice/robotics/w2_rotations.py" },
      { name: "Chain TF transforms to project a point world->camera", file: "coding-practice/robotics/w2_transform_chain.py" },
    ],
  },
  {
    week: 3,
    title: "Camera Models & Classical Image Processing",
    goal: "Understand how 3D becomes pixels, and the filtering/feature toolkit on top of it.",
    lecture: "study-materials/03-camera-models-image-processing.md",
    topics: [
      "Pinhole model, intrinsics K, extrinsics",
      "Lens distortion (radial/tangential) & undistortion",
      "Camera calibration (Zhang's method)",
      "Convolution, Gaussian/box blur, separable filters",
      "Image gradients, Sobel, Laplacian",
      "Image pyramids & scale space",
    ],
    leetcode: [
      { name: "Image Smoother", url: "https://leetcode.com/problems/image-smoother/", diff: "Easy", tag: "Matrix/Conv" },
      { name: "Number of Islands", url: "https://leetcode.com/problems/number-of-islands/", diff: "Medium", tag: "BFS/DFS/CC" },
      { name: "Pacific Atlantic Water Flow", url: "https://leetcode.com/problems/pacific-atlantic-water-flow/", diff: "Medium", tag: "Grid DFS" },
    ],
    robotics: [
      { name: "Implement 2D convolution + Sobel edges (NumPy)", file: "coding-practice/robotics/w3_convolution.py" },
      { name: "Project 3D points with K[R|t] and add distortion", file: "coding-practice/robotics/w3_projection.py" },
    ],
  },
  {
    week: 4,
    title: "Features & Multi-View Geometry",
    goal: "Detect, describe, and match features; recover geometry between views.",
    lecture: "study-materials/04-features-multiview-geometry.md",
    topics: [
      "Harris corners, FAST, blob detectors",
      "Descriptors: SIFT, ORB, BRIEF; matching + ratio test",
      "RANSAC for robust model fitting",
      "Epipolar geometry: fundamental & essential matrix",
      "Homography & the 8-point / 5-point algorithms",
      "Triangulation and PnP",
      "Bundle adjustment (reprojection error)",
    ],
    leetcode: [
      { name: "Max Points on a Line", url: "https://leetcode.com/problems/max-points-on-a-line/", diff: "Hard", tag: "Geometry" },
      { name: "K Closest Points to Origin", url: "https://leetcode.com/problems/k-closest-points-to-origin/", diff: "Medium", tag: "Heap" },
      { name: "Find K Closest Elements", url: "https://leetcode.com/problems/find-k-closest-elements/", diff: "Medium", tag: "Binary Search" },
    ],
    robotics: [
      { name: "RANSAC line/plane fitting from scratch", file: "coding-practice/robotics/w4_ransac.py" },
      { name: "Estimate homography + warp; 8-point fundamental matrix", file: "coding-practice/robotics/w4_homography_fmatrix.py" },
    ],
  },
  {
    week: 5,
    title: "State Estimation & Filtering",
    goal: "Fuse noisy sensors over time: Bayes filter, KF/EKF/UKF, particle filter.",
    lecture: "study-materials/05-state-estimation.md",
    topics: [
      "Recursive Bayes filter (predict/update)",
      "Kalman filter derivation & assumptions",
      "Extended KF: linearization, Jacobians",
      "Unscented KF: sigma points",
      "Particle filter / Monte Carlo localization",
      "Tuning Q, R; observability & consistency (NEES)",
    ],
    leetcode: [
      { name: "Moving Average from Data Stream", url: "https://leetcode.com/problems/moving-average-from-data-stream/", diff: "Easy", tag: "Stream" },
      { name: "Sliding Window Maximum", url: "https://leetcode.com/problems/sliding-window-maximum/", diff: "Hard", tag: "Deque" },
      { name: "Find Median from Data Stream", url: "https://leetcode.com/problems/find-median-from-data-stream/", diff: "Hard", tag: "Heaps" },
    ],
    robotics: [
      { name: "1D Kalman filter for constant-velocity tracking", file: "coding-practice/robotics/w5_kalman_1d.py" },
      { name: "2D EKF for range-bearing landmark localization", file: "coding-practice/robotics/w5_ekf_localization.py" },
    ],
  },
  {
    week: 6,
    title: "SLAM, Odometry & Sensor Fusion",
    goal: "Tie geometry + estimation together into mapping and localization systems.",
    lecture: "study-materials/06-slam-odometry.md",
    topics: [
      "SLAM problem: front-end vs back-end",
      "Visual odometry pipeline (feature & direct)",
      "Pose-graph optimization & loop closure",
      "Factor graphs (GTSAM/g2o mental model)",
      "LiDAR odometry & ICP (point-to-point/plane)",
      "Visual-inertial odometry (IMU preintegration idea)",
    ],
    leetcode: [
      { name: "Course Schedule", url: "https://leetcode.com/problems/course-schedule/", diff: "Medium", tag: "Graph/Topo" },
      { name: "Network Delay Time", url: "https://leetcode.com/problems/network-delay-time/", diff: "Medium", tag: "Dijkstra" },
      { name: "Graph Valid Tree", url: "https://leetcode.com/problems/graph-valid-tree/", diff: "Medium", tag: "Union-Find" },
    ],
    robotics: [
      { name: "2D ICP (point-to-point) aligning two scans", file: "coding-practice/robotics/w6_icp.py" },
      { name: "2D pose-graph optimization (Gauss-Newton)", file: "coding-practice/robotics/w6_pose_graph.py" },
    ],
  },
  {
    week: 7,
    title: "Deep Learning for Perception",
    goal: "Modern neural perception: detection, segmentation, 3D, and point clouds.",
    lecture: "study-materials/07-deep-learning-perception.md",
    topics: [
      "CNN building blocks; receptive field; BN/dropout",
      "Object detection (one-stage vs two-stage, anchors, NMS)",
      "Semantic & instance segmentation (U-Net, Mask R-CNN)",
      "3D detection & BEV; LiDAR nets (PointNet/voxel)",
      "Metrics: IoU, mAP, precision/recall curves",
      "Sensor fusion & calibration for learned models",
    ],
    leetcode: [
      { name: "Maximal Square", url: "https://leetcode.com/problems/maximal-square/", diff: "Medium", tag: "DP/Grid" },
      { name: "Word Ladder", url: "https://leetcode.com/problems/word-ladder/", diff: "Hard", tag: "BFS" },
      { name: "LRU Cache", url: "https://leetcode.com/problems/lru-cache/", diff: "Medium", tag: "Design" },
    ],
    robotics: [
      { name: "IoU + Non-Max Suppression from scratch", file: "coding-practice/robotics/w7_nms_iou.py" },
      { name: "mAP computation for object detection", file: "coding-practice/robotics/w7_map.py" },
    ],
  },
  {
    week: 8,
    title: "Systems, ROS & Mock Interviews",
    goal: "Wire it into real systems and rehearse the interview itself.",
    lecture: "study-materials/08-systems-ros-interview.md",
    topics: [
      "ROS/ROS2 concepts: nodes, topics, TF, time sync",
      "Real-time, latency, threading, memory in C++",
      "Coordinate frames & calibration in a full stack",
      "System design: 'design a perception pipeline for X'",
      "Behavioral stories (STAR) + project deep-dives",
      "2-3 timed mock interviews (coding + domain)",
    ],
    leetcode: [
      { name: "Merge Intervals", url: "https://leetcode.com/problems/merge-intervals/", diff: "Medium", tag: "Intervals" },
      { name: "Design Circular Queue", url: "https://leetcode.com/problems/design-circular-queue/", diff: "Medium", tag: "Ring buffer" },
      { name: "Time-Based Key-Value Store", url: "https://leetcode.com/problems/time-based-key-value-store/", diff: "Medium", tag: "Design" },
    ],
    robotics: [
      { name: "Ring buffer for time-synced sensor messages", file: "coding-practice/robotics/w8_ring_buffer.py" },
      { name: "Nearest-timestamp message synchronizer", file: "coding-practice/robotics/w8_time_sync.py" },
    ],
  },
];

if (typeof module !== "undefined") module.exports = CURRICULUM;
