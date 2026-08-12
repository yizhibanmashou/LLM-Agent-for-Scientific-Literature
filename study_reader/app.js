const DATASET_URL = "./data/generated/study_dataset.json";

const STATE = {
  dataset: null,
  studyBookId: "",
  studyChapterId: "",
  currentChapterId: "",
  activeAnchor: "",
  returnPoint: null,
  openPicker: "",
  markdownCache: new Map(),
  chapterDataCache: new Map(),
};

document.addEventListener("DOMContentLoaded", () => {
  initialize().catch((error) => {
    console.error(error);
    setStatus(`无法加载 Study Reader: ${error.message}`);
  });
});

async function initialize() {
  STATE.dataset = await fetchJson(DATASET_URL);
  bindControls();
  renderBookOptions();
  renderChapterOptions();
  const defaultChapter = STATE.dataset.default_chapter || STATE.dataset.chapters?.[0]?.id || "";
  await openStudyChapter(defaultChapter);
}

function bindControls() {
  document.getElementById("bookSelect").addEventListener("change", async (event) => {
    const bookId = event.target.value;
    const book = bookById(bookId);
    const target = book?.default_chapter || chaptersForBook(bookId)[0]?.id || STATE.dataset.default_chapter || "";
    await openStudyChapter(target);
  });

  document.getElementById("chapterSelect").addEventListener("change", async (event) => {
    await openStudyChapter(event.target.value);
  });

  document.getElementById("bookPickerButton").addEventListener("click", (event) => {
    event.stopPropagation();
    togglePicker("book");
  });

  document.getElementById("chapterPickerButton").addEventListener("click", (event) => {
    event.stopPropagation();
    togglePicker("chapter");
  });

  document.getElementById("bookPickerMenu").addEventListener("click", async (event) => {
    const option = event.target.closest("[data-book-id]");
    if (!option) return;
    closePicker();
    const bookId = option.dataset.bookId;
    const book = bookById(bookId);
    const target = book?.default_chapter || chaptersForBook(bookId)[0]?.id || STATE.dataset.default_chapter || "";
    if (target) await openStudyChapter(target);
  });

  document.getElementById("chapterPickerMenu").addEventListener("click", async (event) => {
    const option = event.target.closest("[data-chapter-id]");
    if (!option) return;
    closePicker();
    await openStudyChapter(option.dataset.chapterId);
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".smart-picker")) closePicker();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closePicker();
  });

  document.getElementById("returnButton").addEventListener("click", async () => {
    if (!STATE.returnPoint) return;
    const target = STATE.returnPoint;
    STATE.returnPoint = null;
    STATE.studyBookId = target.studyBookId || bookIdFromChapterId(target.studyChapterId || target.chapterId);
    STATE.studyChapterId = target.studyChapterId || target.chapterId;
    await openChapter(target.chapterId, target.anchor, { restoreScrollTop: target.scrollTop });
  });

  const root = document.getElementById("markdownRoot");
  root.addEventListener("click", async (event) => {
    const jump = event.target.closest("[data-jump-chapter]");
    if (jump) {
      event.preventDefault();
      await jumpToReference(jump.dataset.jumpChapter, jump.dataset.jumpAnchor || "");
      return;
    }
    const heading = event.target.closest("[data-section-anchor]");
    if (heading) {
      STATE.activeAnchor = heading.dataset.sectionAnchor || "";
      updatePrerequisiteSelection();
    }
  });
  root.addEventListener("scroll", updateActiveSectionFromScroll);

  const rail = document.getElementById("sectionRail");
  rail.addEventListener("click", (event) => {
    const button = event.target.closest("[data-section-nav-anchor]");
    if (!button) return;
    moveReaderToAnchor(button.dataset.sectionNavAnchor || "");
  });
  rail.addEventListener("mouseover", (event) => {
    const button = event.target.closest("[data-section-nav-anchor]");
    if (button) showRailTooltip(button);
  });
  rail.addEventListener("mousemove", (event) => {
    const button = event.target.closest("[data-section-nav-anchor]");
    if (button) positionRailTooltip(button);
  });
  rail.addEventListener("mouseout", (event) => {
    if (!event.relatedTarget || !event.currentTarget.contains(event.relatedTarget)) hideRailTooltip();
  });
  rail.addEventListener("focusin", (event) => {
    const button = event.target.closest("[data-section-nav-anchor]");
    if (button) showRailTooltip(button);
  });
  rail.addEventListener("focusout", hideRailTooltip);

  document.getElementById("conceptList").addEventListener("click", async (event) => {
    const source = event.target.closest("[data-source-chapter]");
    if (source) {
      await jumpToReference(source.dataset.sourceChapter, source.dataset.sourceAnchor || "");
      return;
    }
    const study = event.target.closest("[data-study-anchor]");
    if (study) {
      await jumpToStudyAnchor(study.dataset.studyAnchor || "");
    }
  });
}

async function openStudyChapter(chapterId, anchor = "") {
  const chapter = chapterById(chapterId);
  STATE.studyBookId = chapterBookId(chapter) || bookIdFromChapterId(chapterId);
  STATE.studyChapterId = chapterId;
  STATE.returnPoint = null;
  await openChapter(chapterId, anchor);
}

async function openChapter(chapterId, anchor = "", options = {}) {
  const chapter = chapterById(chapterId);
  if (!chapter) throw new Error(`Unknown chapter: ${chapterId}`);
  await ensureChapterData(chapter);

  STATE.currentChapterId = chapter.id;
  STATE.activeAnchor = anchor || "";
  if (!STATE.studyBookId) STATE.studyBookId = chapterBookId(chapter) || bookIdFromChapterId(chapter.id);
  renderChapterOptions();
  document.getElementById("bookSelect").value = STATE.studyBookId || chapterBookId(chapter) || "";
  document.getElementById("chapterSelect").value = STATE.studyChapterId || chapter.id;
  updatePickerDisplays();
  document.getElementById("chapterTitle").textContent = chapter.label;
  document.getElementById("chapterMeta").textContent = chapterMetaText(chapter);
  updateHeaderContext(chapter);
  setStatus("正在载入 Markdown...");

  const markdown = await fetchText(chapter.markdown_path);
  const root = document.getElementById("markdownRoot");
  root.innerHTML = renderMarkdown(markdown);
  appendGeneratedAssets(root);
  renderSectionRail();
  renderMath(root);
  setStatus(sourceModeStatus());

  if (anchor) {
    window.setTimeout(() => moveReaderToAnchor(anchor), 20);
  } else if (typeof options.restoreScrollTop === "number") {
    root.scrollTop = options.restoreScrollTop;
  } else {
    root.scrollTop = 0;
  }
  updateActiveSectionFromScroll();

  renderPrerequisites();
  updateReturnButton();
  updateSectionRailSelection();
}

