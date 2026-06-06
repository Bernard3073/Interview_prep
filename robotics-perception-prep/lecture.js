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
