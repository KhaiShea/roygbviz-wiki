// Small behaviours in the style of GitHub Docs: mobile menu, "In this article", heading links, copy buttons, search.
(() => {
  const base = document.documentElement.dataset.baseurl || "";

  // ---------- light and dark ----------
  // Figures are <picture> elements with a dark <source> chosen by the system setting. Point each source at the
  // site's mode instead, so the figures follow the theme menu too. The Markdown stays as it is for GitHub.
  const syncFigures = (mode) => {
    document.querySelectorAll("picture source[media*='prefers-color-scheme']").forEach((src) => {
      if (!src.dataset.media) src.dataset.media = src.media;
      const forDark = src.dataset.media.includes("dark");
      src.media = (mode === "dark") === forDark ? "all" : "not all";
    });
  };
  syncFigures(document.documentElement.getAttribute("data-color-mode"));
  document.addEventListener("rv-theme", (e) => syncFigures(e.detail.mode));

  const themeMenu = document.querySelector(".theme-menu");
  if (themeMenu && window.rvTheme) {
    const choices = themeMenu.querySelectorAll("[data-theme-choice]");
    const mark = (pref) => choices.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.themeChoice === pref)));
    mark(window.rvTheme.get());
    choices.forEach((b) => b.addEventListener("click", () => {
      window.rvTheme.set(b.dataset.themeChoice);
      mark(b.dataset.themeChoice);
      themeMenu.open = false;
    }));
    document.addEventListener("click", (e) => { if (!themeMenu.contains(e.target)) themeMenu.open = false; });
    themeMenu.addEventListener("keydown", (e) => { if (e.key === "Escape") themeMenu.open = false; });
  }

  // ---------- enlarge images ----------
  // Every image in a page gets a small button (and a zoom cursor) that opens it in a dialog. The dialog shows the
  // image's currentSrc, so it matches whichever light or dark version is on screen.
  const icon = (d) => `<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${d}"/></svg>`;
  const pageImages = document.querySelectorAll(".markdown-body img");
  if (pageImages.length) {
    const box = document.createElement("dialog");
    box.className = "lightbox";
    box.setAttribute("aria-label", "Enlarged image");
    box.innerHTML = `<img alt=""><button type="button" class="lightbox-close" aria-label="Close">${icon("M4 4l8 8M12 4l-8 8")}</button>`;
    document.body.appendChild(box);
    const big = box.querySelector("img");
    let opener = null;

    const open = (img, from) => {
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      opener = from;
      box.showModal();
    };
    box.addEventListener("click", (e) => { if (e.target !== big) box.close(); }); // backdrop or close button
    box.addEventListener("close", () => { big.removeAttribute("src"); if (opener) opener.focus(); });

    pageImages.forEach((img) => {
      const target = img.closest("picture") || img;
      const wrap = document.createElement("span");
      wrap.className = "zoomable";
      target.before(wrap);
      wrap.appendChild(target);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "zoom-btn";
      btn.setAttribute("aria-label", "Enlarge image");
      btn.title = "Enlarge";
      btn.innerHTML = icon("M10 2h4v4M6 14H2v-4M14 2 9 7M2 14l5-5");
      wrap.appendChild(btn);
      btn.addEventListener("click", () => open(img, btn));
      img.addEventListener("click", () => open(img, btn));
    });
  }

  // ---------- mobile menu ----------
  const toggle = document.querySelector(".nav-toggle");
  const sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", () => {
      const open = sidebar.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }

  // ---------- OS switchers ----------
  // In the Markdown, each OS is an h3 inside <div class="os-tabs">, which reads fine on GitHub. Here the headings
  // become tabs. The first visit picks the reader's OS; after that, their last choice wins, on every page.
  const osOf = (text) => (/windows/i.test(text) ? "windows" : /mac/i.test(text) ? "macos" : "linux");
  const detectOS = () => {
    const p = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || "";
    return /win/i.test(p) ? "windows" : /mac/i.test(p) ? "macos" : "linux";
  };
  let chosenOS = detectOS();
  try { chosenOS = localStorage.getItem("rv-os") || chosenOS; } catch {}
  const osGroups = [];

  document.querySelectorAll(".markdown-body .os-tabs").forEach((box, g) => {
    const heads = [...box.querySelectorAll(":scope > h3")];
    if (heads.length < 2) return;
    const bar = document.createElement("div");
    bar.className = "os-tabs-bar";
    bar.setAttribute("role", "tablist");
    bar.setAttribute("aria-label", "Operating system");
    const tabs = heads.map((h, i) => {
      const panel = document.createElement("div");
      panel.className = "os-tabs-panel";
      panel.id = `os-${g}-${i}`;
      panel.setAttribute("role", "tabpanel");
      let next = h.nextElementSibling;
      while (next && next.tagName !== "H3") {
        const after = next.nextElementSibling;
        panel.appendChild(next);
        next = after;
      }
      const tab = document.createElement("button");
      tab.type = "button";
      tab.id = `${panel.id}-tab`;
      tab.textContent = h.textContent.trim();
      tab.dataset.os = osOf(h.textContent);
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", panel.id);
      panel.setAttribute("aria-labelledby", tab.id);
      bar.appendChild(tab);
      h.replaceWith(panel);
      return { tab, panel };
    });
    box.prepend(bar);
    osGroups.push(tabs);

    bar.addEventListener("click", (e) => {
      const tab = e.target.closest("[role=tab]");
      if (tab) showOS(tab.dataset.os, true);
    });
    bar.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      const i = tabs.findIndex((t) => t.tab === document.activeElement);
      const next = tabs[(i + (e.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length].tab;
      showOS(next.dataset.os, true);
      next.focus();
    });
  });

  function showOS(os, remember) {
    osGroups.forEach((tabs) => {
      const pick = tabs.find((t) => t.tab.dataset.os === os) ? os : tabs[0].tab.dataset.os;
      tabs.forEach(({ tab, panel }) => {
        const on = tab.dataset.os === pick;
        tab.setAttribute("aria-selected", String(on));
        tab.tabIndex = on ? 0 : -1;
        panel.hidden = !on;
      });
    });
    if (remember) {
      try { localStorage.setItem("rv-os", os); } catch {}
    }
  }
  if (osGroups.length) showOS(chosenOS, false);

  // ---------- "In this article" and heading links ----------
  const article = document.querySelector(".markdown-body");
  const tocList = document.getElementById("toc-list");
  if (article) {
    const heads = [...article.querySelectorAll("h2[id], h3[id]")];
    heads.forEach((h) => {
      const a = document.createElement("a");
      a.className = "anchor-link";
      a.href = `#${h.id}`;
      a.setAttribute("aria-label", `Link to ${h.textContent}`);
      a.textContent = "#";
      h.appendChild(a);
    });
    const h2s = heads.filter((h) => h.tagName === "H2");
    if (tocList) {
      if (h2s.length < 2) {
        tocList.closest(".toc").hidden = true;
      } else {
        const links = h2s.map((h) => {
          const li = document.createElement("li");
          const a = document.createElement("a");
          a.href = `#${h.id}`;
          a.textContent = h.firstChild.textContent.trim();
          li.appendChild(a);
          tocList.appendChild(li);
          return a;
        });
        // highlight the section you're reading
        const spy = new IntersectionObserver((entries) => {
          entries.forEach((e) => {
            if (!e.isIntersecting) return;
            links.forEach((a) => a.classList.toggle("is-active", a.hash === `#${e.target.id}`));
          });
        }, { rootMargin: "-80px 0px -70% 0px" });
        h2s.forEach((h) => spy.observe(h));

        // wide screens: a column on the right; narrow screens: under the intro paragraph
        const toc = tocList.closest(".toc");
        const home = toc.parentElement;
        const lead = article.querySelector(":scope > h1:first-child + p") || article.querySelector(":scope > h1:first-child");
        const wide = window.matchMedia("(min-width: 1280px)");
        const place = () => (wide.matches ? home.insertBefore(toc, article) : lead && lead.after(toc));
        wide.addEventListener("change", place);
        place();
      }
    }
  }

  // ---------- copy buttons ----------
  // Rouge wraps the languages it knows in div.highlighter-rouge. Others (fish, say) come out as a bare <pre>, so
  // give those a wrapper too, and every code block gets a button.
  document.querySelectorAll(".markdown-body pre").forEach((pre) => {
    if (pre.closest("div.highlighter-rouge")) return;
    const wrap = document.createElement("div");
    wrap.className = "highlighter-rouge";
    pre.before(wrap);
    wrap.appendChild(pre);
  });
  document.querySelectorAll(".markdown-body div.highlighter-rouge").forEach((block) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-sm copy-btn";
    btn.textContent = "Copy";
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(block.querySelector("pre").innerText);
        btn.textContent = "Copied";
      } catch {
        btn.textContent = "Couldn't copy";
      }
      setTimeout(() => { btn.textContent = "Copy"; }, 1500);
    });
    block.appendChild(btn);
  });

  // ---------- search ----------
  let index = null;
  const load = () => index
    ? Promise.resolve(index)
    : fetch(`${base}/search.json`).then((r) => r.json()).then((d) => (index = d));

  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const markTerms = (s, terms) => terms.reduce(
    (out, t) => out.replace(new RegExp(`(${t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi"), "<mark>$1</mark>"), esc(s));

  function search(q) {
    const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    return index
      .map((p) => {
        const title = p.title.toLowerCase();
        const text = p.text.toLowerCase();
        if (!terms.every((t) => title.includes(t) || text.includes(t))) return null;
        const score = terms.reduce((s, t) => s + (title.includes(t) ? 10 : 0) + Math.min(text.split(t).length - 1, 5), 0);
        const at = Math.max(0, text.indexOf(terms[0]) - 40);
        const snippet = (at ? "…" : "") + p.text.slice(at, at + 140).trim() + "…";
        return { ...p, score, snippet };
      })
      .filter(Boolean)
      .sort((a, b) => b.score - a.score)
      .slice(0, 8);
  }

  document.querySelectorAll("[data-search]").forEach((form) => {
    const input = form.querySelector("input");
    const box = form.querySelector(".search-results");
    let active = -1;

    const close = () => { box.hidden = true; active = -1; };
    const select = (i) => {
      const items = [...box.querySelectorAll("a")];
      if (!items.length) return;
      active = (i + items.length) % items.length;
      items.forEach((a, k) => a.setAttribute("aria-selected", String(k === active)));
      items[active].scrollIntoView({ block: "nearest" });
    };

    input.addEventListener("focus", load, { once: true });
    input.addEventListener("input", async () => {
      const q = input.value.trim();
      if (!q) return close();
      await load();
      const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      const hits = search(q);
      box.innerHTML = hits.length
        ? hits.map((h) => `<li><a href="${h.url}" role="option"><strong>${markTerms(h.title, terms)}</strong><small>${markTerms(h.snippet, terms)}</small></a></li>`).join("")
        : `<li class="empty">Nothing found for "${esc(q)}"</li>`;
      box.hidden = false;
      active = -1;
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") { e.preventDefault(); select(active + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); select(active - 1); }
      else if (e.key === "Escape") { close(); input.blur(); }
      else if (e.key === "Enter") {
        const items = box.querySelectorAll("a");
        const target = items[active >= 0 ? active : 0];
        if (target) window.location.href = target.href;
      }
    });
    document.addEventListener("click", (e) => { if (!form.contains(e.target)) close(); });
  });

  // "/" jumps to search, like on GitHub
  document.addEventListener("keydown", (e) => {
    if (e.key !== "/" || e.target.closest("input, textarea")) return;
    const input = document.querySelector("[data-search] input");
    if (input) { e.preventDefault(); input.focus(); }
  });
})();