function chapterMetaText(chapter) {
  const base = `${chapter.section_count || 0} sections · ${chapter.asset_count || 0} bodies`;
  if (isSourceMode()) return `来源查看 · ${base}`;
  return `${base} · ${chapter.prerequisite_count || 0} prerequisites`;
}

function updateHeaderContext(chapter) {
  const book = bookById(STATE.studyBookId || chapterBookId(chapter));
  const mode = isSourceMode() ? `来源：${chapterLabel(STATE.currentChapterId)}` : `当前：${chapterLabel(STATE.studyChapterId || chapter.id)}`;
  document.getElementById("bookContext").textContent = `${book?.label || chapterBookId(chapter) || ""} · ${mode}`;
}

function sourceModeStatus() {
  if (!isSourceMode()) return "";
  return `正在查看 ${chapterLabel(STATE.studyChapterId)} 的前置来源，可返回原文位置。`;
}

function isSourceMode() {
  return Boolean(STATE.studyChapterId && STATE.currentChapterId && STATE.currentChapterId !== STATE.studyChapterId);
}

async function fetchJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json();
}

async function fetchText(path) {
  if (STATE.markdownCache.has(path)) return STATE.markdownCache.get(path);
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  const text = await response.text();
  STATE.markdownCache.set(path, text);
  return text;
}

function renderBookOptions() {
  const select = document.getElementById("bookSelect");
  const books = STATE.dataset.books || [];
  select.innerHTML = books.map((book) => `<option value="${escapeHtml(book.id)}">${escapeHtml(book.label || book.id)}</option>`).join("");
  document.getElementById("bookPickerMenu").innerHTML = books.map(renderBookPickerOption).join("");
  updatePickerDisplays();
}

function renderChapterOptions() {
  const select = document.getElementById("chapterSelect");
  const bookId = STATE.studyBookId || STATE.dataset.default_book || bookIdFromChapterId(STATE.dataset.default_chapter || "");
  const bookChapters = chaptersForBook(bookId);
  const chapters = bookChapters.filter((chapter) => chapter.kind === "chapter");
  const appendices = bookChapters.filter((chapter) => chapter.kind === "appendix");
  select.innerHTML = [
    chapters.length ? `<optgroup label="Chapters">${chapters.map(renderChapterOption).join("")}</optgroup>` : "",
    appendices.length ? `<optgroup label="Appendices">${appendices.map(renderChapterOption).join("")}</optgroup>` : "",
  ].join("");
  document.getElementById("chapterPickerMenu").innerHTML = [
    chapters.length ? `<div class="picker-section-title">Chapters</div>${chapters.map(renderChapterPickerOption).join("")}` : "",
    appendices.length ? `<div class="picker-section-title">Appendices</div>${appendices.map(renderChapterPickerOption).join("")}` : "",
  ].join("");
  updatePickerDisplays();
}

function renderChapterOption(chapter) {
  return `<option value="${escapeHtml(chapter.id)}">${escapeHtml(chapter.label)}</option>`;
}

function renderBookPickerOption(book) {
  const count = chaptersForBook(book.id).length;
  const selected = book.id === STATE.studyBookId;
  const defaultLabel = chapterLabel(book.default_chapter || "");
  return `
    <button type="button" class="picker-option" role="option" aria-selected="${selected ? "true" : "false"}" data-book-id="${escapeAttribute(book.id)}">
      <span class="picker-option-title">${escapeHtml(book.label || book.id)}</span>
      <span class="picker-option-note">${count} 个章节/附录${defaultLabel ? ` · 默认 ${escapeHtml(defaultLabel)}` : ""}</span>
    </button>
  `;
}

function renderChapterPickerOption(chapter) {
  const selected = chapter.id === STATE.studyChapterId;
  const note = `${chapter.section_count || 0} 小节 · ${chapter.prerequisite_count || 0} 前置`;
  return `
    <button type="button" class="picker-option" role="option" aria-selected="${selected ? "true" : "false"}" data-chapter-id="${escapeAttribute(chapter.id)}">
      <span class="picker-option-title">${escapeHtml(chapter.label)}</span>
      <span class="picker-option-note">${escapeHtml(note)}</span>
    </button>
  `;
}

function togglePicker(type) {
  if (STATE.openPicker === type) {
    closePicker();
    return;
  }
  closePicker();
  STATE.openPicker = type;
  const picker = document.querySelector(`.smart-picker[data-picker="${type}"]`);
  const button = document.getElementById(`${type}PickerButton`);
  const menu = document.getElementById(`${type}PickerMenu`);
  picker?.classList.add("is-open");
  button?.setAttribute("aria-expanded", "true");
  if (menu) menu.hidden = false;
}

function closePicker() {
  if (!STATE.openPicker) return;
  document.querySelectorAll(".smart-picker.is-open").forEach((picker) => picker.classList.remove("is-open"));
  document.querySelectorAll(".picker-button[aria-expanded='true']").forEach((button) => button.setAttribute("aria-expanded", "false"));
  document.querySelectorAll(".picker-menu").forEach((menu) => {
    menu.hidden = true;
  });
  STATE.openPicker = "";
}

function updatePickerDisplays() {
  const book = bookById(STATE.studyBookId);
  const studyChapter = chapterById(STATE.studyChapterId);
  const currentChapter = chapterById(STATE.currentChapterId);
  const bookChapters = chaptersForBook(STATE.studyBookId);
  const chapterMeta = studyChapter
    ? `${studyChapter.section_count || 0} 小节 · ${studyChapter.prerequisite_count || 0} 前置`
    : "";

  document.getElementById("bookPickerValue").textContent = book?.label || STATE.studyBookId || "选择教材";
  document.getElementById("bookPickerMeta").textContent = bookChapters.length ? `${bookChapters.length} 个章节/附录` : "";
  document.getElementById("chapterPickerValue").textContent = studyChapter?.label || "选择章节";
  document.getElementById("chapterPickerMeta").textContent = isSourceMode() && currentChapter
    ? `正在查看来源：${currentChapter.label}`
    : chapterMeta;

  document.querySelectorAll("[data-book-id]").forEach((option) => {
    option.setAttribute("aria-selected", option.dataset.bookId === STATE.studyBookId ? "true" : "false");
  });
  document.querySelectorAll("[data-chapter-id]").forEach((option) => {
    option.setAttribute("aria-selected", option.dataset.chapterId === STATE.studyChapterId ? "true" : "false");
  });
}

function chapterById(chapterId) {
  return (STATE.dataset?.chapters || []).find((chapter) => chapter.id === chapterId) || null;
}

function bookById(bookId) {
  return (STATE.dataset?.books || []).find((book) => book.id === bookId) || null;
}

function chaptersForBook(bookId) {
  return (STATE.dataset?.chapters || []).filter((chapter) => chapterBookId(chapter) === bookId);
}

function chapterBookId(chapter) {
  return chapter?.book_id || chapter?.book || "";
}

