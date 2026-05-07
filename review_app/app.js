const DATA_FILES = {
  review: "./data/generated/review_dataset.json",
  flow: "./data/generated/flow_graph.json",
  formulaOcr: "./tmp/formula_ocr_index.json",
  reviewLocators: "./tmp/review_locator_index.json",
};

const REVIEW_RECORDS_ENDPOINT = "./api/review-records";
const ISSUE_TAXONOMY_ENDPOINT = "./api/issue-taxonomy";
const STATUS_LABELS = {
  pending: "待确认",
  pass: "通过",
  fail: "不通过",
};
const STATUS_CLASS = {
  pending: "status-pending",
  pass: "status-pass",
  fail: "status-fail",
};
const STATUS_PRIORITY = {
  pending: 0,
  fail: 1,
  pass: 2,
};
const ISSUE_SEVERITY_LABELS = {
  info: "信息",
  warning: "警告",
  error: "错误",
  fatal: "致命",
};
const ISSUE_SCOPE_OPTIONS = [
  ["text", "正文"],
  ["inline_math", "inline 公式"],
  ["display_math", "display 公式"],
  ["formula_reference", "公式引用"],
  ["table_reference", "表格引用"],
  ["table", "表格"],
  ["chunk", "chunk 切分"],
  ["structure", "结构噪声"],
];
const FALLBACK_ISSUE_TAXONOMY = {
  version: 1,
  categories: [
    { issue_code: "inline_math_damage", label: "inline 公式损坏", scope: "inline_math", severity: "error", status: "manual_only" },
    { issue_code: "display_formula_damage", label: "display 公式损坏", scope: "display_math", severity: "error", status: "manual_only" },
    { issue_code: "formula_reference_error", label: "公式引用错误", scope: "formula_reference", severity: "fatal", status: "manual_only" },
    { issue_code: "formula_mention_not_linked", label: "公式提及未回链", scope: "formula_reference", severity: "warning", status: "manual_only" },
    { issue_code: "table_reference_error", label: "表格引用错误", scope: "table_reference", severity: "fatal", status: "manual_only" },
    { issue_code: "table_row_group_misattribution", label: "表格行归属错误", scope: "table", severity: "error", status: "manual_only" },
    { issue_code: "table_cell_alignment_error", label: "表格单元格错位", scope: "table", severity: "error", status: "manual_only" },
    { issue_code: "table_reference_target_error", label: "表格引用目标错误", scope: "table_reference", severity: "error", status: "manual_only" },
    { issue_code: "table_structure_error", label: "表格结构问题", scope: "table", severity: "error", status: "manual_only" },
    { issue_code: "duplicate_or_leaked_block", label: "重复/泄漏块", scope: "structure", severity: "warning", status: "manual_only" },
    { issue_code: "chunk_split_error", label: "chunk 切分问题", scope: "chunk", severity: "warning", status: "manual_only" },
    { issue_code: "chunk_boundary_error", label: "chunk 边界错误", scope: "chunk", severity: "warning", status: "manual_only" },
    { issue_code: "ocr_garbled_text", label: "OCR 乱码", scope: "text", severity: "warning", status: "manual_only" },
    { issue_code: "ghost_or_float_block", label: "ghost/[h] 噪声块", scope: "structure", severity: "error", status: "manual_only" },
    { issue_code: "truncated_text", label: "文本截断", scope: "text", severity: "error", status: "manual_only" },
    { issue_code: "placeholder_leak", label: "占位符/表格浮动残留", scope: "structure", severity: "error", status: "manual_only" },
  ],
};
const CHUNK_HIGHLIGHT_META = [
  { semantic: "discussion", kind: "chunk_discussion", label: "Discussion" },
  { semantic: "derivation", kind: "chunk_derivation", label: "Derivation" },
  { semantic: "proposition", kind: "chunk_proposition", label: "Proposition" },
  { semantic: "definition", kind: "chunk_definition", label: "Definition" },
];

const STATE = {
  section: "review",
  chapterId: null,
  viewId: "formulas",
  statusFilter: "all",
  searchQuery: "",
  selectedItemId: null,
  selectedItemKey: null,
  itemListCollapsed: true,
  subflowId: "formulas",
  pdfDoc: null,
  pdfChapterId: null,
  pdfPage: 1,
  pdfScale: 1.4,
  pdfFitMode: true,
  pdfViewCustomized: false,
  pdfStageScrollLeft: 0,
  pdfStageScrollTop: 0,
  highlightSpec: null,
  lastLocatedItemKey: null,
  candidatePages: [],
  locateRequestId: 0,
  indexWarmup: {},
  overlayManualPosition: null,
  overlayDrag: null,
  tableMathEnabled: true,
  chunkHighlightLegend: {
    discussion: true,
    derivation: true,
    proposition: true,
    definition: true,
  },
};

const DATA = {
  review: null,
  flow: null,
  formulaOcr: null,
  reviewLocators: null,
  pdfDocs: new Map(),
  pdfTextCache: new Map(),
};

let REVIEW_RECORDS = {};
let ISSUE_TAXONOMY = FALLBACK_ISSUE_TAXONOMY;
let SYNC_NOTICE = "未连接本地记录文件，当前先使用浏览器会话。";
let PDF_STAGE_RESIZE_OBSERVER = null;
let PDF_STAGE_RESIZE_TIMER = null;
let MATH_RENDER_RETRY_TIMER = null;
let MATH_RENDER_RETRY_COUNT = 0;
let SEARCH_LOCATE_TIMER = null;

document.addEventListener("DOMContentLoaded", () => {
  initialize().catch((error) => {
    console.error(error);
    document.body.innerHTML = `<div class="page-shell"><section class="panel-section"><h1>加载失败</h1><p>${escapeHtml(String(error))}</p></section></div>`;
  });
});

async function initialize() {
  const [review, flow, formulaOcr, reviewLocators] = await Promise.all([
    fetchJson(DATA_FILES.review),
    fetchJson(DATA_FILES.flow),
    fetchJsonOptional(DATA_FILES.formulaOcr, { chapters: {} }),
    fetchJsonOptional(DATA_FILES.reviewLocators, { chapters: {} }),
  ]);
  DATA.review = review;
  DATA.flow = flow;
  DATA.formulaOcr = formulaOcr || { chapters: {} };
  DATA.reviewLocators = reviewLocators || { chapters: {} };
  STATE.chapterId = review.default_chapter || review.chapters?.[0]?.id || null;

  await hydrateIssueTaxonomy();
  await hydrateReviewRecords();
  await configurePdfJs();
  bindGlobalControls();
  bindPdfStageAutoFit();
  renderViewTabs();
  renderChapterOptions();
  renderHero();
  renderReview();
  renderFlow();
  switchSection("review");
  await locateSelectedItemInPdf(true);
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`无法读取 ${path}: ${response.status}`);
  }
  return response.json();
}

async function fetchJsonOptional(path, fallbackValue) {
  try {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) {
      return fallbackValue;
    }
    return await response.json();
  } catch (error) {
    console.warn(`optional json not available: ${path}`, error);
    return fallbackValue;
  }
}

async function configurePdfJs() {
  if (!window.pdfjsLib) {
    try {
      const module = await import("https://cdn.jsdelivr.net/npm/pdfjs-dist@4.5.136/build/pdf.min.mjs");
      window.pdfjsLib = module;
    } catch (error) {
      console.warn("failed to import pdfjs", error);
    }
  }

  if (!window.pdfjsLib) {
    updatePdfStatus("PDF.js 未加载，无法预览原文。");
    return false;
  }
  window.pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.5.136/build/pdf.worker.min.mjs";
  return true;
}

function bindGlobalControls() {
  document.getElementById("navReview").addEventListener("click", () => switchSection("review"));
  document.getElementById("navFlow").addEventListener("click", () => switchSection("flow"));

  document.getElementById("chapterSelect").addEventListener("change", async (event) => {
    STATE.chapterId = event.target.value;
    STATE.selectedItemId = null;
    STATE.selectedItemKey = null;
    STATE.lastLocatedItemKey = null;
    STATE.candidatePages = [];
    renderReview();
    await locateSelectedItemInPdf(true);
  });

  document.getElementById("statusFilter").addEventListener("change", async (event) => {
    STATE.statusFilter = event.target.value;
    STATE.selectedItemId = null;
    STATE.selectedItemKey = null;
    STATE.lastLocatedItemKey = null;
    STATE.highlightSpec = null;
    STATE.candidatePages = [];
    renderReview();
    await locateSelectedItemInPdf(true);
  });

  document.getElementById("searchInput").addEventListener("input", (event) => {
    STATE.searchQuery = String(event.target.value || "");
    STATE.selectedItemId = null;
    STATE.selectedItemKey = null;
    STATE.lastLocatedItemKey = null;
    STATE.highlightSpec = null;
    STATE.candidatePages = [];
    renderReview();
    scheduleLocateSelectedItemInPdf();
  });

  document.getElementById("pdfPrev").addEventListener("click", async () => {
    if (!STATE.pdfDoc) {
      return;
    }
    STATE.pdfPage = Math.max(1, STATE.pdfPage - 1);
    STATE.highlightSpec = null;
    await renderPdfPage();
  });

  document.getElementById("pdfNext").addEventListener("click", async () => {
    if (!STATE.pdfDoc) {
      return;
    }
    STATE.pdfPage = Math.min(STATE.pdfDoc.numPages, STATE.pdfPage + 1);
    STATE.highlightSpec = null;
    await renderPdfPage();
  });

  document.getElementById("pdfZoomOut").addEventListener("click", async () => {
    if (!STATE.pdfDoc) {
      return;
    }
    STATE.pdfViewCustomized = true;
    STATE.pdfFitMode = false;
    STATE.pdfScale = Math.max(0.55, Number((STATE.pdfScale - 0.12).toFixed(2)));
    await renderPdfPage();
  });

  document.getElementById("pdfZoomIn").addEventListener("click", async () => {
    if (!STATE.pdfDoc) {
      return;
    }
    STATE.pdfViewCustomized = true;
    STATE.pdfFitMode = false;
    STATE.pdfScale = Math.min(2.6, Number((STATE.pdfScale + 0.12).toFixed(2)));
    await renderPdfPage();
  });

  document.getElementById("pdfFitToggle").addEventListener("click", async () => {
    STATE.pdfViewCustomized = true;
    STATE.pdfFitMode = !STATE.pdfFitMode;
    await renderPdfPage();
  });

  document.getElementById("pdfRelocate").addEventListener("click", async () => {
    await locateSelectedItemInPdf(true);
  });

  document.getElementById("itemPrev").addEventListener("click", async () => {
    await moveItemSelection(-1);
  });
  document.getElementById("itemNext").addEventListener("click", async () => {
    await moveItemSelection(1);
  });
  document.getElementById("itemListToggle").addEventListener("click", () => {
    STATE.itemListCollapsed = !STATE.itemListCollapsed;
    renderReview();
  });

  const pdfStage = document.getElementById("pdfStage");
  if (pdfStage) {
    pdfStage.addEventListener(
      "scroll",
      () => {
        STATE.pdfStageScrollLeft = pdfStage.scrollLeft;
        STATE.pdfStageScrollTop = pdfStage.scrollTop;
        if (pdfStage.scrollLeft > 0 || pdfStage.scrollTop > 0) {
          STATE.pdfViewCustomized = true;
        }
      },
      { passive: true }
    );
  }

  window.addEventListener("keydown", async (event) => {
    if (isTypingTarget(event.target)) {
      return;
    }
    const key = String(event.key || "").toLowerCase();
    if (key === "j") {
      event.preventDefault();
      await moveItemSelection(1);
      return;
    }
    if (key === "k") {
      event.preventDefault();
      await moveItemSelection(-1);
      return;
    }
    if (key === "a") {
      event.preventDefault();
      if (STATE.pdfDoc) {
        STATE.pdfPage = Math.max(1, STATE.pdfPage - 1);
        STATE.highlightSpec = null;
        await renderPdfPage();
      }
      return;
    }
    if (key === "d") {
      event.preventDefault();
      if (STATE.pdfDoc) {
        STATE.pdfPage = Math.min(STATE.pdfDoc.numPages, STATE.pdfPage + 1);
        STATE.highlightSpec = null;
        await renderPdfPage();
      }
      return;
    }
    if (key === "r") {
      event.preventDefault();
      await locateSelectedItemInPdf(true);
    }
  });

  window.addEventListener("pointermove", (event) => {
    updateFormulaOverlayDrag(event);
  });
  window.addEventListener("pointerup", () => {
    stopFormulaOverlayDrag();
  });
  window.addEventListener("pointercancel", () => {
    stopFormulaOverlayDrag();
  });
}

