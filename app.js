/* Tracker logic: renders curriculum, persists progress in localStorage. */
(function () {
  const STORE_KEY = "rp_prep_progress_v1";
  const THEME_KEY = "rp_prep_theme";
  const weeksEl = document.getElementById("weeks");

  let state = loadState();

  function loadState() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; }
    catch { return {}; }
  }
  function saveState() { localStorage.setItem(STORE_KEY, JSON.stringify(state)); }

  // Problems solved in the in-site practice page (separate store).
  function solvedSet() {
    try { return JSON.parse(localStorage.getItem("rp_prep_solved")) || {}; }
    catch { return {}; }
  }

  // Stable id per checkable item
  function idFor(week, kind, i) { return `w${week}_${kind}_${i}`; }

  function isDone(id) { return !!state[id]; }
  function toggle(id, on) { state[id] = on; saveState(); update(); }

  function weekItems(w) {
    const ids = [];
    w.topics.forEach((_, i) => ids.push(idFor(w.week, "t", i)));
    w.leetcode.forEach((_, i) => ids.push(idFor(w.week, "lc", i)));
    w.robotics.forEach((_, i) => ids.push(idFor(w.week, "rb", i)));
    return ids;
  }

  function render() {
    weeksEl.innerHTML = "";
    CURRICULUM.forEach((w) => {
      const card = document.createElement("section");
      card.className = "week-card";
      card.dataset.week = w.week;

      const head = document.createElement("div");
      head.className = "week-head";
      head.innerHTML = `
        <span class="week-num">Week ${w.week}</span>
        <div style="flex:1">
          <h2>${w.title}</h2>
          <p class="week-goal">${w.goal}</p>
        </div>
        <span class="week-pct" data-pct>0%</span>
        <span class="chevron">▶</span>`;
      head.addEventListener("click", () => card.classList.toggle("open"));

      const mini = document.createElement("div");
      mini.className = "week-mini-track";
      mini.innerHTML = `<div class="week-mini-fill" data-minifill></div>`;

      const body = document.createElement("div");
      body.className = "week-body";

      // Lecture link
      const lec = document.createElement("a");
      lec.className = "lecture-link";
      lec.href = w.lecture;
      lec.innerHTML = `📖 Read lecture notes: <strong>&nbsp;${w.title}</strong>`;
      body.appendChild(lec);

      body.appendChild(sectionTitle("Lecture topics"));
      body.appendChild(itemList(w.topics.map((t, i) => ({
        id: idFor(w.week, "t", i),
        html: `<span class="item-label">${t}</span>`,
      }))));

      if (w.leetcode.length) {
      body.appendChild(sectionTitle("LeetCode practice"));
      body.appendChild(itemList(w.leetcode.map((p, i) => {
        // In-site problems (have a pid) open the practice page; others link out.
        const link = p.pid
          ? `<a href="practice.html?p=${p.pid}">${p.name}</a> <span class="solve-chip">▶ solve in-site</span>`
          : `<a href="${p.url}" target="_blank">${p.name} ↗</a>`;
        const solvedBadge = p.pid && solvedSet()[p.pid] ? `<span class="mini-solved">✓</span>` : "";
        return {
          id: idFor(w.week, "lc", i),
          html: `<span class="item-label">${solvedBadge}${link}</span>
                 <span class="tag">${p.tag}</span>
                 <span class="badge ${p.diff}">${p.diff}</span>`,
        };
      })));
      }

      if (w.robotics.length) {
      body.appendChild(sectionTitle("Robotics / perception coding"));
      body.appendChild(itemList(w.robotics.map((p, i) => {
        const link = p.pid
          ? `<a href="practice.html?p=${p.pid}">${p.name}</a> <span class="solve-chip">▶ solve in-site</span>`
          : `<a href="${p.file}" target="_blank">${p.name}</a>`;
        const ref = p.pid && p.file ? ` <a class="ref-link" href="${p.file}" target="_blank" title="full numpy reference">📄 .py</a>` : "";
        const solvedBadge = p.pid && solvedSet()[p.pid] ? `<span class="mini-solved">✓</span>` : "";
        return {
          id: idFor(w.week, "rb", i),
          html: `<span class="item-label">${solvedBadge}${link}${ref}</span>
                 ${p.tag ? `<span class="tag">${p.tag}</span>` : ""}
                 ${p.diff ? `<span class="badge ${p.diff}">${p.diff}</span>` : ""}`,
        };
      })));
      }

      card.append(head, mini, body);
      weeksEl.appendChild(card);
    });
    if (weeksEl.firstChild) weeksEl.firstChild.classList.add("open");
  }

  function sectionTitle(txt) {
    const d = document.createElement("div");
    d.className = "section-title";
    d.textContent = txt;
    return d;
  }

  function itemList(items) {
    const ul = document.createElement("ul");
    ul.className = "items";
    items.forEach(({ id, html }) => {
      const li = document.createElement("li");
      li.className = "item";
      li.dataset.id = id;
      const cb = document.createElement("input");
      cb.type = "checkbox"; cb.checked = isDone(id);
      cb.addEventListener("change", () => toggle(id, cb.checked));
      li.appendChild(cb);
      const span = document.createElement("span");
      span.style.flex = "1";
      span.style.display = "flex";
      span.style.gap = "10px";
      span.style.alignItems = "center";
      span.innerHTML = html;
      li.appendChild(span);
      ul.appendChild(li);
    });
    return ul;
  }

  function update() {
    let total = 0, done = 0, weeksComplete = 0;
    CURRICULUM.forEach((w) => {
      const ids = weekItems(w);
      const wd = ids.filter(isDone).length;
      total += ids.length; done += wd;
      if (wd === ids.length && ids.length > 0) weeksComplete++;
      const card = weeksEl.querySelector(`.week-card[data-week="${w.week}"]`);
      if (card) {
        const pct = ids.length ? Math.round((wd / ids.length) * 100) : 0;
        card.querySelector("[data-pct]").textContent = pct + "%";
        card.querySelector("[data-minifill]").style.width = pct + "%";
      }
    });
    // Per-item visual state
    weeksEl.querySelectorAll("li.item").forEach((li) => {
      li.classList.toggle("checked", isDone(li.dataset.id));
    });
    const pct = total ? Math.round((done / total) * 100) : 0;
    document.getElementById("overall-pct").textContent = pct + "%";
    document.getElementById("overall-fill").style.width = pct + "%";
    document.getElementById("done-count").textContent = done;
    document.getElementById("total-count").textContent = total;
    document.getElementById("streak").textContent = weeksComplete;
  }

  // Theme
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    document.getElementById("theme-btn").textContent = t === "light" ? "☀️" : "🌙";
    localStorage.setItem(THEME_KEY, t);
  }
  document.getElementById("theme-btn").addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
    applyTheme(cur);
  });
  document.getElementById("reset-btn").addEventListener("click", () => {
    if (confirm("Reset ALL progress? This cannot be undone.")) {
      state = {}; saveState();
      weeksEl.querySelectorAll("input[type=checkbox]").forEach((c) => (c.checked = false));
      update();
    }
  });

  applyTheme(localStorage.getItem(THEME_KEY) || "dark");
  render();
  update();
})();
