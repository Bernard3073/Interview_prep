/* Tiny self-contained syntax highlighter for Python and C++ (no dependencies).
   Emits <span class="tok-*"> wrappers; colors are defined in style.css using the
   VS Code Dark+ palette. Used by the practice editor's highlight overlay. */
(function () {
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const span = (cls, text) => `<span class="tok-${cls}">${esc(text)}</span>`;
  const set = (s) => new Set(s.split(/\s+/));

  // Python
  const PY_STORAGE = set("def class lambda import from as global nonlocal with async await");
  const PY_CONTROL = set("if elif else for while return break continue pass try except finally raise yield del in is not and or assert match case");
  const PY_CONST = set("True False None");

  // C++
  const CPP_CONTROL = set("if else for while do switch case default break continue return goto try catch throw");
  const CPP_KEY = set("int long short char bool float double void auto const constexpr static inline virtual override final class struct enum union namespace template typename using typedef sizeof new delete this nullptr true false unsigned signed mutable volatile friend explicit public private protected operator decltype noexcept extern thread_local register");
  const CPP_TYPE = set("std size_t string wstring vector map unordered_map set unordered_set pair queue stack deque array tuple optional shared_ptr unique_ptr weak_ptr function complex");

  function highlightCode(code, lang) {
    const py = lang === "python";
    const n = code.length;
    let out = "", i = 0;

    while (i < n) {
      const c = code[i];

      // line comments
      if (py && c === "#") {
        // C++ uses '#' for preprocessor; Python uses it for comments.
        let j = code.indexOf("\n", i); if (j < 0) j = n;
        out += span("comment", code.slice(i, j)); i = j; continue;
      }
      if (!py && c === "/" && code[i + 1] === "/") {
        let j = code.indexOf("\n", i); if (j < 0) j = n;
        out += span("comment", code.slice(i, j)); i = j; continue;
      }
      if (!py && c === "/" && code[i + 1] === "*") {
        let j = code.indexOf("*/", i + 2); j = j < 0 ? n : j + 2;
        out += span("comment", code.slice(i, j)); i = j; continue;
      }

      // C++ preprocessor (line-leading '#')
      if (!py && c === "#") {
        const ls = code.lastIndexOf("\n", i - 1) + 1;
        if (code.slice(ls, i).trim() === "") {
          let j = code.indexOf("\n", i); if (j < 0) j = n;
          const line = code.slice(i, j);
          const m = line.match(/^(#\s*[a-z_]+)(\s*)(<[^>\n]*>|"[^"\n]*")?([\s\S]*)$/);
          if (m) {
            out += span("pre", m[1]);
            out += esc(m[2] || "");
            if (m[3]) out += span("string", m[3]);
            if (m[4]) out += esc(m[4]);
          } else {
            out += span("pre", line);
          }
          i = j; continue;
        }
      }

      // strings
      if (py && (code.startsWith('"""', i) || code.startsWith("'''", i))) {
        const q = code.substr(i, 3);
        let j = code.indexOf(q, i + 3); j = j < 0 ? n : j + 3;
        out += span("string", code.slice(i, j)); i = j; continue;
      }
      if (c === '"' || c === "'") {
        let j = i + 1;
        while (j < n) {
          if (code[j] === "\\") { j += 2; continue; }
          if (code[j] === c) { j++; break; }
          if (code[j] === "\n") break; // unterminated — stop at line end
          j++;
        }
        out += span("string", code.slice(i, j)); i = j; continue;
      }

      // numbers
      if (/[0-9]/.test(c) || (c === "." && /[0-9]/.test(code[i + 1] || ""))) {
        const m = code.slice(i).match(/^(0[xX][0-9a-fA-F']+|0[bB][01']+|\d[\d']*\.?\d*(?:[eE][+-]?\d+)?[fFuUlL]*)/);
        if (m) { out += span("num", m[0]); i += m[0].length; continue; }
      }

      // identifiers / keywords
      if (/[A-Za-z_]/.test(c)) {
        let j = i + 1;
        while (j < n && /[A-Za-z0-9_]/.test(code[j])) j++;
        const word = code.slice(i, j);
        let k = j;
        while (k < n && (code[k] === " " || code[k] === "\t")) k++;
        const isCall = code[k] === "(";
        let cls = null;
        if (py) {
          if (PY_CONTROL.has(word)) cls = "kw";
          else if (PY_STORAGE.has(word)) cls = "key";
          else if (PY_CONST.has(word)) cls = "const";
          else if (isCall) cls = "fn";
        } else {
          if (CPP_CONTROL.has(word)) cls = "kw";
          else if (CPP_KEY.has(word)) cls = "key";
          else if (CPP_TYPE.has(word)) cls = "type";
          else if (isCall) cls = "fn";
        }
        out += cls ? span(cls, word) : esc(word);
        i = j; continue;
      }

      // everything else (operators, punctuation, whitespace)
      out += esc(c); i++;
    }
    return out;
  }

  window.highlightCode = highlightCode;
})();