function bindPdfStageAutoFit() {
  const stage = document.getElementById("pdfStage");
  if (!stage || typeof ResizeObserver === "undefined") {
    return;
  }
  if (PDF_STAGE_RESIZE_OBSERVER) {
    PDF_STAGE_RESIZE_OBSERVER.disconnect();
    PDF_STAGE_RESIZE_OBSERVER = null;
  }
  PDF_STAGE_RESIZE_OBSERVER = new ResizeObserver(() => {
    if (!STATE.pdfDoc || !STATE.pdfFitMode) {
      return;
    }
    if (PDF_STAGE_RESIZE_TIMER) {
      window.clearTimeout(PDF_STAGE_RESIZE_TIMER);
    }
    PDF_STAGE_RESIZE_TIMER = window.setTimeout(() => {
      renderPdfPage().catch((error) => {
        console.warn("pdf stage refit failed", error);
      });
    }, 90);
  });
  PDF_STAGE_RESIZE_OBSERVER.observe(stage);
}

function scheduleLocateSelectedItemInPdf(delayMs = 180) {
  if (SEARCH_LOCATE_TIMER) {
    window.clearTimeout(SEARCH_LOCATE_TIMER);
  }
  SEARCH_LOCATE_TIMER = window.setTimeout(() => {
    SEARCH_LOCATE_TIMER = null;
    locateSelectedItemInPdf(true).catch((error) => {
      console.warn("scheduled pdf locate failed", error);
    });
  }, delayMs);
}

function isTypingTarget(target) {
  if (!(target instanceof HTMLElement)) {
    return false;
  }
  const tagName = target.tagName.toLowerCase();
  return tagName === "input" || tagName === "textarea" || tagName === "select" || Boolean(target.isContentEditable);
}

function switchSection(sectionId) {
  STATE.section = sectionId;
  const isReview = sectionId === "review";
  document.getElementById("reviewSection").classList.toggle("hidden", !isReview);
  document.getElementById("flowSection").classList.toggle("hidden", isReview);
  document.getElementById("navReview").classList.toggle("is-active", isReview);
  document.getElementById("navFlow").classList.toggle("is-active", !isReview);
}

function renderHero() {
  const chapters = DATA.review?.chapters || [];
  const statuses = { pending: 0, pass: 0, fail: 0 };
  Object.values(REVIEW_RECORDS).forEach((record) => {
    statuses[record.status] = (statuses[record.status] || 0) + 1;
  });
  const sourceVersion = currentSourceVersion();
  const chapterFilter = Array.isArray(DATA.review?.chapter_filter) ? DATA.review.chapter_filter : chapters.map((chapter) => chapter.id);
  const chapterText = chapterFilter.length <= 7 ? chapterFilter.join(", ") : `${chapterFilter.slice(0, 7).join(", ")}…`;

  const heroMeta = document.getElementById("heroMeta");
  heroMeta.innerHTML = [
    metricCard("源版本", sourceVersion, DATA.review?.structured_dir || "structured"),
    metricCard("章节数", String(chapters.length), chapterText || "未过滤"),
    metricCard("待确认", String(statuses.pending || 0), "优先处理"),
    metricCard("不通过", String(statuses.fail || 0), "需复核"),
    metricCard("通过", String(statuses.pass || 0), "已确认"),
  ].join("");
}

function renderChapterOptions() {
  const select = document.getElementById("chapterSelect");
  const chapters = DATA.review?.chapters || [];
  select.innerHTML = chapters
    .map((chapter) => `<option value="${escapeHtml(chapter.id)}">${escapeHtml(chapter.label)}</option>`)
    .join("");
  if (STATE.chapterId) {
    select.value = STATE.chapterId;
  }
}

function renderViewTabs() {
  const root = document.getElementById("viewTabs");
  const views = DATA.review?.views || [];
  root.innerHTML = views
    .map(
      (view) =>
        `<button class="${view.id === STATE.viewId ? "is-active" : ""}" type="button" data-view-id="${escapeHtml(view.id)}">${escapeHtml(
          view.label
        )}</button>`
    )
    .join("");
  root.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", async () => {
      STATE.viewId = button.dataset.viewId;
      STATE.selectedItemId = null;
      STATE.selectedItemKey = null;
      STATE.lastLocatedItemKey = null;
      STATE.candidatePages = [];
      renderViewTabs();
      renderReview();
      await locateSelectedItemInPdf(true);
    });
  });
}

function currentChapterMeta() {
  return chapterMetaById(STATE.chapterId);
}

function chapterMetaById(chapterId) {
  const normalizedChapterId = String(chapterId || "").trim().toLowerCase();
  return (DATA.review?.chapters || []).find((chapter) => chapter.id === normalizedChapterId) || null;
}

function itemChapterId(item) {
  return String(item?.chapter || STATE.chapterId || "").trim().toLowerCase();
}

function currentItemsRaw() {
  return DATA.review?.data?.[STATE.chapterId]?.[STATE.viewId] || [];
}

function currentSourceVersion() {
  const raw = DATA.review?.structured_source_version || DATA.review?.source_version || "current_data";
  const cleaned = String(raw || "current_data")
    .trim()
    .replace(/[^\w.-]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return cleaned || "current_data";
}

function compactText(value, limit = 90) {
  const text = String(value || "")
    .replace(/\s+/g, " ")
    .trim();
  if (!text || text.length <= limit) {
    return text;
  }
  return `${text.slice(0, Math.max(0, limit - 1)).trim()}…`;
}

function formatGuideNumber(value, digits = 2) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(digits) : "";
}

function sourcePageHintText(item) {
  const locator = item?.locator || {};
  const hints = [];
  if (locator.toc_page_hint) {
    hints.push(`小节锚点 P${locator.toc_page_hint}`);
  }
  if (locator.toc_chapter_page) {
    hints.push(`章节起始 P${locator.toc_chapter_page}`);
  }
  if (item?.source_page) {
    hints.push(`source_page ${item.source_page}`);
  }
  return hints.join(" · ") || "无页码锚点";
}

function sourceTermsText(item, limit = 5) {
  const locatorTerms = Array.isArray(item?.locator?.terms) ? item.locator.terms : [];
  const searchKeys = Array.isArray(item?.search_keys) ? item.search_keys : [];
  const terms = [...locatorTerms, ...searchKeys]
    .map((term) => compactText(term, 42))
    .filter(Boolean);
  return Array.from(new Set(terms)).slice(0, limit).join(" · ");
}

function itemSourceGuideBrief(item) {
  const locator = item?.locator || {};
  const sourceUnit = locator.source_unit_id || item?.source_unit_id || "-";
  const subsection = compactText(locator.subsection || item?.subtitle || "", 58);
  const pageHint = sourcePageHintText(item);
  return `${pageHint} · ${sourceUnit}${subsection ? ` · ${subsection}` : ""}`;
}

function recordKeyForItem(item) {
  const baseKey = item?.item_key || `${itemChapterId(item)}::${STATE.viewId}::${item?.id || ""}`;
  const prefix = currentSourceVersion();
  return String(baseKey).startsWith(`${prefix}::`) ? String(baseKey) : `${prefix}::${baseKey}`;
}

function recordForItem(item) {
  return REVIEW_RECORDS[recordKeyForItem(item)] || null;
}

function normalizeIssuePayload(rawIssue) {
  if (!rawIssue || typeof rawIssue !== "object") {
    return null;
  }
  const issueCode = String(rawIssue.issue_code || "").trim();
  const badSpan = String(rawIssue.bad_span || "").trim();
  const expected = String(rawIssue.expected || "").trim();
  const context = String(rawIssue.context || "").trim();
  const targetId = String(rawIssue.target_id || "").trim();
  const evidence = String(rawIssue.evidence || "").trim();
  const note = String(rawIssue.note || "").trim();
  if (!issueCode && !badSpan && !expected && !context && !targetId && !evidence && !note) {
    return null;
  }
  const severity = ["info", "warning", "error", "fatal"].includes(String(rawIssue.severity || "").toLowerCase())
    ? String(rawIssue.severity).toLowerCase()
    : "warning";
  return {
    id: String(rawIssue.id || cryptoRandomId()).trim() || cryptoRandomId(),
    issue_code: issueCode || "uncategorized",
    issue_label: String(rawIssue.issue_label || "").trim(),
    scope: String(rawIssue.scope || "").trim(),
    severity,
    bad_span: badSpan,
    expected,
    context,
    target_id: targetId,
    evidence,
    note,
    created_at: typeof rawIssue.created_at === "string" ? rawIssue.created_at : new Date().toISOString(),
    item_snapshot: rawIssue.item_snapshot && typeof rawIssue.item_snapshot === "object" ? rawIssue.item_snapshot : {},
  };
}

function slugIssueCode(value) {
  const text = String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^\w]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return text || `issue_${cryptoRandomId().slice(0, 8)}`;
}

function normalizeRecordPayload(payload) {
  const source = payload && typeof payload === "object" ? payload : {};
  const records = {};
  const rawRecords = source.records && typeof source.records === "object" ? source.records : {};
  Object.entries(rawRecords).forEach(([key, value]) => {
    if (!value || typeof value !== "object") {
      return;
    }
    const status = ["pending", "pass", "fail"].includes(value.status) ? value.status : "pending";
    const statusUpdatedAt = typeof value.status_updated_at === "string" ? value.status_updated_at : new Date().toISOString();
    const notes = Array.isArray(value.notes)
      ? value.notes
          .map((note) => {
            if (!note || typeof note !== "object") {
              return null;
            }
            const text = String(note.text || "").trim();
            if (!text) {
              return null;
            }
            return {
              id: String(note.id || cryptoRandomId()).trim() || cryptoRandomId(),
              text,
              created_at: typeof note.created_at === "string" ? note.created_at : new Date().toISOString(),
            };
          })
          .filter(Boolean)
      : [];
    const issues = Array.isArray(value.issues) ? value.issues.map(normalizeIssuePayload).filter(Boolean) : [];
    records[String(key)] = { status, status_updated_at: statusUpdatedAt, notes, issues };
  });
  return records;
}

function normalizeCategory(rawCategory) {
  if (!rawCategory || typeof rawCategory !== "object") {
    return null;
  }
  const issueCode = slugIssueCode(rawCategory.issue_code || rawCategory.label || "");
  if (!issueCode) {
    return null;
  }
  const status = ["manual_only", "candidate", "active"].includes(String(rawCategory.status || "").toLowerCase())
    ? String(rawCategory.status).toLowerCase()
    : "manual_only";
  const severity = ["info", "warning", "error", "fatal"].includes(String(rawCategory.severity || "").toLowerCase())
    ? String(rawCategory.severity).toLowerCase()
    : "warning";
  const detector = rawCategory.detector && typeof rawCategory.detector === "object" ? rawCategory.detector : {};
  const patterns = Array.isArray(detector.patterns) ? detector.patterns.map((pattern) => String(pattern)).filter(Boolean) : [];
  return {
    issue_code: issueCode,
    label: String(rawCategory.label || issueCode).trim(),
    scope: String(rawCategory.scope || "text").trim(),
    description: String(rawCategory.description || "").trim(),
    severity,
    status,
    aliases: Array.isArray(rawCategory.aliases) ? rawCategory.aliases.map((alias) => String(alias).trim()).filter(Boolean) : [],
    examples: Array.isArray(rawCategory.examples) ? rawCategory.examples : [],
    detector: {
      mode: String(detector.mode || "regex").trim() || "regex",
      patterns,
    },
  };
}

function normalizeTaxonomyPayload(payload) {
  const source = payload && typeof payload === "object" ? payload : FALLBACK_ISSUE_TAXONOMY;
  const seen = new Set();
  const categories = (Array.isArray(source.categories) ? source.categories : FALLBACK_ISSUE_TAXONOMY.categories)
    .map(normalizeCategory)
    .filter((category) => {
      if (!category || seen.has(category.issue_code)) {
        return false;
      }
      seen.add(category.issue_code);
      return true;
    });
  return {
    version: Number(source.version || 1),
    updated_at: typeof source.updated_at === "string" ? source.updated_at : new Date().toISOString(),
    categories: categories.length ? categories : FALLBACK_ISSUE_TAXONOMY.categories,
  };
}

