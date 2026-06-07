/* In-site coding practice: editor + runner. Executes real Python (CPython) and
   C++ (g++) through the Wandbox compile API, judges against verified test cases,
   and tracks solved problems in localStorage. */
(function () {
  const THEME_KEY = "rp_prep_theme";
  const SOLVED_KEY = "rp_prep_solved";
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
  function buildNav() {
    nav.innerHTML = "";
    let curWeek = null;
    PROBLEMS.slice().sort((a, b) => a.week - b.week).forEach((p) => {
      if (p.week !== curWeek) {
        curWeek = p.week;
        const h = document.createElement("div");
        h.className = "prob-week";
        h.textContent = "Week " + p.week;
        nav.appendChild(h);
      }
      const a = document.createElement("a");
      a.className = "prob-item" + (p.id === pid ? " active" : "");
      a.href = "practice.html?p=" + p.id;
      a.innerHTML = `<span class="pi-check">${solved[p.id] ? "✓" : "○"}</span>
        <span class="pi-title">${p.title}</span>
        <span class="badge ${p.diff}">${p.diff}</span>`;
      nav.appendChild(a);
    });
  }

  // ---------- editor helpers ----------
  const codeEl = document.getElementById("code");
  const codeKey = (id, l) => `rp_code_${id}_${l}`;
  function loadCode() {
    const saved = localStorage.getItem(codeKey(pid, lang));
    codeEl.value = saved != null ? saved : byId(pid).starter[lang];
  }
  codeEl.addEventListener("input", () => localStorage.setItem(codeKey(pid, lang), codeEl.value));
  // Tab inserts 4 spaces
  codeEl.addEventListener("keydown", (e) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const s = codeEl.selectionStart, en = codeEl.selectionEnd;
      codeEl.value = codeEl.value.slice(0, s) + "    " + codeEl.value.slice(en);
      codeEl.selectionStart = codeEl.selectionEnd = s + 4;
      localStorage.setItem(codeKey(pid, lang), codeEl.value);
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

  // ---------- runner ----------
  async function runWandbox(code, stdin) {
    const body = {
      compiler: COMPILER[lang],
      code,
      stdin,
      save: false,
    };
    if (lang === "cpp") body["compiler-option-raw"] = "-std=c++17\n-O2";
    const resp = await fetch(WANDBOX, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!resp.ok) throw new Error("Wandbox HTTP " + resp.status);
    return resp.json();
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
        const got = norm(r.program_output || "");
        const exp = norm(t.expected);
        const ok = got === exp;
        if (ok) passed++;
        rows.push({ i, ok, t, got, runtimeErr: (r.program_error || "").trim() });
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
      document.getElementById("prob-solved").hidden = false;
      buildNav();
      resultsEl.insertAdjacentHTML("afterbegin", `<div class="run-status ok">🎉 Marked as solved!</div>`);
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