function chapterData(chapterId = STATE.currentChapterId) {
  return STATE.chapterDataCache.get(chapterId)
    || STATE.dataset?.data?.[chapterId]
    || { sections: [], assets: [], references: {}, semantic_chapter_links: [], prerequisites: [] };
}

async function ensureChapterData(chapter) {
  if (!chapter?.id || STATE.chapterDataCache.has(chapter.id) || STATE.dataset?.data?.[chapter.id]) return;
  const path = chapter.data_path || `./data/generated/chapters/${chapter.id}.json`;
  STATE.chapterDataCache.set(chapter.id, await fetchJson(path));
}

function studyChapterData() {
  return chapterData(STATE.studyChapterId || STATE.currentChapterId);
}

function setStatus(message) {
  const status = document.getElementById("readerStatus");
  status.textContent = message || "";
  status.hidden = !message;
}

function renderSectionRail() {
  const rail = document.getElementById("sectionRail");
  const sections = (chapterData(STATE.currentChapterId).sections || []).filter((section) => section.anchor);
  rail.innerHTML = sections.length ? sections.map(renderSectionRailItem).join("") : "";
  hideRailTooltip();
  updateSectionRailSelection();
}

function renderSectionRailItem(section) {
  const depth = Math.min(3, Math.max(0, Number(section.depth ?? section.level ?? 1) - 1));
  const title = section.nav_label || compactNavTitle(section.title);
  return `
    <button type="button" class="section-rail-item" style="--depth: ${depth}" data-section-nav-anchor="${escapeHtml(section.anchor)}" data-title="${escapeHtml(title)}" aria-label="${escapeHtml(title)}">
      <span class="rail-mark" aria-hidden="true"></span>
    </button>
  `;
}

function showRailTooltip(button) {
  const tooltip = document.getElementById("railTooltip");
  const title = button.dataset.title || "";
  if (!tooltip || !title) return;
  tooltip.textContent = title;
  tooltip.hidden = false;
  positionRailTooltip(button);
}

function positionRailTooltip(button) {
  const tooltip = document.getElementById("railTooltip");
  const pane = document.querySelector(".reading-pane");
  if (!tooltip || !pane || tooltip.hidden) return;
  const buttonBox = button.getBoundingClientRect();
  const paneBox = pane.getBoundingClientRect();
  const tooltipBox = tooltip.getBoundingClientRect();
  const top = Math.max(10, Math.min(buttonBox.top - paneBox.top + buttonBox.height / 2 - tooltipBox.height / 2, paneBox.height - tooltipBox.height - 10));
  tooltip.style.top = `${top}px`;
  tooltip.style.right = "48px";
}

function hideRailTooltip() {
  const tooltip = document.getElementById("railTooltip");
  if (!tooltip) return;
  tooltip.hidden = true;
}

function compactNavTitle(title) {
  const text = compactTitle(title)
    .replace(/^Chapter\s+\d+\s*[·:-]\s*/i, "")
    .replace(/^Appendix\s+\d+\s*[·:-]\s*/i, "");
  const parts = text.split(/\s*\/\s*/).map((part) => part.trim()).filter(Boolean);
  return (parts[parts.length - 1] || text).slice(0, 58);
}

function renderPrerequisites() {
  const data = studyChapterData();
  const prerequisites = sortedPrerequisites((data.prerequisites || []).filter((item) => item.validated_by_llm === true));
  document.getElementById("conceptScope").textContent = `对应 ${chapterLabel(STATE.studyChapterId || STATE.currentChapterId)}`;
  document.getElementById("conceptCount").textContent = String(prerequisites.length);
  document.getElementById("conceptList").innerHTML = prerequisites.length
    ? prerequisites.map(renderPrerequisiteCard).join("")
    : `<div class="empty-state">该章节的前置概念尚未生成，或 LLM 未确认存在可靠的跨章节依赖。</div>`;
  updatePrerequisiteSelection();
}

function sortedPrerequisites(prerequisites) {
  return [...prerequisites].sort((left, right) => {
    const leftScore = Number(left.priority_score || fallbackPriorityScore(left));
    const rightScore = Number(right.priority_score || fallbackPriorityScore(right));
    return rightScore - leftScore;
  });
}

function fallbackPriorityScore(item) {
  const links = item.source_links || [];
  const assetRefs = links.filter((link) => link.ref_type !== "chapter").length;
  return (item.used_in_sections || []).length * 10 + links.length * 2 + assetRefs;
}

function renderPrerequisiteCard(item) {
  const keyPoints = (item.key_points || []).map((point) => `<li>${renderInline(point)}</li>`).join("");
  const sources = (item.source_links || [])
    .map((link) => `
      <button type="button" class="source-chip" data-source-chapter="${escapeHtml(link.chapter_id)}" data-source-anchor="${escapeHtml(link.anchor || "")}">
        <span>${escapeHtml(sourceButtonLabel(link))}</span>
      </button>
    `)
    .join("");
  const evidence = item.evidence_summary || item.source_excerpt || "";
  const title = item.concept_title || item.nav_label || prerequisiteTitle(item);

  return `
    <article class="concept-card" data-used-sections="${escapeHtml((item.used_in_sections || []).join(" "))}">
      <div class="concept-card-header">
        <h3>${escapeHtml(title)}</h3>
      </div>
      ${item.why_needed ? `<p class="why-needed">${renderInline(item.why_needed)}</p>` : ""}
      ${sources ? `<div class="knowledge-jumps" aria-label="前置知识点跳转">${sources}</div>` : ""}
      ${keyPoints ? `<ul class="key-points">${keyPoints}</ul>` : ""}
      ${evidence ? `<blockquote>${escapeHtml(evidence)}</blockquote>` : ""}
    </article>
  `;
}

function prerequisiteTitle(item) {
  const chapter = chapterLabel(item.source_chapter_id);
  const firstLink = (item.source_links || []).find((link) => link.ref_type !== "chapter") || (item.source_links || [])[0] || {};
  const sectionTitle = compactTitle(firstLink.section_title || "");
  const tail = sectionTitle.split("/").map((part) => part.trim()).filter(Boolean).pop() || "";
  if (!tail || tail.toLowerCase().startsWith(chapter.toLowerCase())) return chapter;
  return `${chapter} · ${tail.slice(0, 56)}`;
}

function sourceButtonLabel(link) {
  const type = String(link.ref_type || "").toLowerCase();
  if (type === "chapter") return `${link.label || chapterLabel(link.chapter_id)} overview`;
  if (type === "equation" || type === "formula") return `Formula ${link.ref_id || ""}`.trim();
  if (type === "figure") return `Figure ${link.ref_id || ""}`.trim();
  if (type === "table") return `Table ${link.ref_id || ""}`.trim();
  if (type === "example") return `Example ${link.ref_id || ""}`.trim();
  return link.label || link.ref_id || link.chapter_id || "Source";
}

