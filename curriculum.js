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
    lecture: "lecture.html?week=1",
    topics: [
      "Vectors, matrices, norms, dot/cross products",
      "Eigenvalues, eigenvectors, SVD (geometric meaning)",
      "Least squares (normal equations + SVD solution)",
      "Probability: Bayes rule, Gaussians, covariance",
      "Gradient descent, Gauss-Newton, Levenberg-Marquardt",
    ],
    leetcode: [
      { name: "Two Sum", pid: "two-sum", url: "https://leetcode.com/problems/two-sum/", diff: "Easy", tag: "Arrays/Hash" },
      { name: "Maximum Subarray", pid: "maximum-subarray", url: "https://leetcode.com/problems/maximum-subarray/", diff: "Medium", tag: "DP/Kadane" },
      { name: "Product of Array Except Self", pid: "product-except-self", url: "https://leetcode.com/problems/product-of-array-except-self/", diff: "Medium", tag: "Arrays" },
    ],
    robotics: [
      { name: "Least-Squares Line Fit", pid: "rob-least-squares-line", diff: "Easy", tag: "Linear Algebra", file: "coding-practice/robotics/w1_least_squares.py" },
      { name: "Covariance & Mahalanobis Distance", pid: "rob-covariance-mahalanobis", diff: "Medium", tag: "Probability", file: "coding-practice/robotics/w1_covariance.py" },
    ],
  },
  {
    week: 2,
    title: "3D Geometry & Rigid-Body Transforms",
    goal: "Master rotations, quaternions, and SE(3) — the language of every robot pose.",
    lecture: "lecture.html?week=2",
    topics: [
      "Rotation matrices, properties of SO(3)",
      "Euler angles & gimbal lock",
      "Axis-angle and the exponential map",
      "Quaternions: composition, slerp, pitfalls",
      "Homogeneous coordinates & SE(3) transforms",
      "Frame conventions (body, world, camera, sensor)",
    ],
    leetcode: [
      { name: "Rotate Image", pid: "rotate-image", url: "https://leetcode.com/problems/rotate-image/", diff: "Medium", tag: "Matrix" },
      { name: "Spiral Matrix", pid: "spiral-matrix", url: "https://leetcode.com/problems/spiral-matrix/", diff: "Medium", tag: "Matrix" },
      { name: "Set Matrix Zeroes", pid: "set-matrix-zeroes", url: "https://leetcode.com/problems/set-matrix-zeroes/", diff: "Medium", tag: "Matrix" },
    ],
    robotics: [
      { name: "Rotate a Vector by a Quaternion", pid: "rob-quaternion-rotate", diff: "Easy", tag: "3D Geometry", file: "coding-practice/robotics/w2_rotations.py" },
      { name: "Compose SE(3) and Transform a Point", pid: "rob-transform-point", diff: "Medium", tag: "3D Geometry", file: "coding-practice/robotics/w2_transform_chain.py" },
    ],
  },
  {
    week: 3,
    title: "Camera Models & Classical Image Processing",
    goal: "Understand how 3D becomes pixels, and the filtering/feature toolkit on top of it.",
    lecture: "lecture.html?week=3",
    topics: [
      "Pinhole model, intrinsics K, extrinsics",
      "Lens distortion (radial/tangential) & undistortion",
      "Camera calibration (Zhang's method)",
      "Convolution, Gaussian/box blur, separable filters",
      "Image gradients, Sobel, Laplacian",
      "Image pyramids & scale space",
    ],
    leetcode: [
      { name: "Image Smoother", pid: "image-smoother", url: "https://leetcode.com/problems/image-smoother/", diff: "Easy", tag: "Matrix/Conv" },
      { name: "Number of Islands", pid: "number-of-islands", url: "https://leetcode.com/problems/number-of-islands/", diff: "Medium", tag: "BFS/DFS/CC" },
      { name: "Pacific Atlantic Water Flow", pid: "pacific-atlantic", url: "https://leetcode.com/problems/pacific-atlantic-water-flow/", diff: "Medium", tag: "Grid DFS" },
    ],
    robotics: [
      { name: "2D Cross-Correlation", pid: "rob-convolution-2d", diff: "Easy", tag: "Image Processing", file: "coding-practice/robotics/w3_convolution.py" },
      { name: "Project a 3D Point to a Pixel", pid: "rob-project-point", diff: "Easy", tag: "Camera Model", file: "coding-practice/robotics/w3_projection.py" },
    ],
  },
  {
    week: 4,
    title: "Features & Multi-View Geometry",
    goal: "Detect, describe, and match features; recover geometry between views.",
    lecture: "lecture.html?week=4",
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
      { name: "Max Points on a Line", pid: "max-points-on-a-line", url: "https://leetcode.com/problems/max-points-on-a-line/", diff: "Hard", tag: "Geometry" },
      { name: "K Closest Points to Origin", pid: "k-closest-points", url: "https://leetcode.com/problems/k-closest-points-to-origin/", diff: "Medium", tag: "Heap" },
      { name: "Find K Closest Elements", pid: "find-k-closest-elements", url: "https://leetcode.com/problems/find-k-closest-elements/", diff: "Medium", tag: "Binary Search" },
    ],
    robotics: [
      { name: "RANSAC Line — Max Inliers", pid: "rob-ransac-line-inliers", diff: "Medium", tag: "Robust Fitting", file: "coding-practice/robotics/w4_ransac.py" },
      { name: "2D Rigid Point-Set Alignment (Kabsch)", pid: "rob-rigid-align-2d", diff: "Medium", tag: "Registration", file: "coding-practice/robotics/w4_homography_fmatrix.py" },
    ],
  },
  {
    week: 5,
    title: "State Estimation & Filtering",
    goal: "Fuse noisy sensors over time: Bayes filter, KF/EKF/UKF, particle filter.",
    lecture: "lecture.html?week=5",
    topics: [
      "Recursive Bayes filter (predict/update)",
      "Kalman filter derivation & assumptions",
      "Extended KF: linearization, Jacobians",
      "Unscented KF: sigma points",
      "Particle filter / Monte Carlo localization",
      "Tuning Q, R; observability & consistency (NEES)",
    ],
    leetcode: [
      { name: "Moving Average from Data Stream", pid: "moving-average", url: "https://leetcode.com/problems/moving-average-from-data-stream/", diff: "Easy", tag: "Stream" },
      { name: "Sliding Window Maximum", pid: "sliding-window-maximum", url: "https://leetcode.com/problems/sliding-window-maximum/", diff: "Hard", tag: "Deque" },
      { name: "Find Median from Data Stream", pid: "find-median-from-data-stream", url: "https://leetcode.com/problems/find-median-from-data-stream/", diff: "Hard", tag: "Heaps" },
    ],
    robotics: [
      { name: "1D Kalman Filter (scalar)", pid: "rob-kalman-1d", diff: "Medium", tag: "State Estimation", file: "coding-practice/robotics/w5_kalman_1d.py" },
      { name: "Inverse-Variance Sensor Fusion", pid: "rob-measurement-fusion", diff: "Easy", tag: "Sensor Fusion" },
    ],
  },
  {
    week: 6,
    title: "SLAM, Odometry & Sensor Fusion",
    goal: "Tie geometry + estimation together into mapping and localization systems.",
    lecture: "lecture.html?week=6",
    topics: [
      "SLAM problem: front-end vs back-end",
      "Visual odometry pipeline (feature & direct)",
      "Pose-graph optimization & loop closure",
      "Factor graphs (GTSAM/g2o mental model)",
      "LiDAR odometry & ICP (point-to-point/plane)",
      "Visual-inertial odometry (IMU preintegration idea)",
    ],
    leetcode: [
      { name: "Course Schedule", pid: "course-schedule", url: "https://leetcode.com/problems/course-schedule/", diff: "Medium", tag: "Graph/Topo" },
      { name: "Network Delay Time", pid: "network-delay-time", url: "https://leetcode.com/problems/network-delay-time/", diff: "Medium", tag: "Dijkstra" },
      { name: "Graph Valid Tree", pid: "graph-valid-tree", url: "https://leetcode.com/problems/graph-valid-tree/", diff: "Medium", tag: "Union-Find" },
    ],
    robotics: [
      { name: "ICP — One Iteration (2D)", pid: "rob-icp-2d-step", diff: "Hard", tag: "SLAM / Registration", file: "coding-practice/robotics/w6_icp.py" },
      { name: "1D Pose-Graph Optimization", pid: "rob-pose-graph-1d", diff: "Hard", tag: "SLAM / Optimization", file: "coding-practice/robotics/w6_pose_graph.py" },
    ],
  },
  {
    week: 7,
    title: "Deep Learning for Perception",
    goal: "Modern neural perception: detection, segmentation, 3D, and point clouds.",
    lecture: "lecture.html?week=7",
    topics: [
      "CNN building blocks; receptive field; BN/dropout",
      "Object detection (one-stage vs two-stage, anchors, NMS)",
      "Semantic & instance segmentation (U-Net, Mask R-CNN)",
      "3D detection & BEV; LiDAR nets (PointNet/voxel)",
      "Metrics: IoU, mAP, precision/recall curves",
      "Sensor fusion & calibration for learned models",
    ],
    leetcode: [
      { name: "Maximal Square", pid: "maximal-square", url: "https://leetcode.com/problems/maximal-square/", diff: "Medium", tag: "DP/Grid" },
      { name: "Word Ladder", pid: "word-ladder", url: "https://leetcode.com/problems/word-ladder/", diff: "Hard", tag: "BFS" },
      { name: "LRU Cache", pid: "lru-cache", url: "https://leetcode.com/problems/lru-cache/", diff: "Medium", tag: "Design" },
    ],
    robotics: [
      { name: "IoU + Non-Max Suppression", pid: "rob-iou-nms", diff: "Medium", tag: "Detection", file: "coding-practice/robotics/w7_nms_iou.py" },
      { name: "Average Precision (detection)", pid: "rob-average-precision", diff: "Hard", tag: "Detection Metrics", file: "coding-practice/robotics/w7_map.py" },
    ],
  },
  {
    week: 8,
    title: "Systems, ROS & Mock Interviews",
    goal: "Wire it into real systems and rehearse the interview itself.",
    lecture: "lecture.html?week=8",
    topics: [
      "ROS/ROS2 concepts: nodes, topics, TF, time sync",
      "Real-time, latency, threading, memory in C++",
      "Coordinate frames & calibration in a full stack",
      "System design: 'design a perception pipeline for X'",
      "Behavioral stories (STAR) + project deep-dives",
      "2-3 timed mock interviews (coding + domain)",
    ],
    leetcode: [
      { name: "Merge Intervals", pid: "merge-intervals", url: "https://leetcode.com/problems/merge-intervals/", diff: "Medium", tag: "Intervals" },
      { name: "Design Circular Queue", pid: "design-circular-queue", url: "https://leetcode.com/problems/design-circular-queue/", diff: "Medium", tag: "Ring buffer" },
      { name: "Time-Based Key-Value Store", pid: "time-based-key-value-store", url: "https://leetcode.com/problems/time-based-key-value-store/", diff: "Medium", tag: "Design" },
    ],
    robotics: [
      { name: "Sensor Ring Buffer", pid: "rob-ring-buffer", diff: "Easy", tag: "Systems / Design", file: "coding-practice/robotics/w8_ring_buffer.py" },
      { name: "Nearest-Timestamp Sensor Sync", pid: "rob-time-sync", diff: "Medium", tag: "Systems / Sync", file: "coding-practice/robotics/w8_time_sync.py" },
    ],
  },
  {
    week: 9,
    title: "C++ for Robotics",
    goal: "The C++ idioms you're expected to speak fluently — RAII, ownership, move semantics, real-time memory, and concurrency. Plus a real-time systems problem; re-solve earlier ones with the C++ tab too.",
    lecture: "lecture.html?week=9",
    topics: [
      "RAII & deterministic resource management",
      "Smart pointers: unique_ptr / shared_ptr / weak_ptr",
      "Move semantics & the Rule of 0/3/5",
      "const correctness; references vs pointers",
      "STL containers & their complexity",
      "Memory, cache locality & real-time (no heap in hot loops)",
      "Concurrency: threads, mutex, atomics, data races",
      "Eigen / PCL / OpenCV / ROS2 & CMake basics",
    ],
    leetcode: [],
    robotics: [
      { name: "Real-Time Frame Ingest Buffer", pid: "rob-frame-ingest", diff: "Medium", tag: "Systems / Real-Time" },
    ],
  },
];

if (typeof module !== "undefined") module.exports = CURRICULUM;
