/* Build per-structure subpages: study-materials/data-structure-topics/*.md -> ds-topics-data.js
   Reuses the lecture markdown renderer and adds a ":::solution [title]" ... ":::" block
   that pairs a ```python and a ```cpp fence into a Python/C++ tabbed solution widget.
   Run: node build_ds_topics.cjs   */
const fs = require("fs");
const path = require("path");

const SRC = path.join(__dirname, "study-materials", "data-structure-topics");
const files = fs.readdirSync(SRC).filter(f => /^\d\d-.*\.md$/.test(f)).sort();

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function inline(text) {
  const parts = text.split(/(`[^`]+`)/);
  return parts.map(p => {
    if (p.length >= 2 && p[0] === "`" && p[p.length - 1] === "`") {
      return `<code>${esc(p.slice(1, -1))}</code>`;
    }
    let s = esc(p);
    s = s.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) => {
      if (src.startsWith("images/")) src = "study-materials/" + src;
      return `<img class="lec-img" src="${src}" alt="${alt}" loading="lazy">`;
    });
    s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, t, u) => `<a href="${u}" target="_blank" rel="noopener">${t}</a>`);
    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    return s;
  }).join("");
}

let slugCount = {};
function slug(text) {
  let base = text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  if (slugCount[base] == null) { slugCount[base] = 0; return base; }
  slugCount[base]++; return `${base}-${slugCount[base]}`;
}

// Pull a single ```lang fenced block out of `lines` starting at index i.
// Returns { code, next } or null if the line isn't a matching fence.
function grabFence(lines, i, wantLang) {
  if (!lines[i] || !lines[i].trim().startsWith("```")) return null;
  const lang = lines[i].trim().slice(3).trim().toLowerCase();
  if (wantLang && lang !== wantLang) return null;
  const buf = []; let j = i + 1;
  while (j < lines.length && !lines[j].trim().startsWith("```")) { buf.push(lines[j]); j++; }
  return { lang, code: buf.join("\n"), next: j + 1 };
}

function solPre(lang, code, hidden) {
  return `<div class="sol-pane" data-lang="${lang}"${hidden ? " hidden" : ""}>` +
    `<pre class="lec-pre" data-lang="${lang}"><code>${esc(code)}</code></pre></div>`;
}

function renderBlocks(lines, toc, titleRef) {
  const out = [];
  let i = 0;
  const isBreak = (ln) => /^(#{1,4}\s|>|\s*[-*]\s|\d+\.\s|```|\||\?\?\?\s|:::)/.test(ln) || /^-{3,}$/.test(ln.trim());

  while (i < lines.length) {
    let line = lines[i];
    if (line.trim() === "") { i++; continue; }

    // solution tabs: ":::solution [optional title]" ... two code fences ... ":::"
    if (/^:::solution\b/.test(line.trim())) {
      const title = line.trim().replace(/^:::solution\s*/, "").trim();
      i++;
      // skip blanks, grab python then cpp (order-independent)
      const langs = {};
      let guard = 0;
      while (i < lines.length && !/^:::\s*$/.test(lines[i].trim()) && guard++ < 10) {
        if (lines[i].trim() === "") { i++; continue; }
        const g = grabFence(lines, i);
        if (!g) { i++; continue; }
        langs[g.lang === "py" ? "python" : (g.lang === "c++" ? "cpp" : g.lang)] = g.code;
        i = g.next;
      }
      if (i < lines.length && /^:::\s*$/.test(lines[i].trim())) i++;   // consume closing :::
      const hasPy = langs.python != null, hasCpp = langs.cpp != null;
      let html = `<div class="sol">`;
      if (title) html += `<div class="sol-title">${inline(title)}</div>`;
      html += `<div class="sol-tabs" role="tablist">` +
        (hasPy ? `<button class="sol-tab active" data-lang="python" type="button">Python</button>` : "") +
        (hasCpp ? `<button class="sol-tab${hasPy ? "" : " active"}" data-lang="cpp" type="button">C++</button>` : "") +
        `</div>`;
      if (hasPy) html += solPre("python", langs.python, false);
      if (hasCpp) html += solPre("cpp", langs.cpp, hasPy);
      html += `</div>`;
      out.push(html);
      continue;
    }

    // Q&A collapsible
    if (line.startsWith("??? ")) {
      const q = line.slice(4).trim();
      i++;
      const ans = [];
      while (i < lines.length && !lines[i].startsWith("??? ") &&
             !/^#{1,4}\s/.test(lines[i]) && !/^-{3,}$/.test(lines[i].trim())) {
        ans.push(lines[i]); i++;
      }
      const body = renderBlocks(ans, null, {});
      out.push(`<details class="qa"><summary>${inline(q)}</summary><div class="qa-body">${body}</div></details>`);
      continue;
    }

    // code fence
    if (line.trim().startsWith("```")) {
      const lang = line.trim().slice(3).trim().toLowerCase();
      i++;
      const buf = [];
      while (i < lines.length && !lines[i].trim().startsWith("```")) { buf.push(lines[i]); i++; }
      i++;
      const langAttr = lang ? ` data-lang="${esc(lang)}"` : "";
      out.push(`<pre class="lec-pre"${langAttr}><code>${esc(buf.join("\n"))}</code></pre>`);
      continue;
    }

    // heading
    let h = line.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      const level = h[1].length, txt = h[2].trim();
      if (level === 1) { if (titleRef && !titleRef.value) titleRef.value = txt; i++; continue; }
      const id = slug(txt);
      if (toc && (level === 2 || level === 3)) toc.push({ level, txt, id });
      out.push(`<h${level} id="${id}">${inline(txt)}</h${level}>`);
      i++; continue;
    }

    // horizontal rule
    if (/^-{3,}$/.test(line.trim()) && !line.includes("|")) { out.push("<hr>"); i++; continue; }

    // table
    if (line.trim().startsWith("|") && i + 1 < lines.length &&
        /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1]) && lines[i + 1].includes("-")) {
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) { rows.push(lines[i]); i++; }
      const cells = r => r.trim().replace(/^\||\|$/g, "").split("|").map(c => c.trim());
      const header = cells(rows[0]);
      const body = rows.slice(2).map(cells);
      let t = '<div class="lec-table-wrap"><table class="lec-table"><thead><tr>';
      t += header.map(c => `<th>${inline(c)}</th>`).join("") + "</tr></thead><tbody>";
      for (const row of body) t += "<tr>" + row.map(c => `<td>${inline(c)}</td>`).join("") + "</tr>";
      t += "</tbody></table></div>";
      out.push(t); continue;
    }

    // blockquote
    if (line.trim().startsWith(">")) {
      const buf = [];
      while (i < lines.length && lines[i].trim().startsWith(">")) { buf.push(lines[i].replace(/^\s*>\s?/, "")); i++; }
      out.push(`<blockquote class="lec-callout">${inline(buf.join(" "))}</blockquote>`);
      continue;
    }

    // ordered list
    if (/^\d+\.\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i])) {
        let item = lines[i].replace(/^\d+\.\s+/, ""); i++;
        while (i < lines.length && /^\s+\S/.test(lines[i]) && !/^\s*\d+\.\s+/.test(lines[i]) && !/^\s*[-*]\s+/.test(lines[i])) {
          item += " " + lines[i].trim(); i++;
        }
        items.push(item);
      }
      out.push("<ol>" + items.map(t => `<li>${inline(t)}</li>`).join("") + "</ol>");
      continue;
    }

    // unordered list (one nesting level)
    if (/^\s*[-*]\s+/.test(line)) {
      const top = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        const indent = lines[i].match(/^(\s*)/)[1].length;
        let item = lines[i].replace(/^\s*[-*]\s+/, ""); i++;
        while (i < lines.length && /^\s+\S/.test(lines[i]) && !/^\s*[-*]\s+/.test(lines[i])) { item += " " + lines[i].trim(); i++; }
        const children = [];
        while (i < lines.length && /^\s{2,}[-*]\s+/.test(lines[i]) && lines[i].match(/^(\s*)/)[1].length > indent) {
          let c = lines[i].replace(/^\s*[-*]\s+/, ""); i++;
          while (i < lines.length && /^\s+\S/.test(lines[i]) && !/^\s*[-*]\s+/.test(lines[i])) { c += " " + lines[i].trim(); i++; }
          children.push(c);
        }
        top.push({ item, children });
      }
      let html = "<ul>";
      for (const { item, children } of top) {
        html += `<li>${inline(item)}`;
        if (children.length) html += "<ul>" + children.map(c => `<li>${inline(c)}</li>`).join("") + "</ul>";
        html += "</li>";
      }
      out.push(html + "</ul>"); continue;
    }

    // paragraph
    const buf = [line]; i++;
    while (i < lines.length && lines[i].trim() !== "" && !isBreak(lines[i])) { buf.push(lines[i]); i++; }
    out.push(`<p>${inline(buf.join(" "))}</p>`);
  }
  return out.join("\n");
}

function convert(md) {
  slugCount = {};
  const lines = md.replace(/\r\n/g, "\n").split("\n");
  const toc = [];
  const titleRef = {};
  const html = renderBlocks(lines, toc, titleRef);
  return { title: titleRef.value, html, toc };
}

const topics = [];
for (const f of files) {
  const s = f.replace(/^\d\d-/, "").replace(/\.md$/, "");
  const md = fs.readFileSync(path.join(SRC, f), "utf8");
  const { title, html, toc } = convert(md);
  topics.push({ slug: s, title, html, toc });
  console.log(`converted ${s}: "${title}" (${toc.length} toc, ${(html.match(/sol-tabs/g) || []).length} solutions)`);
}

const banner = "/* AUTO-GENERATED from study-materials/data-structure-topics/*.md by build_ds_topics.cjs.\n" +
               "   Edit the source there and rebuild: node build_ds_topics.cjs */\n";
fs.writeFileSync(path.join(__dirname, "ds-topics-data.js"),
  banner + "const DS_TOPICS = " + JSON.stringify(topics, null, 2) + ";\n");
console.log(`wrote ds-topics-data.js (${topics.length} topics)`);