async function jumpToReference(chapterId, anchor) {
  if (!chapterId) return;
  const root = document.getElementById("markdownRoot");
  if (chapterId !== STATE.currentChapterId) {
    if (!STATE.returnPoint && STATE.currentChapterId === STATE.studyChapterId) {
      STATE.returnPoint = {
        studyBookId: STATE.studyBookId,
        studyChapterId: STATE.studyChapterId,
        chapterId: STATE.currentChapterId,
        anchor: STATE.activeAnchor,
        scrollTop: root.scrollTop,
      };
    }
    await openChapter(chapterId, anchor);
    return;
  }
  moveReaderToAnchor(anchor);
}

async function jumpToStudyAnchor(anchor) {
  const studyChapterId = STATE.studyChapterId || STATE.currentChapterId;
  STATE.returnPoint = null;
  if (STATE.currentChapterId !== studyChapterId) {
    await openChapter(studyChapterId, anchor);
    return;
  }
  moveReaderToAnchor(anchor);
}

function updateReturnButton() {
  const button = document.getElementById("returnButton");
  button.hidden = !STATE.returnPoint;
}

function renderMarkdown(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const html = [];
  let index = 0;
  let currentSectionAnchor = "";

  while (index < lines.length) {
    const line = lines[index];
    const trimmed = line.trim();

    if (!trimmed) {
      index += 1;
      continue;
    }
    if (/^\*\*\[[^\]]+\]\*\*$/.test(trimmed)) {
      index += 1;
      continue;
    }
    if (/^---+$/.test(trimmed)) {
      html.push("<hr>");
      index += 1;
      continue;
    }
    if (/^#{1,6}\s+/.test(trimmed)) {
      const parsed = parseSectionTitle(trimmed.replace(/^#{1,6}\s+/, ""));
      currentSectionAnchor = parsed.anchor;
      html.push(renderHeading(trimmed));
      index += 1;
      continue;
    }
    if (trimmed.startsWith(">")) {
      const block = collectQuote(lines, index);
      html.push(renderQuoteBlock(block.lines, { sectionAnchor: currentSectionAnchor }));
      index = block.nextIndex;
      continue;
    }
    if (looksLikeMarkdownTable(lines, index)) {
      const block = collectMarkdownTable(lines, index);
      html.push(renderTable({ rows: block.rows }));
      index = block.nextIndex;
      continue;
    }

    const paragraph = [];
    while (index < lines.length) {
      const current = lines[index];
      const currentTrimmed = current.trim();
      if (
        !currentTrimmed ||
        /^#{1,6}\s+/.test(currentTrimmed) ||
        currentTrimmed.startsWith(">") ||
        /^---+$/.test(currentTrimmed) ||
        looksLikeMarkdownTable(lines, index)
      ) {
        break;
      }
      if (!/^\*\*\[[^\]]+\]\*\*$/.test(currentTrimmed)) paragraph.push(currentTrimmed);
      index += 1;
    }
    if (paragraph.length) html.push(renderParagraph(paragraph.join(" "), { sectionAnchor: currentSectionAnchor }));
  }

  return html.join("\n");
}

function appendGeneratedAssets(root) {
  const data = chapterData(STATE.currentChapterId);
  const generatedAssets = (data.assets || []).filter((asset) => (
    ["formula", "table", "example"].includes(normalizeAssetKind(asset.kind)) &&
    ["paddle", "placeholder", "formula-library", "table-library", "example-library"].includes(String(asset.origin || ""))
  ));
  generatedAssets.forEach((asset) => {
    const anchor = asset.anchor || assetAnchor(asset.kind, asset.id);
    if (!anchor || root.querySelector(`#${cssEscape(anchor)}`)) return;
    const wrapper = document.createElement("div");
    wrapper.className = "generated-asset-slot";
    wrapper.innerHTML = renderGeneratedAsset(asset);
    if (!wrapper.innerHTML.trim()) return;
    insertAtSectionEnd(root, wrapper, asset.section_id || "");
  });
}

function renderGeneratedAsset(asset) {
  const kind = normalizeAssetKind(asset.kind);
  if (kind === "formula") return renderFormulaBlock(asset.id, asset);
  if (kind === "table") {
    return renderTable({
      id: asset.anchor || assetAnchor("table", asset.id),
      label: asset.label || `Table ${asset.id}`,
      caption: asset.caption || "",
      rows: Array.isArray(asset.rows) ? asset.rows : [],
      htmlTable: asset.html || asset.htmlTable || "",
    });
  }
  if (kind === "example") {
    const content = String(asset.content_markdown || asset.excerpt || "").trim();
    const body = content ? renderGeneratedExampleBody(content) : "";
    return `
      <section class="asset-block example-block" id="${escapeHtml(asset.anchor || assetAnchor("example", asset.id))}">
        <h3>${escapeHtml(asset.label || `Example ${asset.id}`)}</h3>
        ${body}
      </section>
    `;
  }
  return "";
}

function renderGeneratedExampleBody(content) {
  return String(content || "")
    .split(/\n{2,}/)
    .map((chunk) => chunk.trim())
    .filter(Boolean)
    .map((chunk) => `<p>${renderInline(chunk.replace(/^Example\s+\S+\.\s*/i, ""))}</p>`)
    .join("");
}

function insertAtSectionEnd(root, element, sectionId) {
  const data = chapterData(STATE.currentChapterId);
  const section = (data.sections || []).find((item) => item.id === sectionId);
  if (!section?.anchor) {
    root.appendChild(element);
    return;
  }
  const heading = root.querySelector(`[data-section-anchor="${cssEscape(section.anchor)}"]`);
  if (!heading) {
    root.appendChild(element);
    return;
  }
  let cursor = heading.nextElementSibling;
  while (cursor && !cursor.matches("[data-section-anchor]")) {
    cursor = cursor.nextElementSibling;
  }
  root.insertBefore(element, cursor || null);
}

function renderParagraph(text, context = {}) {
  const value = String(text || "");
  const html = [];
  let inlineBuffer = "";

  const pushText = () => {
    const chunk = inlineBuffer;
    inlineBuffer = "";
    const trimmed = String(chunk || "").trim();
    if (trimmed) html.push(`<p>${renderInline(trimmed, context)}</p>`);
  };

  const appendTextWithFormulaRefs = (rawText) => {
    const pattern = /(?:(LW)\s+)?\[\[SEE_FORMULA:([^\]]+)\]\]/gi;
    let lastIndex = 0;
    let match;
    while ((match = pattern.exec(rawText)) !== null) {
      inlineBuffer += rawText.slice(lastIndex, match.index);
      const [raw, lw, refId] = match;
      const targetChapterId = chapterIdFromRef(refId, lw ? "Genetics" : currentBookId());
      const asset = targetChapterId === STATE.currentChapterId ? findAsset("formula", refId, STATE.currentChapterId) : null;
      if (asset?.origin === "placeholder" || asset?.origin === "paddle") {
        pushText();
        html.push(renderFormulaBlock(refId, asset));
      } else {
        inlineBuffer += raw;
      }
      lastIndex = match.index + raw.length;
    }
    inlineBuffer += rawText.slice(lastIndex);
  };

  const parsed = window.StudyMath?.tokenizeMath(value) || { tokens: [{ kind: "text", value }], diagnostics: [] };
  reportMathDiagnostics(parsed.diagnostics, value, "paragraph");
  parsed.tokens.forEach((token) => {
    if (token.kind === "display") {
      pushText();
      const asset = findFormulaAssetByLatex(token.value);
      if (asset) {
        html.push(renderFormulaBlock(asset.id, asset));
      } else {
        html.push(`<div class="math-block" data-tex="${escapeAttribute(token.value)}"></div>`);
      }
      return;
    }
    if (token.kind === "inline") inlineBuffer += `$${token.value}$`;
    else appendTextWithFormulaRefs(token.value);
  });
  pushText();
  return html.join("\n");
}

