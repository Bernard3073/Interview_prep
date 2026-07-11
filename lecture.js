/* Lecture reader: renders pre-built HTML from lectures-data.js,
   builds the sidebar (from curriculum.js), an auto table-of-contents,
   prev/next navigation, and syncs the theme with the tracker. */
(function () {
  const THEME_KEY = "rp_prep_theme";
  const params = new URLSearchParams(location.search);
  let week = parseInt(params.get("week"), 10);
  const weeks = CURRICULUM.map((w) => w.week);
  if (!weeks.includes(week)) week = weeks[0];

  // ---- theme (shared with tracker) ----
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    document.getElementById("theme-btn").textContent = t === "light" ? "☀️" : "🌙";
    localStorage.setItem(THEME_KEY, t);
  }
  document.getElementById("theme-btn").addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
    applyTheme(cur);
  });
  applyTheme(localStorage.getItem(THEME_KEY) || "dark");

  // ---- left sidebar: all lectures ----
  const nav = document.getElementById("lec-nav");
  CURRICULUM.forEach((w) => {
    const a = document.createElement("a");
    a.className = "lec-nav-item" + (w.week === week ? " active" : "");
    a.href = `lecture.html?week=${w.week}`;
    a.innerHTML = `<span class="lec-nav-num">W${w.week}</span><span>${w.title}</span>`;
    nav.appendChild(a);
  });

  // ---- main content ----
  const data = LECTURES[week] || LECTURES[String(week)];
  const cur = CURRICULUM.find((w) => w.week === week);
  document.title = `Week ${week}: ${cur.title} — Prep`;
  // Title: drop the "Week N — " prefix if present (we show the week badge separately)
  const cleanTitle = (data.title || cur.title).replace(/^Week\s*\d+\s*[—-]\s*/, "");
  document.getElementById("lec-title").innerHTML =
    `<span class="lec-week-badge">Week ${week}</span>${cleanTitle}`;
  document.getElementById("lec-body").innerHTML = data.html;

  // ---- VS Code-style code blocks (window chrome + Dark+ syntax highlighting) ----
  (function styleCodeBlocks() {
    const LABELS = {
      python: "Python", py: "Python",
      cpp: "C++", "c++": "C++", cc: "C++", cxx: "C++", c: "C",
      text: "pseudocode", plaintext: "pseudocode", pseudocode: "pseudocode",
      bash: "bash", sh: "shell", js: "JavaScript", javascript: "JavaScript",
    };
    const HL = { python: "python", py: "python", cpp: "cpp", "c++": "cpp", cc: "cpp", cxx: "cpp" };
    document.querySelectorAll("#lec-body pre.lec-pre").forEach((pre) => {
      const lang = (pre.getAttribute("data-lang") || "").toLowerCase();
      const code = pre.querySelector("code");
      const raw = code ? code.textContent : "";
      if (HL[lang] && code && window.highlightCode) {
        code.innerHTML = window.highlightCode(raw, HL[lang]);   // text unchanged; adds tok-* spans
      }
      const win = document.createElement("div");
      win.className = "code-window";
      const bar = document.createElement("div");
      bar.className = "code-titlebar";
      bar.innerHTML =
        `<span class="code-dots"><i></i><i></i><i></i></span>` +
        `<span class="code-lang">${LABELS[lang] || lang || "code"}</span>` +
        `<button class="code-copy" type="button" title="Copy code">Copy</button>`;
      pre.parentNode.insertBefore(win, pre);
      win.appendChild(bar);
      win.appendChild(pre);
      bar.querySelector(".code-copy").addEventListener("click", (e) => {
        const btn = e.currentTarget;
        if (!navigator.clipboard) return;
        navigator.clipboard.writeText(raw).then(() => {
          btn.textContent = "Copied ✓";
          setTimeout(() => { btn.textContent = "Copy"; }, 1200);
        });
      });
    });
  })();

  // ---- Python / C++ solution tabs (shared preference switches all at once) ----
  (function wireSolutionTabs() {
    const LANG_KEY = "rp_topic_lang";   // shared with the topic deep-dive pages
    const sols = Array.from(document.querySelectorAll("#lec-body .sol"));
    if (!sols.length) return;
    let lang = localStorage.getItem(LANG_KEY) || "python";

    function show(l) {
      lang = l;
      localStorage.setItem(LANG_KEY, l);
      sols.forEach((sol) => {
        // fall back to whatever pane exists if a solution lacks one language
        const has = Array.from(sol.querySelectorAll(".sol-pane")).some(
          (p) => p.getAttribute("data-lang") === l
        );
        const target = has ? l : sol.querySelector(".sol-pane").getAttribute("data-lang");
        sol.querySelectorAll(".sol-tab").forEach((b) =>
          b.classList.toggle("active", b.dataset.lang === target)
        );
        sol.querySelectorAll(".sol-pane").forEach((p) =>
          (p.hidden = p.getAttribute("data-lang") !== target)
        );
      });
    }

    sols.forEach((sol) => {
      sol.querySelectorAll(".sol-tab").forEach((btn) => {
        btn.addEventListener("click", () => show(btn.dataset.lang));
      });
    });
    show(lang);
  })();

  // ---- "Practice for this week" panel (links to the in-site coding playground) ----
  (function addPracticePanel() {
    const all = [].concat(cur.leetcode || [], cur.robotics || []).filter((p) => p.pid);
    if (!all.length) return;
    const solved = (() => { try { return JSON.parse(localStorage.getItem("rp_prep_solved")) || {}; } catch { return {}; } })();
    const panel = document.createElement("div");
    panel.className = "lec-practice";
    panel.innerHTML = `<h2 id="practice-this-week">💻 Practice for this week</h2>
      <p>Solve these in the in-site editor (Python or C++), no setup needed.</p>`;
    const ul = document.createElement("ul");
    ul.className = "lec-practice-list";
    all.forEach((p) => {
      const li = document.createElement("li");
      const done = solved[p.pid] ? `<span class="mini-solved">✓</span>` : "";
      li.innerHTML = `${done}<a href="practice.html?p=${p.pid}">${p.name}</a>
        <span class="badge ${p.diff}">${p.diff}</span>
        <span class="tag">${p.tag || ""}</span>`;
      ul.appendChild(li);
    });
    panel.appendChild(ul);
    document.getElementById("lec-body").appendChild(panel);
    // include in the TOC
    (data.toc || []).push({ level: 2, txt: "Practice for this week", id: "practice-this-week" });
  })();

  // ---- right TOC ----
  const tocNav = document.getElementById("toc-nav");
  (data.toc || []).forEach((t) => {
    const a = document.createElement("a");
    a.className = "toc-item lvl" + t.level;
    a.href = "#" + t.id;
    a.textContent = t.txt.replace(/^\d+\.\s*/, "");
    a.addEventListener("click", (e) => {
      e.preventDefault();
      const el = document.getElementById(t.id);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      history.replaceState(null, "", "#" + t.id);
      closeTocMobile();
    });
    tocNav.appendChild(a);
  });

  // ---- scroll spy: highlight current TOC entry ----
  const headings = (data.toc || []).map((t) => document.getElementById(t.id)).filter(Boolean);
  const tocLinks = Array.from(tocNav.querySelectorAll(".toc-item"));
  function onScroll() {
    let idx = 0;
    for (let k = 0; k < headings.length; k++) {
      if (headings[k].getBoundingClientRect().top - 90 <= 0) idx = k;
    }
    tocLinks.forEach((l, k) => l.classList.toggle("active", k === idx));
  }
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ---- prev / next ----
  const idx = weeks.indexOf(week);
  const prev = document.getElementById("lec-prev");
  const next = document.getElementById("lec-next");
  if (idx > 0) {
    const pw = CURRICULUM[idx - 1];
    prev.href = `lecture.html?week=${pw.week}`;
    prev.innerHTML = `← Week ${pw.week}: ${pw.title}`;
  } else { prev.classList.add("disabled"); prev.textContent = ""; }
  if (idx < weeks.length - 1) {
    const nw = CURRICULUM[idx + 1];
    next.href = `lecture.html?week=${nw.week}`;
    next.innerHTML = `Week ${nw.week}: ${nw.title} →`;
  } else { next.classList.add("disabled"); next.textContent = ""; }

  // ---- mobile TOC toggle ----
  const tocAside = document.querySelector(".lec-toc");
  function closeTocMobile() { tocAside.classList.remove("open"); }
  document.getElementById("toc-fab").addEventListener("click", () => {
    tocAside.classList.toggle("open");
  });

  // jump to hash if present
  if (location.hash) {
    const el = document.getElementById(location.hash.slice(1));
    if (el) setTimeout(() => el.scrollIntoView(), 50);
  }
})();