async function hydrateIssueTaxonomy() {
  try {
    const response = await fetch(ISSUE_TAXONOMY_ENDPOINT, { cache: "no-store" });
    if (response.ok) {
      ISSUE_TAXONOMY = normalizeTaxonomyPayload(await response.json());
      return;
    }
  } catch (error) {
    console.warn("failed to load issue taxonomy", error);
  }
  ISSUE_TAXONOMY = normalizeTaxonomyPayload(FALLBACK_ISSUE_TAXONOMY);
}

async function persistIssueTaxonomy() {
  try {
    const payload = {
      ...ISSUE_TAXONOMY,
      updated_at: new Date().toISOString(),
    };
    const response = await fetch(ISSUE_TAXONOMY_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    ISSUE_TAXONOMY = normalizeTaxonomyPayload(await response.json());
  } catch (error) {
    console.warn("failed to persist issue taxonomy", error);
  }
}

async function hydrateReviewRecords() {
  try {
    const response = await fetch(REVIEW_RECORDS_ENDPOINT, { cache: "no-store" });
    if (response.ok) {
      const payload = await response.json();
      REVIEW_RECORDS = normalizeRecordPayload(payload);
      SYNC_NOTICE = "审核记录已连接本地文件并自动持久化。";
      return;
    }
  } catch (error) {
    console.warn("failed to load review records", error);
  }
  REVIEW_RECORDS = {};
  SYNC_NOTICE = "审核记录当前只在浏览器会话中保存，建议用 python knowledge_engineering/review_app/serve_review_app.py 启动。";
}

async function persistReviewRecords() {
  try {
    const payload = {
      version: 1,
      updated_at: new Date().toISOString(),
      records: REVIEW_RECORDS,
    };
    const response = await fetch(REVIEW_RECORDS_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    REVIEW_RECORDS = normalizeRecordPayload(await response.json());
    SYNC_NOTICE = "审核记录已写回本地文件。";
  } catch (error) {
    console.warn("failed to persist review records", error);
    SYNC_NOTICE = "写回本地文件失败，当前改动仅保留在浏览器会话。";
  }
}

function ensureRecord(item) {
  const key = recordKeyForItem(item);
  if (!REVIEW_RECORDS[key]) {
    REVIEW_RECORDS[key] = {
      status: "pending",
      status_updated_at: new Date().toISOString(),
      notes: [],
      issues: [],
    };
  }
  if (!Array.isArray(REVIEW_RECORDS[key].issues)) {
    REVIEW_RECORDS[key].issues = [];
  }
  if (!Array.isArray(REVIEW_RECORDS[key].notes)) {
    REVIEW_RECORDS[key].notes = [];
  }
  return REVIEW_RECORDS[key];
}

function statusOfItem(item) {
  const key = recordKeyForItem(item);
  return REVIEW_RECORDS[key]?.status || "pending";
}

function filteredItems() {
  const query = normalizeMatchText(STATE.searchQuery);
  const rows = currentItemsRaw().filter((item) => {
    const status = statusOfItem(item);
    if (STATE.statusFilter !== "all" && status !== STATE.statusFilter) {
      return false;
    }
    if (!query) {
      return true;
    }
    const haystack = normalizeMatchText(
      [
        item.id,
        item.title,
        item.subtitle,
        item.excerpt,
        ...(item.search_keys || []),
        ...((item.locator && item.locator.terms) || []),
      ]
        .filter(Boolean)
        .join(" ")
    );
    return haystack.includes(query);
  });

  rows.sort((left, right) => {
    const leftStatus = statusOfItem(left);
    const rightStatus = statusOfItem(right);
    const statusDelta = (STATUS_PRIORITY[leftStatus] || 99) - (STATUS_PRIORITY[rightStatus] || 99);
    if (statusDelta !== 0) {
      return statusDelta;
    }
    return String(left.id).localeCompare(String(right.id), "en");
  });
  return rows;
}

function ensureSelectionInItems(items) {
  if (!items.length) {
    STATE.selectedItemId = null;
    STATE.selectedItemKey = null;
    return null;
  }

  let selected = items.find((item) => item.id === STATE.selectedItemId) || null;
  if (!selected) {
    selected = items[0];
    STATE.selectedItemId = selected.id;
    STATE.selectedItemKey = selected.item_key || recordKeyForItem(selected);
  }
  return selected;
}

function renderReview() {
  const chapterMeta = currentChapterMeta();
  const chapterLabel = chapterMeta?.label || "-";
  const allRows = currentItemsRaw();
  const rows = filteredItems();
  const selected = ensureSelectionInItems(rows);
  const reviewPane = document.querySelector(".review-pane");
  if (reviewPane) {
    reviewPane.classList.toggle("list-collapsed", Boolean(STATE.itemListCollapsed));
  }
  const itemListToggle = document.getElementById("itemListToggle");
  if (itemListToggle) {
    itemListToggle.textContent = STATE.itemListCollapsed ? "展开列表" : "收起列表";
  }

  document.getElementById("itemListTitle").textContent = `${chapterLabel} · ${viewLabel(STATE.viewId)}`;
  document.getElementById("itemListCount").textContent = `${rows.length} / ${allRows.length}`;
  renderReviewStats(allRows);
  renderItemList(rows);
  renderReviewDetail(selected);
  renderCandidatePages();
  renderChunkLegend();

  renderHero();
  renderChapterOptions();
}

function renderReviewStats(rows) {
  const root = document.getElementById("reviewStats");
  const counts = { pending: 0, pass: 0, fail: 0 };
  const issueCounts = {};
  let issueTotal = 0;
  rows.forEach((item) => {
    counts[statusOfItem(item)] += 1;
    const record = recordForItem(item);
    const issues = Array.isArray(record?.issues) ? record.issues : [];
    issueTotal += issues.length;
    issues.forEach((issue) => {
      const code = issue.issue_code || "uncategorized";
      issueCounts[code] = (issueCounts[code] || 0) + 1;
    });
  });
  const topIssue = Object.entries(issueCounts).sort((left, right) => right[1] - left[1])[0];
  root.innerHTML = [
    metricCard("总条目", String(rows.length), "当前章节 + 当前视图"),
    metricCard("待确认", String(counts.pending), "优先处理"),
    metricCard("不通过", String(counts.fail), "需要修订"),
    metricCard("通过", String(counts.pass), "审核完成"),
    metricCard("问题记录", String(issueTotal), "结构化 issue"),
    metricCard("高频分类", topIssue ? `${topIssue[0]} · ${topIssue[1]}` : "-", "当前列表"),
  ].join("");
}

function renderItemList(allItems) {
  const root = document.getElementById("itemList");
  if (!allItems.length) {
    root.innerHTML = '<div class="placeholder">当前筛选条件下没有条目。</div>';
    return;
  }
  root.innerHTML = allItems
    .map((item) => {
      const status = statusOfItem(item);
      const sourceGuide = itemSourceGuideBrief(item);
      return `<button type="button" class="item-pill ${item.id === STATE.selectedItemId ? "is-active" : ""}" data-item-id="${escapeHtml(
        item.id
      )}">
        <div class="item-pill-title">${escapeHtml(item.id)}</div>
        <div class="small-text">${escapeHtml(compactText(item.subtitle || item.title || "-", 78))}</div>
        <div class="item-pill-meta">${escapeHtml(sourceGuide)}</div>
        <span class="status-chip ${STATUS_CLASS[status]}">${escapeHtml(STATUS_LABELS[status])}</span>
      </button>`;
    })
    .join("");

  root.querySelectorAll(".item-pill").forEach((button) => {
    button.addEventListener("click", async () => {
      STATE.selectedItemId = button.dataset.itemId;
      const selected = allItems.find((item) => item.id === STATE.selectedItemId);
      STATE.selectedItemKey = selected?.item_key || null;
      renderReview();
      await locateSelectedItemInPdf(true);
    });
  });

  const active = root.querySelector(".item-pill.is-active");
  if (active) {
    active.scrollIntoView({ block: "nearest" });
  }
}

function findItemById(itemId) {
  return currentItemsRaw().find((item) => item.id === itemId) || null;
}

function pickAdjacentItemId(items, currentItemId, delta) {
  if (!Array.isArray(items) || !items.length) {
    return null;
  }
  const currentIndex = items.findIndex((row) => row.id === currentItemId);
  if (currentIndex < 0) {
    return items[0]?.id || null;
  }
  const nextIndex = Math.max(0, Math.min(items.length - 1, currentIndex + delta));
  return items[nextIndex]?.id || null;
}

async function advanceSelectionAfterReview(currentItemId, preferredNextItemId) {
  let nextItemId = preferredNextItemId || null;
  if (!nextItemId) {
    const itemsBefore = filteredItems();
    nextItemId = pickAdjacentItemId(itemsBefore, currentItemId, 1);
  }
  if (nextItemId) {
    const nextItem = findItemById(nextItemId);
    STATE.selectedItemId = nextItemId;
    STATE.selectedItemKey = nextItem?.item_key || (nextItem ? recordKeyForItem(nextItem) : null);
  }
  renderReview();
  await locateSelectedItemInPdf(true);
}

function taxonomyCategories() {
  return Array.isArray(ISSUE_TAXONOMY?.categories) ? ISSUE_TAXONOMY.categories : [];
}

function categoryByCode(issueCode) {
  return taxonomyCategories().find((category) => category.issue_code === issueCode) || null;
}

function issueRecordSnapshotForItem(item) {
  return {
    chapter: itemChapterId(item),
    view: STATE.viewId,
    item_id: item?.id || "",
    item_key: item?.item_key || recordKeyForItem(item),
    source_version: currentSourceVersion(),
  };
}

function selectedTextForReviewDetail(root) {
  const selection = window.getSelection?.();
  if (!selection || selection.rangeCount === 0) {
    return "";
  }
  const range = selection.getRangeAt(0);
  if (!root.contains(range.commonAncestorContainer)) {
    return "";
  }
  return String(selection.toString() || "").trim();
}

function issueHistoryHtml(record) {
  const issues = Array.isArray(record?.issues) ? [...record.issues] : [];
  issues.sort((left, right) => String(right.created_at).localeCompare(String(left.created_at)));
  return issues
    .map(
      (issue) => `<article class="issue-card">
        <div class="note-time">${escapeHtml(formatTime(issue.created_at))}</div>
        <div class="issue-title">
          <strong>${escapeHtml(issue.issue_label || issue.issue_code || "uncategorized")}</strong>
          <span class="status-chip ${issue.severity === "fatal" || issue.severity === "error" ? "status-fail" : "status-pending"}">${escapeHtml(
            ISSUE_SEVERITY_LABELS[issue.severity] || issue.severity || "警告"
          )}</span>
        </div>
        <div class="small-text">${escapeHtml(`${issue.issue_code || "uncategorized"} · ${issue.scope || "-"} · ${issue.bad_span || "-"}`)}</div>
        ${
          issue.item_snapshot && typeof issue.item_snapshot === "object"
            ? `<div class="small-text">来源：${escapeHtml(
                [
                  issue.item_snapshot.source_version || "-",
                  issue.item_snapshot.chapter || "-",
                  issue.item_snapshot.view || "-",
                  issue.item_snapshot.item_id || "-",
                ].join(" · ")
              )}</div>`
            : ""
        }
        ${issue.target_id ? `<div class="issue-target">目标/归属：${escapeHtml(issue.target_id)}</div>` : ""}
        ${issue.expected ? `<div class="issue-expected">期望：${escapeHtml(issue.expected)}</div>` : ""}
        ${issue.context ? `<div class="issue-context">${escapeHtml(issue.context)}</div>` : ""}
        ${issue.evidence ? `<div class="issue-evidence">证据：${escapeHtml(issue.evidence)}</div>` : ""}
        ${issue.note ? `<div class="issue-note">${escapeHtml(issue.note)}</div>` : ""}
      </article>`
    )
    .join("");
}

function issueCategoryOptionsHtml(selectedCode = "") {
  const categories = taxonomyCategories();
  const options = categories
    .map((category) => {
      const label = `${category.label || category.issue_code} · ${category.scope || "text"} · ${category.status || "manual_only"}`;
      const isSelected = category.issue_code === selectedCode;
      return `<option value="${escapeHtml(category.issue_code)}"${isSelected ? " selected" : ""} data-scope="${escapeHtml(
        category.scope || "text"
      )}" data-label="${escapeHtml(category.label || category.issue_code)}" data-severity="${escapeHtml(
        category.severity || "warning"
      )}">${escapeHtml(label)}</option>`;
    })
    .join("");
  return `<option value="">请选择分类</option>${options}<option value="__new__">新建分类…</option>`;
}

function issueScopeOptionsHtml(selectedScope = "") {
  return ISSUE_SCOPE_OPTIONS.map(
    ([value, label]) => `<option value="${escapeHtml(value)}"${value === selectedScope ? " selected" : ""}>${escapeHtml(label)}</option>`
  ).join("");
}

function issueSeverityOptionsHtml(selectedSeverity = "warning") {
  return Object.entries(ISSUE_SEVERITY_LABELS)
    .map(([value, label]) => `<option value="${escapeHtml(value)}"${value === selectedSeverity ? " selected" : ""}>${escapeHtml(label)}</option>`)
    .join("");
}

function guideRowHtml(label, value) {
  const displayValue = compactText(value, 160) || "-";
  return `<div class="source-guide-row">
    <span>${escapeHtml(label)}</span>
    <strong class="chunk-math-text">${escapeHtml(displayValue)}</strong>
  </div>`;
}

function renderSourceGuide(item) {
  const locator = item?.locator || {};
  const sourceTerms = sourceTermsText(item, 6) || "-";
  const matchScore = formatGuideNumber(locator.toc_match_score, 3);
  const tocMatch = locator.toc_match_title
    ? `${locator.toc_match_title}${matchScore ? ` · score ${matchScore}` : ""}`
    : matchScore
      ? `score ${matchScore}`
      : "-";
  const rows = [
    ["源版本", currentSourceVersion()],
    ["章节/视图", `${chapterMetaById(itemChapterId(item))?.label || itemChapterId(item)} · ${viewLabel(STATE.viewId)}`],
    ["原文页码指引", sourcePageHintText(item)],
    ["小节锚点", locator.subsection || item.subtitle || "-"],
    ["TOC 匹配", tocMatch],
    ["source.unit_id", locator.source_unit_id || item.source_unit_id || "-"],
    ["定位关键词", sourceTerms],
    ["record key", recordKeyForItem(item)],
  ];
  return `<section class="source-guide">
    <div class="source-guide-title">原文指引</div>
    <div class="source-guide-grid">${rows.map(([label, value]) => guideRowHtml(label, value)).join("")}</div>
  </section>`;
}

function renderReviewDetail(item) {
  const root = document.getElementById("reviewDetail");
  if (!item) {
    root.innerHTML = '<div class="placeholder">请选择条目开始审核。</div>';
    return;
  }

  const record = ensureRecord(item);
  const detailHtml = renderItemPayload(item);
  const noteHistory = [...record.notes]
    .sort((left, right) => String(right.created_at).localeCompare(String(left.created_at)))
    .map(
      (note) => `<article class="note-card">
        <div class="note-time">${escapeHtml(formatTime(note.created_at))}</div>
        <div>${escapeHtml(note.text)}</div>
      </article>`
    )
    .join("");
  const selectedCategoryCode = "";

  root.innerHTML = `
    <div class="card-header">
      <div>
        <h3>${escapeHtml(item.id)}</h3>
        <div class="small-text">${escapeHtml(item.subtitle || item.title || "-")}</div>
      </div>
      <span class="status-chip ${STATUS_CLASS[record.status]}">${escapeHtml(STATUS_LABELS[record.status])}</span>
    </div>
    ${renderSourceGuide(item)}
    ${detailHtml}
    <div class="status-actions">
      ${["pending", "pass", "fail"]
        .map(
          (status) =>
            `<button type="button" class="${record.status === status ? "is-active" : ""}" data-set-status="${status}">${escapeHtml(
              STATUS_LABELS[status]
            )}</button>`
        )
        .join("")}
    </div>
    <div class="issue-form">
      <div class="issue-form-title">
        <strong>审核记录</strong>
        <span class="small-text">通过项可只点“通过”；不通过或待确认项建议补全下列表单。</span>
      </div>
      <div class="issue-form-grid">
        <label>
          问题分类
          <select id="issueCategorySelect">${issueCategoryOptionsHtml(selectedCategoryCode)}</select>
        </label>
        <div id="newCategoryPanel" class="new-category-fields is-hidden">
          <label>
            新建分类代码
            <input id="issueNewCode" type="text" placeholder="例如 table_row_group_misattribution" />
          </label>
          <label>
            新建分类名称
            <input id="issueNewLabel" type="text" placeholder="例如 表格行归属错误" />
          </label>
        </div>
        <label>
          问题范围
          <select id="issueScopeSelect">${issueScopeOptionsHtml(categoryByCode(selectedCategoryCode)?.scope || "text")}</select>
        </label>
        <label>
          严重级别
          <select id="issueSeveritySelect">${issueSeverityOptionsHtml(categoryByCode(selectedCategoryCode)?.severity || "warning")}</select>
        </label>
        <label>
          错误片段
          <textarea id="issueBadSpan" rows="2" placeholder="选中文字后可一键填入"></textarea>
        </label>
        <label>
          正确结果
          <textarea id="issueExpected" rows="2" placeholder="应该是什么；可写正确公式、正确表格归属、正确 chunk 边界"></textarea>
        </label>
        <label>
          上下文
          <textarea id="issueContext" rows="2" placeholder="建议保留前后各一句，或表格相邻行/列"></textarea>
        </label>
        <label>
          目标/归属
          <input id="issueTargetId" type="text" placeholder="例如 formula 6.8 / table 6.1 / chapter6_004 后应回链" />
        </label>
        <label>
          证据
          <textarea id="issueEvidence" rows="2" placeholder="原文页码、Paddle/GLM 差异、表格行列位置、判断依据"></textarea>
        </label>
        <label>
          审核说明/备注
          <textarea id="issueNote" rows="2" placeholder="一句话说明问题和修复建议；无分类时会作为普通备注保存"></textarea>
        </label>
      </div>
      <div class="issue-form-actions">
        <button type="button" id="captureSelectionBtn">捕获选中文本</button>
        <button type="button" id="saveIssueBtn">保存审核记录</button>
      </div>
      <div class="small-text">保存后会同步到本地 <code>review_records.json</code>。分类为空但备注非空时，只追加普通备注；选择分类后会写入结构化 issue。</div>
    </div>
    <div class="issue-history">
      ${issueHistoryHtml(record) || '<div class="placeholder">暂无结构化问题记录。</div>'}
    </div>
    <div class="note-history">
      ${noteHistory || '<div class="placeholder">暂无备注历史。</div>'}
    </div>
    <div class="sync-note">${escapeHtml(SYNC_NOTICE)}</div>
  `;

  root.querySelectorAll("[data-set-status]").forEach((button) => {
    button.addEventListener("click", async () => {
      const status = button.dataset.setStatus;
      const preferredNextItemId = pickAdjacentItemId(filteredItems(), item.id, 1);
      const target = ensureRecord(item);
      target.status = status;
      target.status_updated_at = new Date().toISOString();
      await persistReviewRecords();
      await advanceSelectionAfterReview(item.id, preferredNextItemId);
    });
  });

  const issueCategorySelect = root.querySelector("#issueCategorySelect");
  const issueNewCode = root.querySelector("#issueNewCode");
  const issueNewLabel = root.querySelector("#issueNewLabel");
  const newCategoryPanel = root.querySelector("#newCategoryPanel");
  const issueScopeSelect = root.querySelector("#issueScopeSelect");
  const issueSeveritySelect = root.querySelector("#issueSeveritySelect");
  const issueBadSpan = root.querySelector("#issueBadSpan");
  const issueExpected = root.querySelector("#issueExpected");
  const issueContext = root.querySelector("#issueContext");
  const issueTargetId = root.querySelector("#issueTargetId");
  const issueEvidence = root.querySelector("#issueEvidence");
  const issueNote = root.querySelector("#issueNote");
  const captureSelectionBtn = root.querySelector("#captureSelectionBtn");
  const saveIssueBtn = root.querySelector("#saveIssueBtn");

  const toggleNewCategoryPanel = () => {
    if (newCategoryPanel) {
      newCategoryPanel.classList.toggle("is-hidden", issueCategorySelect?.value !== "__new__");
    }
  };

  const syncCategoryDefaults = () => {
    const category = categoryByCode(issueCategorySelect?.value || "");
    if (category) {
      issueScopeSelect.value = category.scope || "text";
      issueSeveritySelect.value = category.severity || "warning";
    }
  };
  syncCategoryDefaults();
  toggleNewCategoryPanel();

  if (issueCategorySelect) {
    issueCategorySelect.addEventListener("change", () => {
      if (issueCategorySelect.value === "__new__") {
        issueNewCode.value = "";
        issueNewLabel.value = "";
        issueScopeSelect.value = "text";
        issueSeveritySelect.value = "warning";
        toggleNewCategoryPanel();
        return;
      }
      toggleNewCategoryPanel();
      syncCategoryDefaults();
    });
  }

  if (captureSelectionBtn && issueBadSpan) {
    captureSelectionBtn.addEventListener("click", () => {
      const text = selectedTextForReviewDetail(root);
      if (text) {
        issueBadSpan.value = text;
      }
    });
  }

  if (saveIssueBtn) {
    saveIssueBtn.addEventListener("click", async () => {
      const selectedCode = String(issueCategorySelect?.value || "").trim();
      const selectedCategory = selectedCode && selectedCode !== "__new__" ? categoryByCode(selectedCode) : null;
      const rawCustomCode = String(issueNewCode?.value || issueNewLabel?.value || "").trim();
      const badSpan = String(issueBadSpan?.value || "").trim();
      const expected = String(issueExpected?.value || "").trim();
      const context = String(issueContext?.value || "").trim();
      const targetId = String(issueTargetId?.value || "").trim();
      const evidence = String(issueEvidence?.value || "").trim();
      const note = String(issueNote?.value || "").trim();
      const hasIssueDetail = Boolean(selectedCategory || rawCustomCode || badSpan || expected || context || targetId || evidence);
      const target = ensureRecord(item);

      if (!hasIssueDetail) {
        if (note) {
          target.notes.push({
            id: cryptoRandomId(),
            text: note,
            created_at: new Date().toISOString(),
          });
          await persistReviewRecords();
          renderReview();
        }
        return;
      }

      if (!selectedCategory && !rawCustomCode) {
        issueCategorySelect?.focus();
        return;
      }

      const issueCode = selectedCategory ? selectedCategory.issue_code : slugIssueCode(rawCustomCode);
      if (!issueCode) {
        return;
      }
      const issueLabel = selectedCategory?.label || String(issueNewLabel?.value || issueCode).trim();
      const scope = String(issueScopeSelect?.value || selectedCategory?.scope || "text").trim();
      const severity = String(issueSeveritySelect?.value || selectedCategory?.severity || "warning").trim();
      target.issues.push({
        id: cryptoRandomId(),
        issue_code: issueCode,
        issue_label: issueLabel,
        scope,
        severity,
        bad_span: badSpan,
        expected,
        context,
        target_id: targetId,
        evidence,
        note,
        created_at: new Date().toISOString(),
        item_snapshot: issueRecordSnapshotForItem(item),
      });
      await persistReviewRecords();

      if (!selectedCategory) {
        const existing = categoryByCode(issueCode);
        if (!existing) {
          ISSUE_TAXONOMY.categories.push({
            issue_code: issueCode,
            label: issueLabel,
            scope,
            description: note || "",
            severity,
            status: "manual_only",
            examples: badSpan ? [{ bad_span: badSpan, expected, context, target_id: targetId, evidence }] : [],
            detector: { mode: "regex", patterns: [] },
          });
          await persistIssueTaxonomy();
        }
      } else {
        const existing = categoryByCode(issueCode);
        if (existing) {
          existing.examples = Array.isArray(existing.examples) ? existing.examples : [];
          if (badSpan) {
            existing.examples.push({ bad_span: badSpan, expected, context, target_id: targetId, evidence });
          }
          await persistIssueTaxonomy();
        }
      }
      renderReview();
    });
  }

  const tableToggleButton = root.querySelector("#toggleTableMath");
  if (tableToggleButton) {
    tableToggleButton.addEventListener("click", () => {
      STATE.tableMathEnabled = !STATE.tableMathEnabled;
      renderReviewDetail(item);
    });
  }

  applyMath(root);
}

function renderItemPayload(item) {
  if (STATE.viewId === "formulas") {
    return `
      <div class="formula-header-row">
        <strong>公式内容</strong>
        <span class="small-text">默认渲染</span>
      </div>
      <div class="formula-box" data-latex="${escapeHtml(item.latex || "")}"></div>
      <details class="raw-latex">
        <summary>原始 LaTeX</summary>
        <pre class="formula-raw">${escapeHtml(item.latex || "N/A")}</pre>
      </details>
      <div class="detail-meta">
        <div class="detail-row"><strong>标题:</strong> ${mathTextHtml(item.title || item.id, "inline-math-text")}</div>
        <div class="detail-row"><strong>摘要:</strong> ${mathTextHtml(item.excerpt || "-", "inline-math-text")}</div>
        <div class="detail-row"><strong>小节:</strong> ${mathTextHtml(item.locator?.subsection || item.subtitle || "-", "inline-math-text")}</div>
        <div class="detail-row"><strong>source.unit_id:</strong> ${escapeHtml(item.source_unit_id || "-")}</div>
      </div>
    `;
  }

  if (STATE.viewId === "tables") {
    const tableHtml = renderTableHtml(item.html, STATE.tableMathEnabled);
    return `
      <div class="detail-meta">
        <div class="detail-row"><strong>标题:</strong> ${mathTextHtml(item.excerpt || item.title || "-", "inline-math-text")}</div>
        <div class="detail-row"><strong>行列:</strong> ${item.row_count} × ${item.column_count}</div>
        <div class="detail-row"><strong>小节:</strong> ${mathTextHtml(item.locator?.subsection || item.subtitle || "-", "inline-math-text")}</div>
        <div class="detail-row"><strong>source.unit_id:</strong> ${escapeHtml(item.source_unit_id || "-")}</div>
      </div>
      <div class="table-render-controls">
        <strong>表格渲染</strong>
        <button
          type="button"
          id="toggleTableMath"
          class="table-render-toggle ${STATE.tableMathEnabled ? "is-active" : ""}"
        >
          数学渲染: ${STATE.tableMathEnabled ? "开" : "关"}
        </button>
      </div>
      ${tableHtml}
    `;
  }

  const blocks = (item.blocks || [])
    .map(
      (block) => `<article class="block-item">
        <div class="small-text">${escapeHtml(block.type || "unknown")} · EN</div>
        <div class="chunk-math-text">${escapeHtml(block.text || "")}</div>
        ${
          block.text_zh
            ? `<div class="small-text block-zh-label">中文</div><div class="chunk-math-text">${escapeHtml(block.text_zh)}</div>`
            : ""
        }
      </article>`
    )
    .join("");
  return `
    <div class="detail-meta">
      <div class="detail-row"><strong>标题 / Title:</strong> ${mathTextHtml(item.title || item.id, "inline-math-text")}</div>
      <div class="detail-row"><strong>摘要 / Excerpt:</strong> ${mathTextHtml(item.excerpt || "-", "inline-math-text")}</div>
      <div class="detail-row"><strong>小节 / Subsection:</strong> ${mathTextHtml(item.locator?.subsection || item.subtitle || "-", "inline-math-text")}</div>
      <div class="detail-row"><strong>公式引用 / Formula refs:</strong> ${escapeHtml((item.formula_references || []).join(", ") || "无")}</div>
      <div class="detail-row"><strong>表格引用 / Table refs:</strong> ${escapeHtml((item.table_references || []).join(", ") || "无")}</div>
      <div class="detail-row"><strong>块数量 / Block count:</strong> ${item.block_count || 0}</div>
    </div>
    <div class="block-list">${blocks || '<div class="placeholder">无 block 详情（No blocks）。</div>'}</div>
  `;
}

function mathTextHtml(value, extraClass = "") {
  const classes = ["chunk-math-text", extraClass].filter(Boolean).join(" ");
  return `<span class="${classes}">${escapeHtml(value)}</span>`;
}

async function moveItemSelection(delta) {
  const items = filteredItems();
  if (!items.length) {
    return;
  }
  const currentIndex = items.findIndex((item) => item.id === STATE.selectedItemId);
  const nextIndex = currentIndex < 0 ? 0 : Math.min(items.length - 1, Math.max(0, currentIndex + delta));
  const nextItem = items[nextIndex];
  if (!nextItem) {
    return;
  }
  STATE.selectedItemId = nextItem.id;
  STATE.selectedItemKey = nextItem.item_key || recordKeyForItem(nextItem);
  renderReview();
  await locateSelectedItemInPdf(true);
}

async function loadPdfForChapter(chapterId, requestId = null) {
  const chapterMeta = chapterMetaById(chapterId);
  if (!chapterMeta) {
    STATE.pdfDoc = null;
    updatePdfStatus("未选择可用章节。");
    return false;
  }

  if (!chapterMeta.pdf_exists || !chapterMeta.pdf_path) {
    STATE.pdfDoc = null;
    clearPdfCanvas();
    updatePdfStatus("当前章节缺少可用 PDF。");
    document.getElementById("pdfPageInfo").textContent = "- / -";
    return false;
  }

  if (!window.pdfjsLib) {
    STATE.pdfDoc = null;
    updatePdfStatus("PDF.js 未就绪。");
    return false;
  }

  if (STATE.pdfChapterId === chapterMeta.id && STATE.pdfDoc) {
    return true;
  }

  updatePdfStatus("正在加载 PDF…");
  let doc = DATA.pdfDocs.get(chapterMeta.id);
  if (!doc) {
    const url = encodeURI(chapterMeta.pdf_path);
    doc = await window.pdfjsLib.getDocument({ url }).promise;
    DATA.pdfDocs.set(chapterMeta.id, doc);
  }
  if (requestId !== null && STATE.locateRequestId !== requestId) {
    return false;
  }
  STATE.pdfDoc = doc;
  STATE.pdfChapterId = chapterMeta.id;
  STATE.pdfPage = Math.min(Math.max(1, STATE.pdfPage), doc.numPages);
  STATE.highlightSpec = null;
  STATE.candidatePages = [];
  startChapterWarmup(chapterMeta.id);
  return true;
}

function chapterCacheKey(chapterId, pageNumber) {
  return `${chapterId}::${pageNumber}`;
}

async function getPageTextCache(chapterId, pageNumber) {
  const key = chapterCacheKey(chapterId, pageNumber);
  if (DATA.pdfTextCache.has(key)) {
    return DATA.pdfTextCache.get(key);
  }

  const pdfDoc = DATA.pdfDocs.get(chapterId);
  if (!pdfDoc) {
    throw new Error(`pdf doc not loaded for ${chapterId}`);
  }
  const page = await pdfDoc.getPage(pageNumber);
  const textContent = await page.getTextContent();
  const normalizedItems = textContent.items.map((item) => ({
    ...item,
    match: normalizeMatchText(item.str || ""),
    raw: String(item.str || ""),
  }));
  const cache = {
    items: normalizedItems,
    joined: normalizedItems.map((item) => item.match).join(" "),
    rawJoined: normalizedItems.map((item) => String(item.raw || "").toLowerCase()).join(" "),
  };
  DATA.pdfTextCache.set(key, cache);
  return cache;
}

function startChapterWarmup(chapterId) {
  const pdfDoc = DATA.pdfDocs.get(chapterId);
  if (!pdfDoc) {
    return;
  }
  const status = STATE.indexWarmup[chapterId];
  if (status?.started) {
    return;
  }
  STATE.indexWarmup[chapterId] = { started: true, done: 0, total: pdfDoc.numPages, ready: false };

  (async () => {
    for (let page = 1; page <= pdfDoc.numPages; page += 1) {
      await getPageTextCache(chapterId, page);
      const warm = STATE.indexWarmup[chapterId];
      if (warm) {
        warm.done = page;
      }
    }
    const warm = STATE.indexWarmup[chapterId];
    if (warm) {
      warm.ready = true;
    }
  })().catch((error) => {
    console.warn("warmup failed", error);
  });
}

function clearPdfCanvas() {
  const canvas = document.getElementById("pdfCanvas");
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  canvas.width = 0;
  canvas.height = 0;
  clearHighlights();
  clearFormulaAuditOverlay();
}

function clearHighlights() {
  document.getElementById("pdfHighlights").innerHTML = "";
}

function clearFormulaAuditOverlay() {
  const overlay = document.getElementById("formulaAuditOverlay");
  if (!overlay) {
    return;
  }
  stopFormulaOverlayDrag();
  overlay.innerHTML = "";
  overlay.classList.add("is-hidden");
  overlay.style.left = "";
  overlay.style.top = "";
}

function textItemRect(item, viewport) {
  try {
    const tx = window.pdfjsLib.Util.transform(viewport.transform, item.transform);
    const x = tx[4];
    const y = tx[5];
    const height = Math.max(8, Math.hypot(tx[2], tx[3]) || (item.height || 10) * viewport.scale);
    const width = Math.max(8, (item.width || item.str.length * 4) * viewport.scale);
    if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(width) || !Number.isFinite(height)) {
      return null;
    }
    return { x, y: y - height, width, height };
  } catch (error) {
    console.warn("failed to build text rect", error);
    return null;
  }
}

function rectsTouch(left, right) {
  const horizontalGap = Math.max(0, Math.max(left.x, right.x) - Math.min(left.x + left.width, right.x + right.width));
  const verticalGap = Math.max(0, Math.max(left.y, right.y) - Math.min(left.y + left.height, right.y + right.height));
  return horizontalGap <= 26 && verticalGap <= 8;
}

function mergeRects(rects) {
  const sorted = [...rects].sort((a, b) => a.y - b.y || a.x - b.x);
  const merged = [];
  sorted.forEach((rect) => {
    const last = merged[merged.length - 1];
    if (last && rectsTouch(last, rect)) {
      const minX = Math.min(last.x, rect.x);
      const minY = Math.min(last.y, rect.y);
      const maxX = Math.max(last.x + last.width, rect.x + rect.width);
      const maxY = Math.max(last.y + last.height, rect.y + rect.height);
      last.x = minX;
      last.y = minY;
      last.width = maxX - minX;
      last.height = maxY - minY;
    } else {
      merged.push({ ...rect });
    }
  });
  return merged.slice(0, 24);
}

function sanitizeHighlightKind(kind) {
  const normalized = String(kind || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return normalized || "text";
}

async function renderHighlights(pageNumber, viewport) {
  clearHighlights();
  if (!STATE.highlightSpec || STATE.highlightSpec.page !== pageNumber) {
    renderChunkLegend();
    return;
  }
  const root = document.getElementById("pdfHighlights");
  const canvas = document.getElementById("pdfCanvas");
  root.style.width = `${canvas.width}px`;
  root.style.height = `${canvas.height}px`;
  root.style.left = `${canvas.offsetLeft}px`;
  root.style.top = `${canvas.offsetTop}px`;

  const boxes = Array.isArray(STATE.highlightSpec.boxes) ? STATE.highlightSpec.boxes : [];
  if (boxes.length) {
    const pixelRects = boxes
      .map((box) => normalizedBoxToRect(box, canvas.width, canvas.height))
      .filter(Boolean)
      .filter((rect) => isChunkHighlightVisible(rect.kind));
    pixelRects
      .sort((left, right) => right.width * right.height - left.width * left.height)
      .slice(0, 96)
      .forEach((rect) => appendHighlightRect(root, rect, rect.kind));
    if (!pixelRects.length) {
      updatePdfStatus("已定位 OCR 页面，但当前框坐标无效。");
    }
    renderChunkLegend();
    return;
  }

  const tokens = STATE.highlightSpec.tokens || [];
  if (!tokens.length) {
    return;
  }

  const cache = await getPageTextCache(STATE.pdfChapterId, pageNumber);
  const matchedRects = [];
  cache.items.forEach((item) => {
    if (!tokens.some((token) => token && item.match.includes(token))) {
      return;
    }
    const rect = textItemRect(item, viewport);
    if (rect) {
      matchedRects.push(rect);
    }
  });

  const mergedRects = mergeRects(matchedRects);
  mergedRects.forEach((rect) => appendHighlightRect(root, rect, "text"));
  renderChunkLegend();

  if (!mergedRects.length) {
    updatePdfStatus("已跳转页面，但未找到可高亮文本块。");
  }
}

function appendHighlightRect(root, rect, kind) {
  const node = document.createElement("div");
  const normalizedKind = sanitizeHighlightKind(kind);
  node.className = `highlight-box highlight-kind-${normalizedKind}`;
  node.style.left = `${rect.x}px`;
  node.style.top = `${rect.y}px`;
  node.style.width = `${rect.width}px`;
  node.style.height = `${rect.height}px`;
  root.appendChild(node);
}

function normalizedBoxToRect(box, canvasWidth, canvasHeight) {
  if (!box || typeof box !== "object") {
    return null;
  }
  const x = Number(box.x);
  const y = Number(box.y);
  const w = Number(box.w);
  const h = Number(box.h);
  if (![x, y, w, h].every((value) => Number.isFinite(value))) {
    return null;
  }
  const left = x <= 1 && w <= 1 ? x * canvasWidth : x;
  const top = y <= 1 && h <= 1 ? y * canvasHeight : y;
  const width = x <= 1 && w <= 1 ? w * canvasWidth : w;
  const height = y <= 1 && h <= 1 ? h * canvasHeight : h;
  if (width <= 0 || height <= 0) {
    return null;
  }
  return { x: left, y: top, width, height, kind: String(box.kind || "ocr") };
}

function pickLargestRect(rects) {
  if (!Array.isArray(rects) || !rects.length) {
    return null;
  }
  return [...rects].sort((left, right) => right.width * right.height - left.width * left.height)[0] || null;
}

function getHighlightAnchorRect(canvas) {
  const ocrBoxes = Array.isArray(STATE.highlightSpec?.boxes) ? STATE.highlightSpec.boxes : [];
  if (ocrBoxes.length) {
    const ocrRects = ocrBoxes
      .map((box) => normalizedBoxToRect(box, canvas.width, canvas.height))
      .filter(Boolean);
    const merged = mergeRects(ocrRects);
    const largest = pickLargestRect(merged);
    if (largest) {
      return largest;
    }
  }

  const textRects = Array.from(document.querySelectorAll("#pdfHighlights .highlight-box")).map((node) => {
    const left = Number.parseFloat(node.style.left || "0");
    const top = Number.parseFloat(node.style.top || "0");
    const width = Number.parseFloat(node.style.width || "0");
    const height = Number.parseFloat(node.style.height || "0");
    if (![left, top, width, height].every((value) => Number.isFinite(value) && value >= 0)) {
      return null;
    }
    return { x: left, y: top, width, height };
  });
  return pickLargestRect(textRects.filter(Boolean));
}

function clampOverlayPosition(stage, overlay, left, top, margin = 10) {
  const maxLeft = Math.max(margin, stage.clientWidth - overlay.offsetWidth - margin);
  const maxTop = Math.max(margin, stage.clientHeight - overlay.offsetHeight - margin);
  return {
    left: Math.max(margin, Math.min(left, maxLeft)),
    top: Math.max(margin, Math.min(top, maxTop)),
  };
}

function rectsOverlap(left, right) {
  if (!left || !right) {
    return false;
  }
  return !(
    left.x + left.width <= right.x ||
    right.x + right.width <= left.x ||
    left.y + left.height <= right.y ||
    right.y + right.height <= left.y
  );
}

function pickDefaultOverlayPosition(stage, overlay, anchorRect) {
  const margin = 10;
  const candidates = [
    { left: stage.clientWidth - overlay.offsetWidth - margin, top: margin },
    { left: margin, top: margin },
    { left: stage.clientWidth - overlay.offsetWidth - margin, top: stage.clientHeight - overlay.offsetHeight - margin },
    { left: margin, top: stage.clientHeight - overlay.offsetHeight - margin },
  ]
    .map((candidate) => clampOverlayPosition(stage, overlay, candidate.left, candidate.top, margin))
    .map((candidate) => ({
      ...candidate,
      rect: {
        x: candidate.left,
        y: candidate.top,
        width: overlay.offsetWidth,
        height: overlay.offsetHeight,
      },
    }));

  const nonBlocking = candidates.find((candidate) => !rectsOverlap(candidate.rect, anchorRect));
  if (nonBlocking) {
    return { left: nonBlocking.left, top: nonBlocking.top };
  }
  return { left: candidates[0].left, top: candidates[0].top };
}

function buildAnchorRectInStage(anchor, canvas) {
  if (!anchor || !canvas) {
    return null;
  }
  return {
    x: canvas.offsetLeft + anchor.x - 18,
    y: canvas.offsetTop + anchor.y - 18,
    width: anchor.width + 36,
    height: anchor.height + 36,
  };
}

function bindFormulaOverlayDrag(overlay, stage) {
  const handle = overlay.querySelector(".formula-audit-title");
  if (!handle || !stage) {
    return;
  }
  handle.onpointerdown = (event) => {
    if (event.button !== 0) {
      return;
    }
    event.preventDefault();
    const startLeft = Number.parseFloat(overlay.style.left || "0");
    const startTop = Number.parseFloat(overlay.style.top || "0");
    STATE.overlayDrag = {
      startClientX: event.clientX,
      startClientY: event.clientY,
      startLeft,
      startTop,
    };
    overlay.classList.add("is-dragging");
  };
}

function updateFormulaOverlayDrag(event) {
  const drag = STATE.overlayDrag;
  if (!drag) {
    return;
  }
  const overlay = document.getElementById("formulaAuditOverlay");
  const stage = document.getElementById("pdfStage");
  if (!overlay || !stage) {
    return;
  }
  const deltaX = event.clientX - drag.startClientX;
  const deltaY = event.clientY - drag.startClientY;
  const next = clampOverlayPosition(stage, overlay, drag.startLeft + deltaX, drag.startTop + deltaY, 8);
  overlay.style.left = `${next.left}px`;
  overlay.style.top = `${next.top}px`;
  STATE.overlayManualPosition = { left: next.left, top: next.top };
}

function stopFormulaOverlayDrag() {
  if (!STATE.overlayDrag) {
    return;
  }
  STATE.overlayDrag = null;
  const overlay = document.getElementById("formulaAuditOverlay");
  if (overlay) {
    overlay.classList.remove("is-dragging");
  }
}

function renderFormulaAuditOverlay(pageNumber) {
  const overlay = document.getElementById("formulaAuditOverlay");
  if (!overlay) {
    return;
  }
  if (STATE.viewId !== "formulas") {
    clearFormulaAuditOverlay();
    return;
  }

  const item = selectedItem();
  if (!item || !item.latex) {
    clearFormulaAuditOverlay();
    return;
  }
  if (!STATE.highlightSpec || STATE.highlightSpec.page !== pageNumber) {
    clearFormulaAuditOverlay();
    return;
  }

  overlay.innerHTML = `
    <div class="formula-audit-title">公式对照审核 · ${escapeHtml(item.id || "-")}</div>
    <div class="formula-audit-math"></div>
  `;
  const mathRoot = overlay.querySelector(".formula-audit-math");
  if (!mathRoot) {
    clearFormulaAuditOverlay();
    return;
  }

  if (window.katex) {
    try {
      window.katex.render(String(item.latex || ""), mathRoot, { displayMode: true, throwOnError: false, strict: "ignore" });
    } catch (error) {
      console.warn("overlay katex render failed", error);
      mathRoot.innerHTML = `<pre class="formula-raw">${escapeHtml(String(item.latex || "N/A"))}</pre>`;
    }
  } else {
    mathRoot.innerHTML = `<pre class="formula-raw">${escapeHtml(String(item.latex || "N/A"))}</pre>`;
  }

  const stage = document.getElementById("pdfStage");
  const canvas = document.getElementById("pdfCanvas");
  if (!stage || !canvas || !canvas.width || !canvas.height) {
    clearFormulaAuditOverlay();
    return;
  }

  overlay.classList.remove("is-hidden");
  const anchor = getHighlightAnchorRect(canvas);
  const anchorRect = buildAnchorRectInStage(anchor, canvas);

  let target;
  if (STATE.overlayManualPosition && typeof STATE.overlayManualPosition === "object") {
    target = clampOverlayPosition(
      stage,
      overlay,
      Number(STATE.overlayManualPosition.left) || 0,
      Number(STATE.overlayManualPosition.top) || 0,
      8
    );
  } else {
    target = pickDefaultOverlayPosition(stage, overlay, anchorRect);
  }

  overlay.style.left = `${target.left}px`;
  overlay.style.top = `${target.top}px`;
  bindFormulaOverlayDrag(overlay, stage);
}

async function renderPdfPage() {
  if (!STATE.pdfDoc) {
    clearPdfCanvas();
    renderChunkLegend();
    return;
  }
  const pageNumber = Math.min(Math.max(1, STATE.pdfPage), STATE.pdfDoc.numPages);
  STATE.pdfPage = pageNumber;

  const page = await STATE.pdfDoc.getPage(pageNumber);
  const stage = document.getElementById("pdfStage");
  const savedScrollLeft = Number.isFinite(STATE.pdfStageScrollLeft) ? STATE.pdfStageScrollLeft : stage.scrollLeft;
  const savedScrollTop = Number.isFinite(STATE.pdfStageScrollTop) ? STATE.pdfStageScrollTop : stage.scrollTop;
  const rawViewport = page.getViewport({ scale: 1 });
  const stageStyle = window.getComputedStyle(stage);
  const horizontalPadding = (Number.parseFloat(stageStyle.paddingLeft) || 0) + (Number.parseFloat(stageStyle.paddingRight) || 0);
  const verticalPadding = (Number.parseFloat(stageStyle.paddingTop) || 0) + (Number.parseFloat(stageStyle.paddingBottom) || 0);
  const availableWidth = Math.max(40, stage.clientWidth - horizontalPadding);
  const availableHeight = Math.max(40, stage.clientHeight - verticalPadding);
  const fitScale = Math.min(availableWidth / rawViewport.width, availableHeight / rawViewport.height);
  const safeFitScale = Number.isFinite(fitScale) && fitScale > 0 ? fitScale : 1;
  const manualScale = Number.isFinite(STATE.pdfScale) && STATE.pdfScale > 0 ? STATE.pdfScale : 1.4;
  const effectiveScale = STATE.pdfFitMode ? Math.max(0.05, Math.min(4, safeFitScale)) : Math.max(0.05, Math.min(4, manualScale));
  if (!STATE.pdfFitMode) {
    STATE.pdfScale = effectiveScale;
  }

  const viewport = page.getViewport({ scale: effectiveScale });
  const canvas = document.getElementById("pdfCanvas");
  const context = canvas.getContext("2d");
  canvas.width = Math.floor(viewport.width);
  canvas.height = Math.floor(viewport.height);

  await page.render({ canvasContext: context, viewport }).promise;
  await renderHighlights(pageNumber, viewport);
  renderFormulaAuditOverlay(pageNumber);
  renderChunkLegend();

  if (STATE.pdfFitMode) {
    stage.scrollLeft = 0;
    stage.scrollTop = 0;
    STATE.pdfStageScrollLeft = 0;
    STATE.pdfStageScrollTop = 0;
  } else {
    const maxLeft = Math.max(0, stage.scrollWidth - stage.clientWidth);
    const maxTop = Math.max(0, stage.scrollHeight - stage.clientHeight);
    const nextLeft = Math.max(0, Math.min(savedScrollLeft, maxLeft));
    const nextTop = Math.max(0, Math.min(savedScrollTop, maxTop));
    stage.scrollLeft = nextLeft;
    stage.scrollTop = nextTop;
    STATE.pdfStageScrollLeft = nextLeft;
    STATE.pdfStageScrollTop = nextTop;
  }

  const warm = STATE.indexWarmup[STATE.pdfChapterId];
  const warmText = warm && !warm.ready ? ` · 索引 ${warm.done}/${warm.total}` : "";
  const fitText = STATE.pdfFitMode ? "fit" : `${effectiveScale.toFixed(2)}x`;
  const chapterLabel = chapterMetaById(STATE.pdfChapterId)?.label || STATE.pdfChapterId || "PDF";
  document.getElementById("pdfPageInfo").textContent = `${chapterLabel} · ${pageNumber} / ${STATE.pdfDoc.numPages} · ${fitText}${warmText}`;
  document.getElementById("pdfFitToggle").textContent = STATE.pdfFitMode ? "退出适配" : "适配视口";
}

function buildMatchTokens(item) {
  const locatorTerms = (item.locator && item.locator.terms) || [];
  const rawKeys = [item.id, item.title, item.subtitle, item.excerpt, ...(item.search_keys || []), ...locatorTerms];
  const tokens = [];
  rawKeys.forEach((key) => {
    const normalized = normalizeMatchText(key);
    if (!normalized) {
      return;
    }
    if (normalized.length >= 6 && normalized.length <= 120) {
      tokens.push(normalized);
    }
    normalized.split(" ").forEach((token) => {
      if (token.length >= 3) {
        tokens.push(token);
      }
    });
  });
  return Array.from(new Set(tokens)).sort((a, b) => b.length - a.length).slice(0, 18);
}

function parseCandidateBoxes(rawCandidate) {
  const rawBoxes = Array.isArray(rawCandidate?.boxes)
    ? rawCandidate.boxes
    : rawCandidate?.bbox && typeof rawCandidate.bbox === "object"
      ? [rawCandidate.bbox]
      : [];
  return rawBoxes
    .map((box) => {
      if (!box || typeof box !== "object") {
        return null;
      }
      const x = Number(box.x);
      const y = Number(box.y);
      const w = Number(box.w);
      const h = Number(box.h);
      if (![x, y, w, h].every((value) => Number.isFinite(value)) || w <= 0 || h <= 0) {
        return null;
      }
      return { x, y, w, h, kind: String(box.kind || "ocr") };
    })
    .filter(Boolean);
}

function normalizeRawCandidates(rawCandidates, fallbackSource, options) {
  const requireBoxes = Boolean(options?.requireBoxes);
  const parsed = (Array.isArray(rawCandidates) ? rawCandidates : [])
    .map((candidate) => {
      const page = Number(candidate?.page);
      const score = Number(candidate?.score);
      const boxes = parseCandidateBoxes(candidate);
      const matched = Array.isArray(candidate?.matched)
        ? candidate.matched.map((token) => String(token || "").trim()).filter(Boolean).slice(0, 8)
        : [];
      if (!Number.isFinite(page) || page < 1) {
        return null;
      }
      if (requireBoxes && !boxes.length) {
        return null;
      }
      if (!boxes.length && !matched.length) {
        return null;
      }
      return {
        page,
        score: Number.isFinite(score) ? score : 0.7,
        boxes,
        matched,
        source: String(candidate?.source || fallbackSource || "locator"),
      };
    })
    .filter(Boolean);
  return normalizeCandidates(parsed);
}

function getReviewLocatorCandidatesForItem(item, chapterId = itemChapterId(item), viewId = STATE.viewId) {
  const chapterPayload = DATA.reviewLocators?.chapters?.[chapterId];
  if (!chapterPayload || typeof chapterPayload !== "object") {
    return [];
  }
  const viewPayload = chapterPayload[viewId];
  if (!viewPayload || typeof viewPayload !== "object") {
    return [];
  }
  const keys = [item.id, item.source_unit_id, item.item_key]
    .map((value) => String(value || "").trim().toLowerCase())
    .filter(Boolean);
  for (const key of keys) {
    const entry = viewPayload[key];
    if (!entry || !Array.isArray(entry.candidates)) {
      continue;
    }
    return normalizeRawCandidates(entry.candidates, `layout_${viewId}`, { requireBoxes: true });
  }
  return [];
}

function getOcrCandidatesForItem(item, chapterId = itemChapterId(item), viewId = STATE.viewId) {
  if (viewId !== "formulas") {
    return [];
  }
  const chapterPayload = DATA.formulaOcr?.chapters?.[chapterId];
  if (!chapterPayload || typeof chapterPayload !== "object") {
    return [];
  }
  const formulaMap = chapterPayload.formulas || {};
  const formulaId = String(item.id || "").toLowerCase();
  const entry = formulaMap[formulaId];
  if (!entry || !Array.isArray(entry.candidates)) {
    return [];
  }
  return normalizeRawCandidates(entry.candidates, "ocr_formula", { requireBoxes: true });
}

function pageTokenScore(pageText, tokens) {
  let score = 0;
  const matched = [];
  tokens.forEach((token) => {
    if (pageText.includes(token)) {
      score += Math.min(22, token.length * 1.6);
      matched.push(token);
    }
  });
  return { score, matched };
}

function formulaIdRegex(itemId) {
  const match = String(itemId || "")
    .trim()
    .toLowerCase()
    .match(/^(\d+)\.(\d+)([a-z]?)$/);
  if (!match) {
    return null;
  }
  const chapter = match[1];
  const number = match[2];
  const suffix = match[3] || "";
  const suffixPart = suffix ? `\\s*${suffix}` : "\\s*[a-z]?";
  const pattern = `(?:eq(?:uation)?\\.?\\s*)?\\(?\\s*${chapter}\\s*\\.\\s*${number}${suffixPart}\\s*\\)?`;
  return new RegExp(pattern, "i");
}

function buildCandidatePageWindow(item, numPages) {
  const locator = item.locator || {};
  const hint = Number(locator.toc_page_hint) || null;
  const chapterHint = Number(locator.toc_chapter_page) || null;
  const pages = new Set();

  if (hint) {
    for (let page = Math.max(1, hint - 6); page <= Math.min(numPages, hint + 6); page += 1) {
      pages.add(page);
    }
  }
  if (chapterHint) {
    for (let page = Math.max(1, chapterHint - 12); page <= Math.min(numPages, chapterHint + 18); page += 1) {
      pages.add(page);
    }
  }
  return Array.from(pages).sort((a, b) => a - b);
}

async function scoreCandidatePages(item, pages, tokens, chapterId = STATE.pdfChapterId, viewId = STATE.viewId) {
  const locator = item.locator || {};
  const subsectionNorm = normalizeMatchText(locator.subsection || item.subtitle || "");
  const hint = Number(locator.toc_page_hint) || null;
  const sourceNorm = normalizeMatchText(locator.source_unit_id || item.source_unit_id || "");
  const formulaRegex = viewId === "formulas" ? formulaIdRegex(item.id) : null;
  const scored = [];

  for (const page of pages) {
    const cache = await getPageTextCache(chapterId, page);
    const tokenScore = pageTokenScore(cache.joined, tokens);
    let score = tokenScore.score;

    if (subsectionNorm && cache.joined.includes(subsectionNorm)) {
      score += 68;
    } else if (subsectionNorm) {
      const subsectionTokens = subsectionNorm.split(" ").filter((token) => token.length >= 3);
      const subsectionHits = subsectionTokens.filter((token) => cache.joined.includes(token)).length;
      score += subsectionHits * 8;
    }

    if (sourceNorm && cache.joined.includes(sourceNorm)) {
      score += 24;
    }

    if (formulaRegex && formulaRegex.test(cache.rawJoined || "")) {
      score += 180;
      tokenScore.matched.unshift(String(item.id || "").toLowerCase());
    }

    if (hint) {
      const distance = Math.abs(page - hint);
      score += Math.max(0, 30 - distance * 4.2);
    }

    scored.push({
      page,
      score,
      matched: tokenScore.matched.slice(0, 8),
      source: hint ? "toc_window" : "global",
    });
  }

  scored.sort((left, right) => right.score - left.score || left.page - right.page);
  return scored;
}

function needsGlobalFallback(item, scoredWindow) {
  if (!scoredWindow.length) {
    return true;
  }
  const hasHint = Boolean(item.locator && item.locator.toc_page_hint);
  const bestScore = scoredWindow[0].score || 0;
  return hasHint && bestScore < 44;
}

function normalizeCandidates(candidates) {
  const map = new Map();
  candidates.forEach((candidate) => {
    const existing = map.get(candidate.page);
    if (!existing || candidate.score > existing.score) {
      map.set(candidate.page, candidate);
    }
  });
  return Array.from(map.values()).sort((a, b) => b.score - a.score || a.page - b.page);
}

function renderCandidatePages() {
  const root = document.getElementById("candidatePages");
  const panel = document.getElementById("candidatePanel");
  const summary = document.getElementById("candidateSummary");
  if (!root || !panel) {
    return;
  }

  if (!STATE.candidatePages.length) {
    root.innerHTML = "";
    panel.classList.add("is-empty");
    if (summary) {
      summary.textContent = "暂无";
    }
    return;
  }
  panel.classList.remove("is-empty");
  if (summary) {
    summary.textContent = `${STATE.candidatePages.length} 个`;
  }

  root.innerHTML = STATE.candidatePages
    .map(
      (candidate, index) => {
        const matched = Array.isArray(candidate.matched) ? candidate.matched.slice(0, 3).join(" / ") : "";
        const matchedLabel = matched ? ` · ${compactText(matched, 34)}` : "";
        return `<button type="button" class="candidate-btn ${candidate.page === STATE.pdfPage ? "is-active" : ""}" data-candidate-index="${index}" title="${escapeHtml(
          matched ? `matched: ${matched}` : ""
        )}">
          P${candidate.page} · ${candidate.score.toFixed(1)} · ${escapeHtml(candidate.source || "text")}${escapeHtml(matchedLabel)}
        </button>`
      }
    )
    .join("");

  root.querySelectorAll(".candidate-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const index = Number(button.dataset.candidateIndex);
      const candidate = STATE.candidatePages[index];
      if (!candidate) {
        return;
      }
      STATE.pdfPage = candidate.page;
      STATE.highlightSpec = {
        page: candidate.page,
        tokens: Array.isArray(candidate.matched) ? candidate.matched.slice(0, 5) : [],
        boxes: Array.isArray(candidate.boxes) ? candidate.boxes : [],
      };
      updatePdfStatus(`切换候选页 P${candidate.page}（${candidate.source}）`);
      await renderPdfPage();
      renderCandidatePages();
    });
  });
}