function renderHeading(line) {
  const match = line.match(/^(#{1,6})\s+(.+)$/);
  const level = Math.min(match[1].length, 4);
  const parsed = parseSectionTitle(match[2]);
  return `<h${level} id="${escapeHtml(parsed.anchor)}" data-section-anchor="${escapeHtml(parsed.anchor)}">${escapeHtml(parsed.title)}</h${level}>`;
}

function parseSectionTitle(rawTitle) {
  const cleaned = cleanText(rawTitle.replace(/#+\s*$/, "").trim());
  const matchedSection = findSectionForHeading(cleaned);
  if (matchedSection) {
    return {
      anchor: matchedSection.anchor,
      title: matchedSection.title || cleaned,
    };
  }
  const unit = cleaned.match(/^([A-Za-z]+_(?:chapter|appendix)\d+_\d{3})\s*(?:·|路|-|—|\|)\s*(.+)$/i);
  if (unit) return { anchor: normalizeAnchor(unit[1]), title: unit[2].trim() };
  return { anchor: normalizeAnchor(cleaned), title: cleaned };
}

function findSectionForHeading(cleanedTitle) {
  const sections = chapterData(STATE.currentChapterId).sections || [];
  return sections.find((section) => {
    const raw = cleanText(section.raw_title || "");
    const title = cleanText(section.title || "");
    return raw === cleanedTitle || title === cleanedTitle;
  }) || null;
}

function collectQuote(lines, start) {
  const quote = [];
  let index = start;
  while (index < lines.length && lines[index].trim().startsWith(">")) {
    quote.push(dequote(lines[index]));
    index += 1;
  }
  return { lines: quote, nextIndex: index };
}

function dequote(line) {
  let text = line.trim();
  while (text.startsWith(">")) text = text.slice(1).trim();
  return text;
}

function renderQuoteBlock(lines, context = {}) {
  const text = lines.join("\n");
  const header = firstAssetHeader(lines);
  const formula = header.match(/\*\*Formula\s+\(([^)]+)\)\*\*/i);
  const figure = header.match(/\*\*Figure\s+(A?\d+\.\d+[a-z]?)\*\*/i);
  const table = header.match(/\*\*Table\s+(A?\d+\.\d+[a-z]?)\*\*/i);
  const example = header.match(/\*\*Example\s+(A?\d+\.\d+[a-z]?)\*\*/i);

  if (formula) {
    const refId = formula[1];
    const asset = findAsset("formula", refId, STATE.currentChapterId);
    const latex = asset?.latex_render || asset?.latex || extractDisplayMath(lines);
    return renderFormulaBlock(refId, { latex_render: latex, latex });
  }

  if (figure) {
    const refId = figure[1];
    const image = text.match(/!\[[^\]]*\]\(([^)]+)\)/);
    const caption = lines.find((item) => item.startsWith(`Figure ${refId}`)) || "";
    return `
      <figure class="asset-block figure-block" id="${escapeHtml(assetAnchor("figure", refId))}">
        ${image ? `<img src="${escapeAttribute(resolveFigureSrc(image[1]))}" alt="${escapeAttribute(`Figure ${refId}`)}" loading="lazy">` : `<div class="missing-asset">Figure image missing</div>`}
        <figcaption>${renderInline(caption || `Figure ${refId}`, context)}</figcaption>
      </figure>
    `;
  }

  if (table) {
    const refId = table[1];
    const caption = lines.find((item) => item.startsWith(`Table ${refId}`)) || "";
    const htmlTable = text.match(/<table[\s\S]*<\/table>/i)?.[0] || "";
    const rows = parseMarkdownRows(lines);
    return renderTable({ id: assetAnchor("table", refId), label: `Table ${refId}`, caption, rows, htmlTable, context });
  }

  if (example) {
    const refId = example[1];
    return `
      <section class="asset-block example-block" id="${escapeHtml(assetAnchor("example", refId))}">
        <h3>Example ${escapeHtml(refId)}</h3>
        ${renderExampleContent(lines, context)}
      </section>
    `;
  }

  const paragraphs = lines.filter(Boolean).map((item) => `<p>${renderInline(item, context)}</p>`).join("");
  return `<blockquote class="reader-quote">${paragraphs}</blockquote>`;
}

function firstAssetHeader(lines) {
  return (lines || []).map((line) => String(line || "").trim()).find(Boolean) || "";
}

function renderFormulaBlock(refId, asset = {}) {
  const latex = asset.latex_render || asset.latex || "";
  return `
    <figure class="asset-block formula-block" id="${escapeHtml(assetAnchor("formula", refId))}">
      <div class="formula-label">Formula ${escapeHtml(refId)}</div>
      <div class="formula-row">
        <div class="math-block" data-tex="${escapeAttribute(latex)}"></div>
        <span class="formula-number">(${escapeHtml(refId)})</span>
      </div>
    </figure>
  `;
}

function findFormulaAssetByLatex(latex) {
  const key = latexKey(latex);
  if (!key) return null;
  return (chapterData(STATE.currentChapterId).assets || []).find((asset) => (
    asset.kind === "formula" &&
    (asset.origin === "paddle" || asset.origin === "placeholder") &&
    (latexKey(asset.latex) === key || latexKey(asset.latex_render) === key)
  )) || null;
}

function latexKey(latex) {
  return String(latex || "")
    .trim()
    .replace(/^\$\$|\$\$$/g, "")
    .replace(/\s+/g, "");
}

function renderExampleContent(lines, context = {}) {
  const bodyLines = (lines || []).filter((item) => !/^\*\*Example\s+/i.test(String(item || "").trim()));
  const html = [];
  let paragraph = [];
  let index = 0;

  const flushParagraph = () => {
    const text = paragraph.join(" ").trim().replace(/^Example\s+\S+\.\s*/i, "");
    if (text) html.push(`<p>${renderInline(text, context)}</p>`);
    paragraph = [];
  };

  while (index < bodyLines.length) {
    const line = String(bodyLines[index] || "").trim();
    if (!line) {
      flushParagraph();
      index += 1;
      continue;
    }
    if (isNestedAssetHeader(line)) {
      flushParagraph();
      const collected = collectNestedAssetLines(bodyLines, index);
      const nested = collected.lines;
      index = collected.nextIndex;
      html.push(renderQuoteBlock(nested, context));
      continue;
    }
    paragraph.push(line);
    index += 1;
  }
  flushParagraph();
  return html.join("\n");
}

function isNestedAssetHeader(line) {
  return /\*\*(?:Formula\s+\([^)]+\)|Figure\s+A?\d+\.\d+[a-z]?|Table\s+A?\d+\.\d+[a-z]?)\*\*/i.test(line);
}

