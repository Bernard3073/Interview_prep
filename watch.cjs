/* Dev watcher: rebuild the generated *-data.js whenever its source markdown
   changes, so the local site is never stale between edits and commits.

   Run: node watch.cjs

   Mirrors the pre-commit hook's source -> build -> output mapping:
     study-materials/*.md (top level)           -> build_lectures.cjs  -> lectures-data.js
     study-materials/leetcode-topics/*.md       -> build_topics.cjs    -> topics-data.js
     study-materials/data-structure-topics/*.md -> build_ds_topics.cjs -> ds-topics-data.js
   Leave it running in a terminal while you edit; save a .md and the matching
   data file rebuilds within ~150ms. Ctrl+C to stop. */
const { execFile } = require("child_process");
const fs = require("fs");
const path = require("path");

const SM = path.join(__dirname, "study-materials");

// Each source tree, its build script, and how to recognise a file that feeds it.
const TARGETS = [
  {
    name: "data-structure-topics",
    dir: path.join(SM, "data-structure-topics"),
    script: "build_ds_topics.cjs",
    matches: f => /\.md$/.test(f),
  },
  {
    name: "leetcode-topics",
    dir: path.join(SM, "leetcode-topics"),
    script: "build_topics.cjs",
    matches: f => /\.md$/.test(f),
  },
  {
    name: "lectures",
    dir: SM, // top-level *.md only; subdirs are handled above
    script: "build_lectures.cjs",
    matches: f => /\.md$/.test(f),
    topLevelOnly: true,
  },
];

const pending = new Set();
const timers = new Map();

function build(target) {
  execFile("node", [target.script], { cwd: __dirname }, (err, _stdout, stderr) => {
    const stamp = new Date().toLocaleTimeString();
    if (err) {
      console.error(`[${stamp}] ✗ ${target.script} failed:\n${stderr}`);
    } else {
      console.log(`[${stamp}] ✓ rebuilt via ${target.script}`);
    }
  });
}

// Debounce: editors fire several events per save, so coalesce per target.
function schedule(target) {
  if (timers.has(target.name)) clearTimeout(timers.get(target.name));
  timers.set(target.name, setTimeout(() => {
    timers.delete(target.name);
    build(target);
  }, 150));
}

for (const target of TARGETS) {
  if (!fs.existsSync(target.dir)) continue;
  fs.watch(target.dir, { recursive: !target.topLevelOnly }, (_event, filename) => {
    if (!filename) return;
    // For the lectures target, ignore nested files (subdir trees own those).
    if (target.topLevelOnly && filename.includes(path.sep)) return;
    if (!target.matches(filename)) return;
    schedule(target);
  });
  console.log(`watching ${path.relative(__dirname, target.dir)}/ -> ${target.script}`);
}

console.log("\nWatching for markdown changes. Ctrl+C to stop.");