function selectedItem() {
  return filteredItems().find((item) => item.id === STATE.selectedItemId) || null;
}

function shouldForceFitCurrentView() {
  return STATE.viewId === "chunks";
}

async function locateSelectedItemInPdf(force) {
  const requestId = STATE.locateRequestId + 1;
  STATE.locateRequestId = requestId;
  const item = selectedItem();
  const targetChapterId = item ? itemChapterId(item) : String(STATE.chapterId || "").trim().toLowerCase();
  if (!item) {
    STATE.highlightSpec = null;
    STATE.lastLocatedItemKey = null;
    STATE.candidatePages = [];
    const loaded = await loadPdfForChapter(targetChapterId, requestId);
    if (STATE.locateRequestId !== requestId) {
      return;
    }
    if (loaded && STATE.pdfDoc) {
      STATE.pdfPage = 1;
      await renderPdfPage();
    }
    renderCandidatePages();
    return;
  }

  const loaded = await loadPdfForChapter(targetChapterId, requestId);
  if (STATE.locateRequestId !== requestId) {
    return;
  }
  if (!loaded || !STATE.pdfDoc) {
    return;
  }

  // Chunk 首次进入默认整页；一旦用户手动调过缩放/滚动，就沿用当前配置。
  if (force && shouldForceFitCurrentView() && !STATE.pdfViewCustomized) {
    STATE.pdfFitMode = true;
  }

  const itemKey = item.item_key || recordKeyForItem(item);
  if (!force && STATE.lastLocatedItemKey === itemKey) {
    return;
  }

  const boxedCandidates = normalizeCandidates([
    ...getReviewLocatorCandidatesForItem(item, targetChapterId, STATE.viewId),
    ...getOcrCandidatesForItem(item, targetChapterId, STATE.viewId),
  ]).slice(0, 3);
  if (boxedCandidates.length) {
    const best = boxedCandidates[0];
    STATE.pdfPage = best.page;
    STATE.highlightSpec = {
      page: best.page,
      tokens: Array.isArray(best.matched) ? best.matched.slice(0, 5) : [],
      boxes: best.boxes || [],
    };
    STATE.candidatePages = boxedCandidates;
    STATE.lastLocatedItemKey = itemKey;
    const sourceText = best.source || "locator";
    updatePdfStatus(`自动定位成功 P${best.page}（${sourceText}，Top${boxedCandidates.length} 可切换）`);
    await renderPdfPage();
    renderCandidatePages();
    return;
  }

  const tokens = buildMatchTokens(item);
  if (!tokens.length) {
    updatePdfStatus("当前条目没有可用于定位的关键词。");
    STATE.highlightSpec = null;
    STATE.lastLocatedItemKey = itemKey;
    STATE.candidatePages = [];
    await renderPdfPage();
    renderCandidatePages();
    return;
  }

  const numPages = STATE.pdfDoc.numPages;
  const windowPages = buildCandidatePageWindow(item, numPages);
  const primaryPages = windowPages.length ? windowPages : Array.from({ length: numPages }, (_, i) => i + 1);
  let candidates = await scoreCandidatePages(item, primaryPages, tokens, targetChapterId, STATE.viewId);
  if (STATE.locateRequestId !== requestId) {
    return;
  }

  if (needsGlobalFallback(item, candidates) && primaryPages.length < numPages) {
    const fullPages = Array.from({ length: numPages }, (_, i) => i + 1);
    const fallback = await scoreCandidatePages(item, fullPages, tokens, targetChapterId, STATE.viewId);
    if (STATE.locateRequestId !== requestId) {
      return;
    }
    fallback.forEach((candidate) => {
      candidate.source = "fallback_global";
    });
    candidates = normalizeCandidates([...candidates, ...fallback]);
  }

  candidates = candidates.slice(0, 3);
  if (!candidates.length) {
    STATE.highlightSpec = null;
    STATE.lastLocatedItemKey = itemKey;
    STATE.candidatePages = [];
    updatePdfStatus("定位失败：未匹配到可用页，请手动翻页复核。");
    await renderPdfPage();
    renderCandidatePages();
    return;
  }

  const best = candidates[0];
  STATE.pdfPage = best.page;
  STATE.highlightSpec = {
    page: best.page,
    tokens: best.matched.slice(0, 5),
    boxes: [],
  };
  STATE.candidatePages = candidates;
  STATE.lastLocatedItemKey = itemKey;

  const anchorText = item.locator?.toc_page_hint ? `小节锚点 P${item.locator.toc_page_hint}` : "无小节锚点";
  updatePdfStatus(`已回退文本定位 P${best.page}（${anchorText}，Top3 可切换）`);
  await renderPdfPage();
  renderCandidatePages();
}