function collectNestedAssetLines(lines, start) {
  const first = String(lines[start] || "");
  const nested = [first];
  const formula = first.match(/\*\*Formula\s+\(([^)]+)\)\*\*/i);
  const figure = first.match(/\*\*Figure\s+(A?\d+\.\d+[a-z]?)\*\*/i);
  const table = first.match(/\*\*Table\s+(A?\d+\.\d+[a-z]?)\*\*/i);
  let index = start + 1;
  let inMath = false;
  let sawMath = false;
  let sawFigureCaption = false;

  while (index < lines.length) {
    const line = String(lines[index] || "");
    const trimmed = line.trim();
    if (isNestedAssetHeader(trimmed)) break;
    nested.push(line);
    index += 1;

    if (formula) {
      if (trimmed.includes("$$")) {
        const count = (trimmed.match(/\$\$/g) || []).length;
        sawMath = true;
        if (count >= 2 && !inMath) break;
        inMath = !inMath;
        if (sawMath && !inMath) break;
      }
      continue;
    }

    if (figure) {
      if (trimmed.startsWith(`Figure ${figure[1]}`)) sawFigureCaption = true;
      if (sawFigureCaption) break;
      continue;
    }

    if (table && sawTableEnd(nested)) break;
  }

  return { lines: nested, nextIndex: index };
}

function sawTableEnd(lines) {
  const content = lines.map((line) => String(line || "").trim()).filter(Boolean);
  if (content.length < 3) return false;
  const last = content[content.length - 1];
  return content.some((line) => /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line)) && !last.includes("|");
}

function extractDisplayMath(lines) {
  const chunks = [];
  let inMath = false;
  lines.forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line.includes("$$") && !inMath) return;
    if (line.includes("$$")) {
      const parts = line.split("$$");
      if (!inMath && parts.length >= 3) {
        chunks.push(parts[1].trim());
        return;
      }
      if (!inMath) {
        chunks.push(parts[1].trim());
        inMath = true;
        return;
      }
      chunks.push(parts[0].trim());
      inMath = false;
      return;
    }
    if (inMath) chunks.push(line);
  });
  return chunks.filter(Boolean).join("\n").trim();
}

function resolveFigureSrc(src) {
  if (!src) return "";
  // Release data must be self-contained. Absolute or protocol-relative asset
  // paths are not rendered, even if malformed source data reaches the client.
  if (/^[a-z][a-z0-9+.-]*:/i.test(src) || src.startsWith("//") || src.startsWith("/")) return "";
  if (src.startsWith("figures/")) return `/data/textbook/${src}`;
  return `/data/textbook/figures/${src}`;
}

function looksLikeMarkdownTable(lines, index) {
  return Boolean(lines[index]?.includes("|") && lines[index + 1]?.match(/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/));
}

function collectMarkdownTable(lines, start) {
  const rows = [];
  let index = start;
  while (index < lines.length && lines[index].includes("|")) {
    rows.push(lines[index]);
    index += 1;
  }
  return { rows: parseMarkdownRows(rows), nextIndex: index };
}

function parseMarkdownRows(lines) {
  return lines
    .filter((line) => line.includes("|") && !/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line))
    .map((line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim()));
}

function renderTable({ id = "", label = "", caption = "", rows = [], htmlTable = "", context = {} }) {
  if (htmlTable) {
    return `
      <figure class="asset-block table-block" ${id ? `id="${escapeHtml(id)}"` : ""}>
        ${label ? `<figcaption>${escapeHtml(label)}</figcaption>` : ""}
        ${caption ? `<p class="table-caption">${renderInline(caption, context)}</p>` : ""}
        <div class="table-scroll">${renderMathInTrustedHtml(htmlTable)}</div>
      </figure>
    `;
  }
  if (!rows.length) return "";
  const header = rows[0] || [];
  const body = rows.slice(1);
  return `
    <figure class="asset-block table-block" ${id ? `id="${escapeHtml(id)}"` : ""}>
      ${label ? `<figcaption>${escapeHtml(label)}</figcaption>` : ""}
      ${caption ? `<p class="table-caption">${renderInline(caption, context)}</p>` : ""}
      <div class="table-scroll">
        <table>
          <thead><tr>${header.map((cell) => `<th>${renderInline(cell)}</th>`).join("")}</tr></thead>
          <tbody>${body.map((row) => `<tr>${row.map((cell) => `<td>${renderInline(cell)}</td>`).join("")}</tr>`).join("")}</tbody>
        </table>
      </div>
    </figure>
  `;
}

function renderInline(rawValue, context = {}) {
  const tokens = [];
  let text = cleanText(String(rawValue || ""));
  const parsed = window.StudyMath?.tokenizeMath(text) || { tokens: [{ kind: "text", value: text }], diagnostics: [] };
  reportMathDiagnostics(parsed.diagnostics, text, "inline");
  text = parsed.tokens.map((part) => {
    if (part.kind === "text") return part.value;
    const token = `\u0000${tokens.length}\u0000`;
    const className = part.kind === "display" ? "math-display-inline" : "math-inline";
    tokens.push(`<span class="${className}" data-tex="${escapeAttribute(part.value)}"></span>`);
    return token;
  }).join("");

  let html = escapeHtml(text);
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\b(?:(LW)\s+)?(Equation|Figure|Table|Example)s?\s+(A?\d+\.\d+(?:\.\d+)?[a-z]?)/gi, (match, lw, kind, refId) => {
    return renderReferenceLink(kind, refId, match, { ...context, bookHint: lw ? "Genetics" : "" });
  });
  html = html.replace(/\bLW\s+\[\[SEE_(FIGURE|TABLE|EXAMPLE|FORMULA):([^\]]+)\]\]/gi, (_, kind, refId) => {
    const labelKind = kind.toLowerCase() === "formula" ? "Formula" : titleCase(kind);
    return renderReferenceLink(kind, refId, `LW ${labelKind} ${refId}`, { ...context, bookHint: "Genetics" });
  });
  html = html.replace(/\[\[SEE_(FIGURE|TABLE|EXAMPLE|FORMULA):([^\]]+)\]\]/gi, (_, kind, refId) => {
    const labelKind = kind.toLowerCase() === "formula" ? "Formula" : titleCase(kind);
    return renderReferenceLink(kind, refId, `${labelKind} ${refId}`, context);
  });
  html = html.replace(/\b(?:(LW)\s+)?Chapters?\s+(\d{1,2}(?:\s*(?:,|and|&)\s*\d{1,2})*)(?!\s*,\s*\d{3,4})/gi, (match, lw, rawNumbers) => {
    const bookHint = lw ? "Genetics" : "";
    const rendered = rawNumbers.replace(/\d+/g, (number) => renderChapterReferenceButton(number, bookHint, context));
    if (!/\d/.test(rendered)) return match;
    return rendered;
  });
  html = html.replace(/\u0000(\d+)\u0000/g, (_, index) => tokens[Number(index)] || "");
  return html;
}

