# Week 10 — Systems, ROS & Interview Prep

> Algorithms are necessary but not sufficient. Robotics roles test whether you can
> build a *system*: real-time, multi-sensor, debuggable. This week wires it all
> together and rehearses the interview.

---

## 1. ROS / ROS2 essentials

- **Nodes** (processes), **topics** (pub/sub streams), **services** (request/reply),
  **actions** (long-running goals), **parameters**.
- **Messages**: typed; sensor_msgs (Image, PointCloud2, Imu), geometry_msgs (Pose,
  Transform), nav_msgs (Odometry).
- **TF / tf2:** the transform tree — keeps every frame's relationship over time so
  you can ask "where was the LiDAR in the map frame at timestamp t?" Learn
  `lookup_transform`, static vs dynamic transforms.
- **Time & sync:** `message_filters` ApproximateTime/ExactTime to align
  multi-sensor messages; use sensor timestamps, not wall clock.
- **ROS2 specifics:** DDS middleware, QoS profiles (reliability/durability),
  lifecycle nodes, executors. Better for real-time/multi-robot than ROS1.
- **Tooling:** `rosbag` (record/replay — your best debugging friend), `rviz`
  (visualize), `rqt_graph`, `ros2 topic echo/hz`.

---

## 2. Real-time & C++ systems concerns

- **Latency & throughput:** perception runs in a pipeline; identify the bottleneck,
  budget per stage, measure (don't guess).
- **Memory:** avoid allocations in the hot loop; preallocate; pools/ring buffers;
  zero-copy where possible.
- **Concurrency:** threads for capture vs processing; lock-free / bounded queues;
  beware priority inversion. Understand data races and how to avoid them.
- **C++ for robotics:** RAII, `std::move`, smart pointers, `const` correctness,
  Eigen (fixed-size types, alignment), avoiding undefined behavior. PCL for point
  clouds, OpenCV for images.
- **Determinism:** real-time systems care about *worst-case*, not average.

---

## 3. Calibration & coordinate frames in a full stack

- **Intrinsic** (per camera) + **extrinsic** (sensor-to-sensor / sensor-to-body).
- Camera–LiDAR, camera–IMU (Kalibr), wheel odometry — each has a calibration
  procedure and failure mode.
- A surprising fraction of "perception bugs" are actually frame/timestamp/
  calibration bugs. Always verify the transform tree first.

---

## 4. System design questions

Expect open-ended prompts like *"Design the perception system for a delivery robot /
warehouse AMR / L2 driving feature."* Structure your answer:

1. **Clarify**: requirements, sensors available, compute budget, latency, safety,
   environment (indoor/outdoor, dynamic?).
2. **Sensors & why**: camera vs LiDAR vs radar vs ultrasonic; redundancy.
3. **Pipeline**: capture → sync → calibration → detection/segmentation →
   tracking → localization/mapping → output to planning.
4. **Estimation/fusion**: filter or factor graph; how sensors fuse.
5. **Failure handling**: sensor dropout, degraded conditions (rain, low light),
   confidence/uncertainty, fallbacks, safety monitor.
6. **Eval & metrics**: how you measure success; logging; data pipeline for
   improvement.
7. **Compute/deployment**: on-board vs offload, real-time budget.

> Show you think about edge cases, uncertainty, and safety — that's what separates
> a robotics engineer from someone who only knows the algorithms.

---

## 5. Behavioral & project deep-dives

- Prepare 3–4 **STAR** stories (Situation, Task, Action, Result): a hard debugging
  win, a design trade-off you made, a failure you learned from, cross-team work.
- Be able to **whiteboard your past projects' architecture** end to end and defend
  every design choice ("why EKF not factor graph?", "why this sensor?").
- Tie answers to measurable impact (latency cut, accuracy gained, drift reduced).

---

## 6. Mock interview plan (do these timed)

- [ ] **Mock 1 — Coding:** 2 LeetCode mediums in 45 min, talk aloud.
- [ ] **Mock 2 — Domain:** geometry + estimation rapid-fire (use the
      interview-style questions in each lecture file).
- [ ] **Mock 3 — System design:** 45-min "design a perception pipeline for X".
- [ ] Record yourself or pair with a peer; review where you got stuck.

---

## Final-week checklist
- [ ] Can derive: pinhole projection, Kalman gain, Gauss–Newton, epipolar constraint.
- [ ] Can implement from scratch: convolution, RANSAC, IoU+NMS, 1D Kalman, ICP step.
- [ ] Can whiteboard: a full VIO/SLAM pipeline and a learned 3D detection stack.
- [ ] Frames/timestamps/calibration debugging story ready.
- [ ] 3–4 STAR stories rehearsed.

## Resources
- ROS2 docs + "ROS2 in 5 days" tutorials.
- *Programming Robots with ROS* (O'Reilly).
- "Grokking the System Design Interview" for structure (adapt to robotics).
- Reread the survey papers and your own project notes.

➡ **Practice (solve in-site):** [w8_ring_buffer.py](practice.html?p=rob-ring-buffer), [w8_time_sync.py](practice.html?p=rob-time-sync)
