/* In-site coding practice: editor + runner. Executes real Python (CPython) and
   C++ (g++) through the Wandbox compile API, judges against verified test cases,
   and tracks solved problems in localStorage. */
(function () {
  const THEME_KEY = "rp_prep_theme";
  const SOLVED_KEY = "rp_prep_solved";
  const SCROLL_KEY = "rp_prac_scroll";   // sidebar scroll position, preserved across selects
  const WANDBOX = "https://wandbox.org/api/compile.json";
  const COMPILER = { python: "cpython-3.12.7", cpp: "gcc-13.2.0" };

  const byId = (id) => PROBLEMS.find((p) => p.id === id);
  const params = new URLSearchParams(location.search);
  let pid = params.get("p");
  if (!byId(pid)) pid = PROBLEMS[0].id;
  let lang = localStorage.getItem("rp_prac_lang") || "python";

  // ---------- theme ----------
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    document.getElementById("theme-btn").textContent = t === "light" ? "☀️" : "🌙";
    localStorage.setItem(THEME_KEY, t);
  }
  document.getElementById("theme-btn").addEventListener("click", () => {
    applyTheme(document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light");
  });
  applyTheme(localStorage.getItem(THEME_KEY) || "dark");

  // ---------- solved state ----------
  const loadSolved = () => { try { return JSON.parse(localStorage.getItem(SOLVED_KEY)) || {}; } catch { return {}; } };
  const saveSolved = (s) => localStorage.setItem(SOLVED_KEY, JSON.stringify(s));
  let solved = loadSolved();

  // ---------- sidebar ----------
  const nav = document.getElementById("prob-nav");
  let filter = localStorage.getItem("rp_prac_filter") || "all";
  function buildNav() {
    nav.innerHTML = "";
    let curWeek = null;
    PROBLEMS.slice()
      .sort((a, b) => a.week - b.week || (a.category > b.category ? 1 : -1))
      .filter((p) => filter === "all" || (p.category || "leetcode") === filter)
      .forEach((p) => {
        if (p.week !== curWeek) {
          curWeek = p.week;
          const h = document.createElement("div");
          h.className = "prob-week";
          h.textContent = "Week " + p.week;
          nav.appendChild(h);
        }
        const cat = p.category || "leetcode";
        const a = document.createElement("a");
        a.className = "prob-item" + (p.id === pid ? " active" : "");
        a.href = "practice.html?p=" + p.id;
        a.innerHTML = `<span class="pi-check">${solved[p.id] ? "✓" : "○"}</span>
          <span class="pi-cat ${cat}">${cat === "robotics" ? "ROB" : "LC"}</span>
          <span class="pi-title">${p.title}</span>
          <span class="badge ${p.diff}">${p.diff}</span>`;
        nav.appendChild(a);
      });
    placeSidebar();
  }

  // Selecting a problem reloads the page. To stop the sidebar jumping each time, we
  // restore exactly where it was — the item you clicked is already in view, so nothing
  // moves. We only scroll when the selected item is genuinely off-screen (e.g. a deep
  // link from a lecture), and then just enough to reveal it, scrolling the sidebar only.
  const sidebarEl = nav.closest(".prob-sidebar");
  function placeSidebar() {
    if (!sidebarEl) return;
    const saved = sessionStorage.getItem(SCROLL_KEY);
    if (saved != null) sidebarEl.scrollTop = parseFloat(saved) || 0;  // preserve → no jump
    requestAnimationFrame(() => {
      const active = nav.querySelector(".prob-item.active");
      if (!active) return;
      const sb = sidebarEl.getBoundingClientRect();
      const a = active.getBoundingClientRect();
      if (a.top >= sb.top && a.bottom <= sb.bottom) return;  // already visible: don't move
      // Off-screen: center it. Rect math works regardless of the offset parent.
      const activeTopInContent = (a.top - sb.top) + sidebarEl.scrollTop;
      const target = activeTopInContent - (sidebarEl.clientHeight - a.height) / 2;
      const max = sidebarEl.scrollHeight - sidebarEl.clientHeight;
      sidebarEl.scrollTop = Math.max(0, Math.min(target, max));
    });
  }
  // Remember the sidebar's scroll position as the user scrolls, so it survives the
  // reload that happens when they click a different problem.
  if (sidebarEl) {
    sidebarEl.addEventListener("scroll", () => {
      sessionStorage.setItem(SCROLL_KEY, sidebarEl.scrollTop);
    }, { passive: true });
  }
  document.querySelectorAll(".filt-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.filt === filter);
    b.addEventListener("click", () => {
      filter = b.dataset.filt;
      localStorage.setItem("rp_prac_filter", filter);
      document.querySelectorAll(".filt-btn").forEach((x) => x.classList.toggle("active", x.dataset.filt === filter));
      buildNav();
    });
  });

  // ---------- editor helpers ----------
  const codeEl = document.getElementById("code");
  const codeKey = (id, l) => `rp_code_${id}_${l}`;
  // Snapshot of the code that actually PASSED, kept separately from the live draft
  // so editing or resetting never loses your accepted solution.
  const solnKey = (id, l) => `rp_soln_${id}_${l}`;
  const solnBtn = document.getElementById("load-soln");

  function loadCode() {
    const saved = localStorage.getItem(codeKey(pid, lang));
    codeEl.value = saved != null ? saved : byId(pid).starter[lang];
    updateSolnBtn();
    renderHL(); syncScroll();
  }
  function updateSolnBtn() {
    solnBtn.hidden = localStorage.getItem(solnKey(pid, lang)) == null;
  }
  solnBtn.addEventListener("click", () => {
    const sol = localStorage.getItem(solnKey(pid, lang));
    if (sol == null) return;
    codeEl.value = sol;
    localStorage.setItem(codeKey(pid, lang), sol);
    renderHL();
  });
  const hlEl = document.getElementById("code-hl");
  function renderHL() { if (window.highlightCode) hlEl.innerHTML = highlightCode(codeEl.value, lang); }
  function syncScroll() { hlEl.scrollTop = codeEl.scrollTop; hlEl.scrollLeft = codeEl.scrollLeft; }

  const persist = () => localStorage.setItem(codeKey(pid, lang), codeEl.value);
  codeEl.addEventListener("input", () => { persist(); renderHL(); });
  codeEl.addEventListener("scroll", syncScroll);

  const UNIT = "    "; // one indent level = 4 spaces

  // Insert text at the caret, preserving native undo where possible.
  function insertText(text) {
    const ok = document.execCommand && document.execCommand("insertText", false, text);
    if (!ok) {                       // fallback for browsers without execCommand
      const s = codeEl.selectionStart, en = codeEl.selectionEnd;
      codeEl.value = codeEl.value.slice(0, s) + text + codeEl.value.slice(en);
      codeEl.selectionStart = codeEl.selectionEnd = s + text.length;
      persist(); renderHL();
    }
  }

  // Editor conveniences: Tab indents, Enter auto-indents (and continues blocks),
  // and in C++ a closing brace auto-dedents / brace pairs expand.
  codeEl.addEventListener("keydown", (e) => {
    const v = codeEl.value, s = codeEl.selectionStart, en = codeEl.selectionEnd;

    if (e.key === "Tab") {
      e.preventDefault();
      insertText(UNIT);
      return;
    }

    if (e.key === "Enter") {
      e.preventDefault();
      const lineStart = v.lastIndexOf("\n", s - 1) + 1;
      const curLine = v.slice(lineStart, s);
      const baseIndent = (curLine.match(/^[ \t]*/) || [""])[0];
      const trimmed = curLine.replace(/\s+$/, "");
      // Open a new indent level after a block header.
      const opensBlock =
        (lang === "python" && /:$/.test(trimmed)) ||
        (lang === "cpp" && (/[{([]$/.test(trimmed) ||
          /^\s*(if|for|while|else\s+if|else|do|switch)\b.*\)\s*$/.test(curLine) ||
          /^\s*else\s*$/.test(curLine)));
      const indent = baseIndent + (opensBlock ? UNIT : "");
      const after = v.slice(en, en + 1);
      // C++: pressing Enter between `{` and `}` drops the brace to its own line.
      if (lang === "cpp" && /\{$/.test(trimmed) && after === "}") {
        insertText("\n" + indent + "\n" + baseIndent);
        codeEl.selectionStart = codeEl.selectionEnd = s + 1 + indent.length;
      } else {
        insertText("\n" + indent);
      }
      return;
    }

    // C++: typing `}` on a blank, indented line snaps it out one level.
    if (lang === "cpp" && e.key === "}" && s === en) {
      const lineStart = v.lastIndexOf("\n", s - 1) + 1;
      const before = v.slice(lineStart, s);
      if (/^[ \t]+$/.test(before) && before.length >= UNIT.length) {
        e.preventDefault();
        codeEl.selectionStart = s - UNIT.length;  // select the trailing indent
        insertText("}");                          // replace it with the brace
      }
    }
  });

  // ---------- render problem ----------
  function renderProblem() {
    const p = byId(pid);
    document.title = `${p.title} — Practice`;
    document.getElementById("prob-title").textContent = p.title;
    const diff = document.getElementById("prob-diff");
    diff.textContent = p.diff; diff.className = "badge " + p.diff;
    document.getElementById("prob-pattern").textContent = p.pattern;
    const catEl = document.getElementById("prob-cat");
    const cat = p.category || "leetcode";
    catEl.textContent = cat === "robotics" ? "Robotics" : "LeetCode";
    catEl.className = "cat-chip " + cat;
    const lecEl = document.getElementById("prob-lecture");
    lecEl.href = `lecture.html?week=${p.week}`;
    lecEl.textContent = `📖 Week ${p.week} lecture`;
    document.getElementById("prob-solved").hidden = !solved[p.id];
    document.getElementById("prob-statement").innerHTML = p.statement;
    document.getElementById("prob-in").textContent = p.inputFormat;
    document.getElementById("prob-out").textContent = p.outputFormat;
    const ex = document.getElementById("prob-examples");
    ex.innerHTML = "";
    p.tests.filter((t) => t.sample).forEach((t, i) => {
      const d = document.createElement("div");
      d.className = "example";
      d.innerHTML = `<div class="ex-label">Example ${i + 1}</div>
        <div class="ex-grid">
          <div><span>Input</span><pre>${escapeHtml(t.input)}</pre></div>
          <div><span>Output</span><pre>${escapeHtml(t.expected)}</pre></div>
        </div>`;
      ex.appendChild(d);
    });
    loadCode();
  }

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  const norm = (s) => s.replace(/\r/g, "").split("\n").map((l) => l.replace(/\s+$/, "")).join("\n").replace(/\n+$/, "");

  // Output checker: exact (default) or float-tolerant (token-wise) for numeric problems.
  function checkOutput(problem, got, expected) {
    if (problem.checker === "float") {
      const g = norm(got).split(/\s+/).filter(Boolean);
      const e = norm(expected).split(/\s+/).filter(Boolean);
      if (g.length !== e.length) return false;
      const tol = problem.tol || 1e-3;
      for (let i = 0; i < e.length; i++) {
        const a = parseFloat(g[i]), b = parseFloat(e[i]);
        if (!isNaN(a) && !isNaN(b)) {
          if (Math.abs(a - b) > tol + tol * Math.abs(b)) return false;
        } else if (g[i] !== e[i]) return false;
      }
      return true;
    }
    return norm(got) === norm(expected);
  }

  // ---------- runner ----------
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  async function runWandbox(code, stdin) {
    const body = { compiler: COMPILER[lang], code, stdin, save: false };
    if (lang === "cpp") body["compiler-option-raw"] = "-std=c++17\n-O2";
    // The shared runner occasionally returns a transient "resource unavailable"
    // error under load — retry a couple of times before giving up.
    let last;
    for (let attempt = 0; attempt < 3; attempt++) {
      const resp = await fetch(WANDBOX, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!resp.ok) { last = new Error("Wandbox HTTP " + resp.status); await sleep(1500); continue; }
      const json = await resp.json();
      const transient = /temporarily unavailable|OCI runtime|Resource/i.test(
        (json.compiler_error || "") + (json.program_error || "") + (json.compiler_message || ""));
      if (transient && attempt < 2) { await sleep(2000); continue; }
      return json;
    }
    throw (last || new Error("runner temporarily unavailable — try again"));
  }

  const resultsEl = document.getElementById("results");
  let running = false;

  async function judge(all) {
    if (running) return;
    running = true;
    const p = byId(pid);
    const cases = all ? p.tests : p.tests.filter((t) => t.sample);
    const code = codeEl.value;
    setButtons(true);
    resultsEl.innerHTML = `<div class="run-status">⏳ Compiling &amp; running ${cases.length} test${cases.length > 1 ? "s" : ""} (${lang === "cpp" ? "g++" : "Python"})…</div>`;

    let passed = 0;
    const rows = [];
    try {
      for (let i = 0; i < cases.length; i++) {
        const t = cases[i];
        let r;
        try {
          r = await runWandbox(code, t.input);
        } catch (err) {
          resultsEl.innerHTML = `<div class="run-status err">⚠ Could not reach the code runner (${escapeHtml(err.message)}).<br>Check your internet connection — execution uses the Wandbox API.</div>`;
          running = false; setButtons(false); return;
        }
        const compileErr = (r.compiler_error || "").trim();
        if (compileErr && (r.status !== "0" || (r.program_output == null && !r.program_error))) {
          // compile failure: stop and show
          resultsEl.innerHTML = `<div class="run-status err">❌ Compile error</div><pre class="err-out">${escapeHtml(compileErr)}</pre>`;
          running = false; setButtons(false); return;
        }
        const got = r.program_output || "";
        const ok = checkOutput(p, got, t.expected);
        if (ok) passed++;
        rows.push({ i, ok, t, got: norm(got), runtimeErr: (r.program_error || "").trim() });
      }
    } finally {
      setButtons(false); running = false;
    }

    // summary + per-case
    const total = cases.length;
    const allPass = passed === total;
    let html = `<div class="run-status ${allPass ? "ok" : "fail"}">${allPass ? "✅" : "❌"} ${passed}/${total} ${all ? "test cases" : "examples"} passed</div>`;
    rows.forEach((row) => {
      const t = row.t;
      html += `<details class="case ${row.ok ? "pass" : "failcase"}" ${row.ok ? "" : "open"}>
        <summary>${row.ok ? "✓" : "✗"} ${t.sample ? "Example" : "Test"} ${row.i + 1}</summary>
        <div class="case-body">
          <div><span>Input</span><pre>${escapeHtml(t.input)}</pre></div>
          <div><span>Expected</span><pre>${escapeHtml(t.expected)}</pre></div>
          <div><span>Your output</span><pre>${escapeHtml(row.got || "(empty)")}</pre></div>
          ${row.runtimeErr ? `<div><span>Stderr</span><pre class="err-out">${escapeHtml(row.runtimeErr)}</pre></div>` : ""}
        </div></details>`;
    });
    resultsEl.innerHTML = html;

    if (all && allPass) {
      solved[pid] = true; saveSolved(solved);
      localStorage.setItem(solnKey(pid, lang), code);   // keep the accepted solution
      updateSolnBtn();
      document.getElementById("prob-solved").hidden = false;
      buildNav();
      resultsEl.insertAdjacentHTML("afterbegin", `<div class="run-status ok">🎉 Marked as solved! Your accepted solution is saved — restore it anytime with “✓ My solution”.</div>`);
    }
  }

  function setButtons(disabled) {
    document.getElementById("run-btn").disabled = disabled;
    document.getElementById("submit-btn").disabled = disabled;
  }

  document.getElementById("run-btn").addEventListener("click", () => judge(false));
  document.getElementById("submit-btn").addEventListener("click", () => judge(true));
  document.getElementById("reset-code").addEventListener("click", () => {
    if (confirm("Reset your code to the starter template?")) {
      codeEl.value = byId(pid).starter[lang];
      localStorage.setItem(codeKey(pid, lang), codeEl.value);
      renderHL();
    }
  });

  // language toggle
  document.querySelectorAll(".lang-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.lang === lang);
    b.addEventListener("click", () => {
      lang = b.dataset.lang;
      localStorage.setItem("rp_prac_lang", lang);
      document.querySelectorAll(".lang-btn").forEach((x) => x.classList.toggle("active", x.dataset.lang === lang));
      loadCode();
    });
  });

  buildNav();
  renderProblem();
})();