function renderMathInTrustedHtml(rawHtml) {
  const safeHtml = sanitizeTableHtml(rawHtml);
  return safeHtml.split(/(<[^>]+>)/g).map((part) => {
    if (!part || part.startsWith("<")) return part;
    const parsed = window.StudyMath?.tokenizeMath(part) || { tokens: [{ kind: "text", value: part }], diagnostics: [] };
    reportMathDiagnostics(parsed.diagnostics, part, "table");
    return parsed.tokens.map((token) => {
      if (token.kind === "text") return token.value;
      const className = token.kind === "display" ? "math-display-inline" : "math-inline";
      return `<span class="${className}" data-tex="${escapeAttribute(token.value)}"></span>`;
    }).join("");
  }).join("");
}

function sanitizeTableHtml(rawHtml) {
  const allowedTags = new Set([
    "TABLE", "THEAD", "TBODY", "TFOOT", "TR", "TH", "TD", "CAPTION",
    "COLGROUP", "COL", "SPAN", "SUP", "SUB", "STRONG", "EM", "BR",
  ]);
  const allowedAttributes = new Set(["rowspan", "colspan", "scope"]);
  const documentNode = new DOMParser().parseFromString(`<body>${String(rawHtml || "")}</body>`, "text/html");
  const elements = Array.from(documentNode.body.querySelectorAll("*"));
  elements.forEach((element) => {
    if (!allowedTags.has(element.tagName)) {
      element.replaceWith(documentNode.createTextNode(element.textContent || ""));
      return;
    }
    Array.from(element.attributes).forEach((attribute) => {
      if (!allowedAttributes.has(attribute.name.toLowerCase())) element.removeAttribute(attribute.name);
    });
  });
  return documentNode.body.innerHTML;
}

function reportMathDiagnostics(diagnostics, source, surface) {
  if (!diagnostics?.length) return;
  console.warn("Math delimiter diagnostic", {
    chapter: STATE.currentChapterId,
    surface,
    diagnostics,
    source: String(source || "").slice(0, 240),
  });
}

function renderReferenceLink(kind, refId, label, context = {}) {
  const target = resolveReference(kind, refId, context);
  if (!target) return escapeHtml(label);
  return `<button type="button" class="inline-ref" data-jump-chapter="${escapeAttribute(target.chapterId)}" data-jump-anchor="${escapeAttribute(target.anchor)}">${escapeHtml(label)}</button>`;
}

function renderChapterReferenceButton(chapterNumber, bookHint = "", context = {}) {
  const chapterId = chapterIdForNumber(chapterNumber, bookHint || currentBookId());
  if (!chapterById(chapterId)) return chapterNumber;
  const target = resolveSemanticChapterTarget(chapterNumber, { ...context, bookHint }) || {
    chapterId,
    anchor: chapterData(chapterId).sections?.[0]?.anchor || "",
  };
  const label = `${bookHint === "Genetics" ? "LW Chapter" : "Chapter"} ${Number(chapterNumber)}`;
  return `<button type="button" class="inline-ref chapter-ref" data-jump-chapter="${escapeAttribute(target.chapterId)}" data-jump-anchor="${escapeAttribute(target.anchor || "")}">${escapeHtml(label)}</button>`;
}

function resolveSemanticChapterTarget(chapterNumber, context = {}) {
  const sourceChapterId = chapterIdForNumber(chapterNumber, context.bookHint || currentBookId());
  const semanticLinks = chapterData(STATE.currentChapterId).semantic_chapter_links || [];
  const sectionAnchor = context.sectionAnchor || "";
  const sectionId = currentSectionIdFromAnchor(sectionAnchor);
  const candidates = semanticLinks.filter((link) => link.source_chapter_id === sourceChapterId);
  if (!candidates.length) return null;
  const sectionMatch = candidates.find((link) => (
    (sectionAnchor && link.current_anchor === sectionAnchor) ||
    (sectionId && link.current_section_id === sectionId)
  ));
  const selected = sectionMatch || candidates[0];
  return {
    chapterId: sourceChapterId,
    anchor: selected.target_anchor || chapterData(sourceChapterId).sections?.[0]?.anchor || "",
  };
}

function currentSectionIdFromAnchor(anchor) {
  if (!anchor) return "";
  return (chapterData(STATE.currentChapterId).sections || []).find((section) => section.anchor === anchor)?.id || "";
}

function resolveReference(kind, refId, context = {}) {
  const targetChapterId = chapterIdFromRef(refId, context.bookHint || currentBookId()) || STATE.currentChapterId;
  const data = chapterData(targetChapterId);
  const wantedKind = normalizeAssetKind(kind);
  const asset = findReferenceAsset(data.assets || [], wantedKind, refId);
  if (asset) return { chapterId: targetChapterId, anchor: asset.anchor };
  return null;
}

function findReferenceAsset(assets, wantedKind, refId) {
  const wantedId = String(refId || "").trim().toLowerCase();
  const normalizedKind = normalizeAssetKind(wantedKind);
  const exact = assets.find((item) => normalizeAssetKind(item.kind) === normalizedKind && String(item.id || "").trim().toLowerCase() === wantedId);
  if (exact) return exact;
  if (normalizedKind === "figure") {
    const baseRefId = wantedId.replace(/[a-z]$/i, "");
    return assets.find((item) => normalizeAssetKind(item.kind) === "figure" && String(item.id || "").trim().toLowerCase() === baseRefId) || null;
  }
  if (normalizedKind === "formula" && /^a?\d+\.\d+(?:\.\d+)?$/i.test(wantedId)) {
    const matches = assets
      .filter((item) => normalizeAssetKind(item.kind) === "formula" && new RegExp(`^${escapeRegExp(wantedId)}[a-z]$`, "i").test(String(item.id || "").trim()))
      .sort((a, b) => formulaRefSortValue(String(a.id || "")).localeCompare(formulaRefSortValue(String(b.id || ""))));
    return matches[0] || null;
  }
  return null;
}