function updatePdfStatus(message) {
  document.getElementById("pdfStatus").textContent = message;
}

function viewLabel(viewId) {
  const view = (DATA.review?.views || []).find((item) => item.id === viewId);
  return view?.label || viewId;
}

function metricCard(label, value, note) {
  return `<article class="metric-card">
    <div class="metric-label">${escapeHtml(label)}</div>
    <span class="metric-value">${escapeHtml(value)}</span>
    <div class="small-text">${escapeHtml(note)}</div>
  </article>`;
}

function renderFlow() {
  const flow = DATA.flow || {};
  const overviewRoot = document.getElementById("flowOverview");
  const tabsRoot = document.getElementById("subflowTabs");
  const detailRoot = document.getElementById("subflowDetail");
  const risksRoot = document.getElementById("flowRisks");

  const overviewNodes = flow.overview_nodes || [];
  overviewRoot.innerHTML = overviewNodes
    .map(
      (node) => `<article class="flow-node">
        <div class="flow-node-title">${escapeHtml(node.title || "-")}</div>
        <div class="small-text">${escapeHtml(node.subtitle || "")}</div>
        <div>${escapeHtml(node.detail || "")}</div>
      </article>`
    )
    .join("");

  const subflowKeys = Object.keys(flow.subflows || {});
  if (!subflowKeys.includes(STATE.subflowId)) {
    STATE.subflowId = subflowKeys[0] || "formulas";
  }
  tabsRoot.innerHTML = subflowKeys
    .map(
      (key) =>
        `<button type="button" class="${key === STATE.subflowId ? "is-active" : ""}" data-subflow-id="${escapeHtml(key)}">${escapeHtml(
          viewLabel(key)
        )}</button>`
    )
    .join("");
  tabsRoot.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      STATE.subflowId = button.dataset.subflowId;
      renderFlow();
    });
  });

  const nodes = flow.subflows?.[STATE.subflowId] || [];
  detailRoot.innerHTML = nodes
    .map(
      (node) => `<article class="pipeline-node">
        <div class="pipeline-node-title">${escapeHtml(node.title || "-")}</div>
        <div>${escapeHtml(node.detail || "")}</div>
      </article>`
    )
    .join("");

  const risks = flow.risks || [];
  risksRoot.innerHTML = risks.length
    ? risks
        .map(
          (risk) => `<article class="stack-item">
            <div><strong>${escapeHtml(risk.risk || "-")}</strong></div>
            <div>${escapeHtml(risk.description || "-")}</div>
            <div class="small-text">状态: ${escapeHtml(risk.status || "N/A")}</div>
          </article>`
        )
        .join("")
    : '<div class="placeholder">未在 docs/architecture.md 中解析到风险表。</div>';
}

