/* Topic deep-dive reader: renders one pattern subpage from topics-data.js,
   builds the sidebar (all patterns), an auto TOC, prev/next, and wires the
   Python/C++ solution tabs (a shared preference switches every solution at once). */
(function () {
  const THEME_KEY = "rp_prep_theme";
  const LANG_KEY = "rp_topic_lang";
  const params = new URLSearchParams(location.search);
  const slugs = TOPICS.map((t) => t.slug);
  let slug = params.get("t");
  if (!slugs.includes(slug)) slug = slugs[0];
  const idx = slugs.indexOf(slug);
  const topic = TOPICS[idx];

  // ---- theme (shared with tracker/lecture) ----
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

  // ---- left sidebar: all patterns ----
  const nav = document.getElementById("topic-nav");
  TOPICS.forEach((t, i) => {
    const a = document.createElement("a");
    a.className = "lec-nav-item" + (t.slug === slug ? " active" : "");
    a.href = `topic.html?t=${t.slug}`;
    const label = t.title.replace(/\s*—.*$/, "");   // drop the "— common …" tail
    a.innerHTML = `<span class="lec-nav-num">${i + 1}</span><span>${label}</span>`;
    nav.appendChild(a);
  });

  // ---- main content ----
  const label = topic.title.replace(/\s*—.*$/, "");
  document.title = `${label} — Pattern Deep-Dive`;
  document.getElementById("lec-title").innerHTML =
    `<span class="lec-week-badge">Pattern</span>${label}`;
  document.getElementById("lec-body").innerHTML = topic.html;

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
        code.innerHTML = window.highlightCode(raw, HL[lang]);
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

  // ---- right TOC ----
  const tocNav = document.getElementById("toc-nav");
  (topic.toc || []).forEach((t) => {
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

  // ---- scroll spy ----
  const headings = (topic.toc || []).map((t) => document.getElementById(t.id)).filter(Boolean);
  const tocLinks = Array.from(tocNav.querySelectorAll(".toc-item"));
  function onScroll() {
    let cur = 0;
    for (let k = 0; k < headings.length; k++) {
      if (headings[k].getBoundingClientRect().top - 90 <= 0) cur = k;
    }
    tocLinks.forEach((l, k) => l.classList.toggle("active", k === cur));
  }
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ---- prev / next ----
  const prev = document.getElementById("lec-prev");
  const next = document.getElementById("lec-next");
  if (idx > 0) {
    const p = TOPICS[idx - 1];
    prev.href = `topic.html?t=${p.slug}`;
    prev.innerHTML = `← ${p.title.replace(/\s*—.*$/, "")}`;
  } else { prev.classList.add("disabled"); prev.textContent = ""; }
  if (idx < TOPICS.length - 1) {
    const n = TOPICS[idx + 1];
    next.href = `topic.html?t=${n.slug}`;
    next.innerHTML = `${n.title.replace(/\s*—.*$/, "")} →`;
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