function formulaRefSortValue(refId) {
  const match = String(refId || "").trim().toLowerCase().match(/^(a?\d+)\.(\d+)(?:\.(\d+))?([a-z]?)$/);
  if (!match) return String(refId || "");
  return `${match[1].padStart(4, "0")}.${match[2].padStart(4, "0")}.${(match[3] || "0").padStart(4, "0")}.${match[4] || ""}`;
}

function escapeRegExp(value) {
  return String(value || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizeAssetKind(kind) {
  const value = String(kind || "").toLowerCase();
  return value === "equation" || value === "formula" ? "formula" : value;
}

function findAsset(kind, refId, chapterId = STATE.currentChapterId) {
  const data = chapterData(chapterId);
  const wantedKind = normalizeAssetKind(kind);
  return (data.assets || []).find((item) => {
    const itemKind = normalizeAssetKind(item.kind);
    return itemKind === wantedKind && String(item.id || "").toLowerCase() === String(refId || "").toLowerCase();
  }) || null;
}

function chapterIdFromRef(refId, bookId = currentBookId()) {
  const value = String(refId || "").trim();
  if (/^a\d+/i.test(value)) {
    const appendixId = `${bookId}_appendix${Number(value.match(/^a(\d+)/i)[1])}`;
    if (chapterById(appendixId)) return appendixId;
    if (String(bookId).toLowerCase() === "genetics" && chapterById("Genetics_chapter27")) return "Genetics_chapter27";
    return appendixId;
  }
  const number = value.match(/^(\d+)/)?.[1];
  return number ? chapterIdForNumber(number, bookId) : "";
}

function chapterIdForNumber(number, bookId = currentBookId()) {
  return `${bookId || currentBookId()}_chapter${Number(number)}`;
}

function currentBookId() {
  return chapterBookId(chapterById(STATE.currentChapterId)) || STATE.studyBookId || STATE.dataset?.default_book || "Evolution";
}

function bookIdFromChapterId(chapterId) {
  return String(chapterId || "").split("_")[0] || "";
}

function renderMath(root) {
  if (!window.katex) return 0;
  let failures = 0;
  root.querySelectorAll("[data-tex]").forEach((element) => {
    // Decode entities introduced by legacy HTML serialization before KaTeX.
    const tex = String(element.dataset.tex || "")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&amp;/g, "&")
      .replace(/&nbsp;/g, " ");
    try {
      if (!tex.trim() || /(^|[^\\])\$/.test(tex)) throw new Error("invalid TeX boundary");
      window.katex.render(tex, element, {
        displayMode: element.classList.contains("math-block") || element.classList.contains("math-display-inline"),
        throwOnError: true,
        strict: "ignore",
        trust: true,
      });
    } catch (error) {
      failures += 1;
      element.classList.add("math-fallback");
      element.textContent = tex;
      element.title = "Formula could not be rendered; original TeX is shown.";
      console.error("KaTeX render failed", {
        chapter: STATE.currentChapterId,
        tex,
        message: error instanceof Error ? error.message : String(error),
      });
    }
  });
  return failures;
}

function moveReaderToAnchor(anchor) {
  if (!anchor) return;
  const root = document.getElementById("markdownRoot");
  const target = root.querySelector(`#${cssEscape(anchor)}`);
  if (!target) return;
  const rootBox = root.getBoundingClientRect();
  const targetBox = target.getBoundingClientRect();
  root.scrollTop += targetBox.top - rootBox.top - 18;
  document.querySelectorAll(".target-highlight, .target-framed, .target-companion").forEach((item) => {
    item.classList.remove("target-highlight", "target-framed", "target-companion");
  });
  target.classList.add("target-highlight", "target-framed");
  const companion = target.matches("[data-section-anchor]") ? nextReadableElement(target) : null;
  if (companion) companion.classList.add("target-companion");
  window.setTimeout(() => target.classList.remove("target-highlight"), 1600);
  window.setTimeout(() => {
    target.classList.remove("target-framed");
    companion?.classList.remove("target-companion");
  }, 4200);
  STATE.activeAnchor = anchor;
  updatePrerequisiteSelection();
  updateSectionRailSelection();
}

function nextReadableElement(element) {
  let node = element.nextElementSibling;
  while (node && !["P", "FIGURE", "SECTION", "BLOCKQUOTE"].includes(node.tagName)) {
    node = node.nextElementSibling;
  }
  return node || null;
}

function updateActiveSectionFromScroll() {
  const root = document.getElementById("markdownRoot");
  const headings = [...root.querySelectorAll("[data-section-anchor]")];
  const rootTop = root.getBoundingClientRect().top;
  let active = "";
  headings.forEach((heading) => {
    if (heading.getBoundingClientRect().top - rootTop < 96) active = heading.dataset.sectionAnchor || "";
  });
  if (active && active !== STATE.activeAnchor) {
    STATE.activeAnchor = active;
    updatePrerequisiteSelection();
    updateSectionRailSelection();
  }
}

function updateSectionRailSelection() {
  document.querySelectorAll(".section-rail-item").forEach((item) => {
    item.classList.toggle("is-active", item.dataset.sectionNavAnchor === STATE.activeAnchor);
  });
}

function updatePrerequisiteSelection() {
  const activeSection = STATE.currentChapterId === STATE.studyChapterId ? sectionIdFromStudyAnchor(STATE.activeAnchor) : "";
  document.querySelectorAll(".concept-card").forEach((card) => {
    const usedSections = (card.dataset.usedSections || "").split(/\s+/);
    card.classList.toggle("is-active", Boolean(activeSection && usedSections.includes(activeSection)));
  });
}

function sectionIdFromStudyAnchor(anchor) {
  return (studyChapterData().sections || []).find((section) => section.anchor === anchor)?.id || "";
}

function compactTitle(title) {
  return cleanText(String(title || ""))
    .replace(/^[A-Za-z]+_(?:chapter|appendix)\d+_\d{3}\s*(?:·|路|-|–|—|\|)\s*/i, "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 96);
}

function chapterLabel(chapterId) {
  return chapterById(chapterId)?.label || chapterId || "";
}

function assetAnchor(kind, refId) {
  const safe = String(refId || "").trim().toLowerCase().replace(/[()]/g, "").replace(/[^a-z0-9.]+/g, "-").replace(/^-|-$/g, "");
  return normalizeAnchor(`${kind}-${safe}`);
}

function normalizeAnchor(value) {
  return String(value || "section")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9_.-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-|-$/g, "") || "section";
}

function cleanText(value) {
  return String(value || "")
    .replace(/\s*路\s*/g, " · ")
    .replace(/\s+/g, " ")
    .trim();
}

function titleCase(value) {
  const text = String(value || "").toLowerCase();
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/`/g, "&#096;");
}

function cssEscape(value) {
  if (window.CSS?.escape) return window.CSS.escape(value);
  return String(value).replace(/[^a-zA-Z0-9_-]/g, "\\$&");
}