function renderMathToken(latex, displayMode) {
  const node = document.createElement(displayMode ? "div" : "span");
  node.className = displayMode ? "table-math table-math-block" : "table-math";
  const normalizedLatex = String(latex || "").trim();
  if (!normalizedLatex) {
    node.textContent = "";
    return node;
  }
  if (window.katex) {
    try {
      window.katex.render(normalizedLatex, node, { displayMode, throwOnError: false, strict: "ignore" });
      return node;
    } catch (error) {
      console.warn("table katex render failed", error);
    }
  }
  node.classList.add("math-fallback");
  node.textContent = displayMode ? `$$${normalizedLatex}$$` : `$${normalizedLatex}$`;
  return node;
}

function renderTableHtml(rawHtml, mathEnabled) {
  const html = String(rawHtml || "").trim();
  if (!html) {
    return '<div class="placeholder">表格 HTML 缺失。</div>';
  }

  const wrapper = document.createElement("div");
  wrapper.innerHTML = html;
  if (!mathEnabled) {
    return `<div class="rendered-table">${wrapper.innerHTML}</div>`;
  }

  const textNodes = [];
  const walker = document.createTreeWalker(wrapper, window.NodeFilter ? window.NodeFilter.SHOW_TEXT : 4, {
    acceptNode(node) {
      const parentTag = node?.parentElement?.tagName?.toLowerCase() || "";
      if (!node?.nodeValue || !node.nodeValue.includes("$")) {
        return window.NodeFilter ? window.NodeFilter.FILTER_SKIP : 3;
      }
      if (["script", "style", "textarea", "code", "pre"].includes(parentTag)) {
        return window.NodeFilter ? window.NodeFilter.FILTER_SKIP : 3;
      }
      return window.NodeFilter ? window.NodeFilter.FILTER_ACCEPT : 1;
    },
  });
  while (walker.nextNode()) {
    textNodes.push(walker.currentNode);
  }

  const mathPattern = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g;
  textNodes.forEach((textNode) => {
    const source = String(textNode.nodeValue || "");
    let cursor = 0;
    let matched = false;
    const fragment = document.createDocumentFragment();
    for (const match of source.matchAll(mathPattern)) {
      const full = match[0];
      const blockLatex = match[1];
      const inlineLatex = match[2];
      const index = Number(match.index);
      if (!Number.isFinite(index)) {
        continue;
      }
      if (index > cursor) {
        fragment.appendChild(document.createTextNode(source.slice(cursor, index)));
      }
      fragment.appendChild(renderMathToken(blockLatex || inlineLatex || "", Boolean(blockLatex)));
      cursor = index + full.length;
      matched = true;
    }
    if (!matched) {
      return;
    }
    if (cursor < source.length) {
      fragment.appendChild(document.createTextNode(source.slice(cursor)));
    }
    textNode.parentNode.replaceChild(fragment, textNode);
  });

  const fallbackHint =
    !window.katex && mathEnabled
      ? '<div class="math-fallback">KaTeX 未加载，当前显示原始数学文本。</div>'
      : "";
  return `${fallbackHint}<div class="rendered-table">${wrapper.innerHTML}</div>`;
}

