# 🤖 Robotics & Perception Engineer — Interview Prep

A self-contained, **trackable** 8-week study plan for robotics/perception engineer
interviews. Python + C++ focus, intermediate level. Includes lecture notes (with
diagrams), LeetCode pattern practice, and from-scratch robotics coding exercises
with self-tests.

## 🚀 Quick start

**Open the tracker** — just open `index.html` in a browser:

```bash
# from this folder
xdg-open index.html        # Linux
# or: open index.html      # macOS
# or simply double-click the file
```

Your progress (checkboxes) is saved automatically in the browser via
`localStorage`. Toggle dark/light, reset anytime.

> Tip: if links to `.md` / `.py` files don't open from `file://` in your browser,
> run a tiny local server instead:
> `python3 -m http.server` then visit `http://localhost:8000`.

## 📂 What's inside

```
robotics-perception-prep/
├── index.html / style.css / app.js   # the progress tracker website
├── curriculum.js                     # the 8-week plan data (edit to customize)
├── study-materials/
│   ├── 01-math-foundations.md
│   ├── 02-3d-geometry-transforms.md
│   ├── 03-camera-models-image-processing.md
│   ├── 04-features-multiview-geometry.md
│   ├── 05-state-estimation.md
│   ├── 06-slam-odometry.md
│   ├── 07-deep-learning-perception.md
│   ├── 08-systems-ros-interview.md
│   └── images/                       # SVG diagrams used in the notes
└── coding-practice/
    ├── leetcode/README.md            # patterns guide + problem map
    └── robotics/                     # 16 from-scratch exercises w/ self-tests
```

## 🗓️ The 8-week plan at a glance

| Week | Theme |
|---|---|
| 1 | Math foundations (linear algebra, probability, optimization) |
| 2 | 3D geometry & rigid-body transforms (SO(3), quaternions, SE(3)) |
| 3 | Camera models & classical image processing |
| 4 | Features & multi-view geometry (RANSAC, epipolar, BA) |
| 5 | State estimation & filtering (KF / EKF / UKF / particle) |
| 6 | SLAM, odometry & sensor fusion (VO, ICP, pose graphs, VIO) |
| 7 | Deep learning for perception (detection, segmentation, 3D, point clouds) |
| 8 | Systems, ROS & mock interviews |

Each week = lecture topics + 3 LeetCode problems + 2 robotics coding exercises,
all tracked as checkboxes.

## 🧪 Running the robotics exercises

They need only `numpy`. Each file has a problem statement, a reference solution,
and an assertion-based self-test:

```bash
pip install numpy
cd coding-practice/robotics
python w1_least_squares.py
python w5_kalman_1d.py
# ... etc. Each prints results and ends with "OK" if correct.
```

Run them all:

```bash
cd coding-practice/robotics
for f in w*.py; do echo "=== $f ==="; python "$f" || break; done
```

## 🎯 How to use this

1. Open the tracker, read each week's **lecture note** first.
2. Implement the **robotics exercise** yourself before reading the reference.
3. Do the **LeetCode** problems for that week's pattern.
4. Check items off as you go; aim to finish a week before moving on.
5. Week 8: do the timed mock interviews and the final checklist.

## ✏️ Customizing

Edit `curriculum.js` to add/remove topics, problems, or weeks — the tracker reads
it directly, no build step. Add new lecture `.md` files under `study-materials/`
and point to them from the curriculum.

---
*Good luck — and remember: in robotics interviews, reasoning about frames,
uncertainty, time sync, and failure modes impresses more than memorized algorithms.*
