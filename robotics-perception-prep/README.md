# 🤖 Robotics & Perception Engineer — Interview Prep

A self-contained, **trackable** 8-week study plan for robotics/perception engineer
interviews. Python + C++ focus, intermediate level. Includes in-browser lecture
notes (rendered as real web pages, with diagrams), LeetCode pattern practice, and
from-scratch robotics coding exercises with self-tests.

## 🚀 Quick start

Open **`index.html`** in a browser — that's the whole app:

```bash
xdg-open index.html        # Linux
# or: open index.html      # macOS
# or simply double-click the file
```

- The tracker home (`index.html`) shows progress and checkboxes per week.
- Click **"Read lecture notes"** on any week to open the **lecture reader**
  (`lecture.html`) — a styled page with sidebar navigation, an auto
  table-of-contents, inline diagrams, and prev/next buttons.
- Each lecture ends with **interview-style questions as click-to-reveal Q&A** —
  try to answer first, then expand to compare with a model answer.
- Click any of the **40 coding problems** (24 LeetCode + 16 robotics/perception) to
  solve it **inside the site** (`practice.html`): read the statement, write Python or
  C++ in the editor, and **Run / Submit** against test cases. Numeric (robotics)
  problems use a float-tolerant judge. Code executes on real CPython 3.12 and g++ 13
  via the Wandbox compile API, so the runner needs internet (the rest stays offline).
- Each **lecture page** ends with a "Practice for this week" panel linking straight
  to that week's problems, and each problem links back to its lecture.
- Progress (checkboxes) and the dark/light theme are saved automatically in the
  browser via `localStorage` and shared across both pages.

Everything works offline straight from the filesystem (`file://`) — no server, no
internet, no build step required to use it.

## 📂 What's inside

```
robotics-perception-prep/
├── index.html / app.js          # progress tracker (home)
├── lecture.html / lecture.js    # in-site lecture reader
├── lectures-data.js             # lecture content as rendered HTML  ← what the site shows
├── practice.html / practice.js  # in-site LeetCode editor + test runner
├── problems.js                  # 40 problems w/ verified test cases  ← what practice shows
├── curriculum.js                # the 8-week plan data (single source of truth)
├── style.css                    # shared theme for all pages
├── build_lectures.cjs           # regenerates lectures-data.js from markdown source
├── gen_problems.py              # regenerates problems.js (verifies test cases locally)
├── study-materials/
│   ├── *.md                     # editable SOURCE for the notes (not shown raw)
│   └── images/                  # SVG diagrams used in the notes
└── coding-practice/
    ├── leetcode/README.md       # patterns guide + problem map
    └── robotics/                # 16 from-scratch exercises w/ self-tests
```

> **Why both `.md` and `lectures-data.js`?** The website never serves raw markdown
> (that's the ugly part you wanted gone) — it renders the polished HTML in
> `lectures-data.js`. The `study-materials/*.md` files are kept only as the
> *editable source*. Edit them and run `node build_lectures.cjs` to regenerate the
> rendered notes, or just edit `lectures-data.js` directly.

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

> These `coding-practice/robotics/*.py` files are the **full numpy reference
> versions** (richer than the in-site problems). The tracker links to them as
> "📄 .py" next to each in-site robotics problem. To *practice* interactively,
> use the in-site editor instead (no numpy needed); use these to study a complete,
> idiomatic solution.

They need only `numpy`. Each file has a problem statement, a reference solution,
and an assertion-based self-test:

```bash
pip install numpy
cd coding-practice/robotics
python w1_least_squares.py      # prints results, ends with "OK" if correct
```

Run them all:

```bash
cd coding-practice/robotics
for f in w*.py; do echo "=== $f ==="; python "$f" || break; done
```

## 🎯 How to use this

1. Open the tracker, read each week's **lecture** (the reader page) first.
2. Implement the **robotics exercise** yourself before reading the reference.
3. Do the **LeetCode** problems for that week's pattern.
4. Check items off as you go; aim to finish a week before moving on.
5. Week 8: do the timed mock interviews and the final checklist.

## ✏️ Customizing

- **Plan / problems:** edit `curriculum.js` — every page reads it directly.
- **Lecture content:** edit `study-materials/*.md` and run
  `node build_lectures.cjs`, or edit `lectures-data.js` directly.
- **Practice problems:** edit `gen_problems.py` (add a statement, starter code, and
  test inputs) and run `python3 gen_problems.py` — it computes the expected outputs
  from a reference solution and compile-checks the C++ starters, then writes
  `problems.js`. All 40 problems (24 LeetCode + 16 robotics/perception) are solvable
  in-site, in Python or C++.
- **Look & feel:** edit `style.css` (theme variables live at the top in `:root`).

---
*Good luck — and remember: in robotics interviews, reasoning about frames,
uncertainty, time sync, and failure modes impresses more than memorized algorithms.*