function renderChunkLegend() {
  const legend = document.getElementById("chunkLegend");
  if (!legend) {
    return;
  }
  if (STATE.viewId !== "chunks") {
    legend.classList.add("is-hidden");
    legend.innerHTML = "";
    return;
  }

  legend.classList.remove("is-hidden");
  legend.innerHTML = `
    <span class="chunk-legend-title">Chunk</span>
    ${CHUNK_HIGHLIGHT_META.map(
      (item) => `<label class="chunk-legend-item">
          <input type="checkbox" data-chunk-semantic="${escapeHtml(item.semantic)}" ${STATE.chunkHighlightLegend[item.semantic] ? "checked" : ""}>
          <span class="chunk-legend-dot chunk-dot-${escapeHtml(item.semantic)}"></span>
          <span>${escapeHtml(item.label)}</span>
        </label>`
    ).join("")}
  `;

  legend.querySelectorAll("input[data-chunk-semantic]").forEach((input) => {
    input.addEventListener("change", async () => {
      const semantic = input.dataset.chunkSemantic;
      if (!semantic) {
        return;
      }
      STATE.chunkHighlightLegend[semantic] = Boolean(input.checked);
      if (!STATE.pdfDoc) {
        return;
      }
      await renderPdfPage();
    });
  });
}

function isChunkHighlightVisible(kind) {
  const normalizedKind = sanitizeHighlightKind(kind);
  if (!normalizedKind.startsWith("chunk_")) {
    return true;
  }
  const semantic = normalizedKind.slice("chunk_".length);
  if (!Object.prototype.hasOwnProperty.call(STATE.chunkHighlightLegend, semantic)) {
    return true;
  }
  return Boolean(STATE.chunkHighlightLegend[semantic]);
}

function renderChunkTextMath(root) {
  if (!window.katex) {
    scheduleMathRenderRetry();
    return;
  }
  MATH_RENDER_RETRY_COUNT = 0;
  const mathPattern = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g;
  root.querySelectorAll(".chunk-math-text").forEach((node) => {
    const source = String(node.textContent || "");
    if (!source || !source.includes("$")) {
      return;
    }

    let cursor = 0;
    let matched = false;
    const fragment = document.createDocumentFragment();
    for (const match of source.matchAll(mathPattern)) {
      const full = match[0];
      const blockLatex = match[1];
      const inlineLatex = match[2];
      const index = Number(match.index);
      if (!Number.isFinite(index)) {
        continue;
      }
      if (index > cursor) {
        fragment.appendChild(document.createTextNode(source.slice(cursor, index)));
      }
      fragment.appendChild(renderMathToken(blockLatex || inlineLatex || "", Boolean(blockLatex)));
      cursor = index + full.length;
      matched = true;
    }

    if (!matched) {
      return;
    }
    if (cursor < source.length) {
      fragment.appendChild(document.createTextNode(source.slice(cursor)));
    }
    node.innerHTML = "";
    node.appendChild(fragment);
  });
}

function applyMath(root) {
  root.querySelectorAll(".formula-box").forEach((node) => {
    const latex = node.dataset.latex || "";
    if (!latex) {
      node.innerHTML = '<pre class="formula-raw">N/A</pre>';
      return;
    }
    if (window.katex) {
      try {
        window.katex.render(latex, node, { displayMode: true, throwOnError: false, strict: "ignore" });
      } catch (error) {
        console.warn("katex render failed", error);
        node.innerHTML = `<pre class="formula-raw">${escapeHtml(latex)}</pre>`;
      }
      return;
    }
    node.innerHTML = `<pre class="formula-raw">${escapeHtml(latex)}</pre>`;
  });

  renderChunkTextMath(root);
}

function scheduleMathRenderRetry() {
  if (MATH_RENDER_RETRY_TIMER || MATH_RENDER_RETRY_COUNT >= 20) {
    return;
  }
  MATH_RENDER_RETRY_COUNT += 1;
  MATH_RENDER_RETRY_TIMER = window.setTimeout(() => {
    MATH_RENDER_RETRY_TIMER = null;
    if (window.katex) {
      applyMath(document);
      return;
    }
    scheduleMathRenderRetry();
  }, 250);
}

function cryptoRandomId() {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }
  return `note_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function formatTime(isoText) {
  const date = new Date(isoText);
  if (Number.isNaN(date.getTime())) {
    return isoText;
  }
  return date.toLocaleString();
}

function normalizeMatchText(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
