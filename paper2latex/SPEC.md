# paper2latex-mcp — spec.md

> 目标：构建一个 MCP（Model Context Protocol）工具，将科学论文（PDF）尽可能自动化地转化为**可编译、可编辑**的 LaTeX 项目（含结构、引用、参考文献、公式 LaTeX、图表占位/抽取）。

---

## 1. 背景与动机

科研论文 PDF（尤其双栏 + 大量公式）是“可读但难复用”的载体。很多下游任务需要：

- 将论文转成 **LaTeX 源码**（继续写作、二次排版、引用复用、可检索的结构化文本）
- 提取 **文献列表**并生成可用 BibTeX
- 保留正文中的 **引用锚点**，并正确映射到参考文献条目
- 将 **公式**转成 LaTeX（而不是图片/乱码）

传统的基于 GROBID 的方案在处理复杂版面（如双栏图片混排）和非英文文档时往往力不从心。本项目采用 **PaddleOCR**（Layout Analysis）作为核心引擎，结合规则解析，提供更鲁棒的还原能力。

---

## 2. 设计目标

### 2.1 Must-have（必须实现）

1. **输入**：PDF 文件路径 / URL
2. **输出**：一个可编译的 LaTeX 工程（`main.tex` + `refs.bib` + `figures/` + `equations/`）
3. **文章结构**：标题、作者、摘要、章节层级、段落精准还原
4. **正文引用**：将正文中的引文标记（如 `[1]`）转为 `\cite{...}`，并与 BibTeX 条目一一对应
5. **参考文献**：输出 `refs.bib`，BibTeX key 稳定可复现
6. **公式**：定位公式区域，支持图片占位或 LaTeX 转换
7. **可追溯性**：保留来源信息（页码、bbox）

### 2.2 Nice-to-have（增强项）

- 图表自动抽取与 `figure` 环境生成
- 支持公式 OCR（pix2tex）
- 扫描版 PDF 的 OCR 回退（PaddleOCR 天然支持）
- 生成结构化中间产物（Document JSON）供 RAG 使用

---

## 3. 总体架构 (v0.2+)

本项目采用 **PaddleOCR First** 策略，不再依赖 GROBID 进行布局分析。

### 3.1 核心流水线

**Stage A — 版面分析 (Layout Analysis)**
- 调用布局分析引擎（如 PaddleOCR MCP/Cloud），获取详细的版面信息。
- 输出：包含所有页面元素的详细 JSON（Text, Title, Figure, Table, Formula, Header/Footer）。
- 优势：原生支持双栏、图片混排、公式区域检测。

**Stage B — 结构化解析 (StructureParser)**
- 将 PaddleOCR 的扁平化/分块 JSON 转换为语义化的 `Document` 模型。
- **Metadata**: 提取 Title, Authors, Abstract。
- **Sectioning**: 根据 Header 类型和文本特征识别章节层级。
- **Filtering**: 剔除页眉页脚干扰。
- **Assets**: 识别 Figure 和 Formula 的位置信息。

**Stage C — 引用解析 (ReferenceResolver)**
- **Bibliography Parsing**: 从 References 章节解析参考文献条目，生成 BibEntry。
- **Citation Linking**: 扫描正文文本，识别引用标记（如 `[1]`, `(Smith, 2020)`），并将其替换为对应的 LaTeX `\cite{key}` 命令。

**Stage D — 生成与渲染 (LaTeXGenerator)**
- **BibTeX**: 基于解析出的参考文献生成 `refs.bib`。
- **Main TeX**: 生成 `main.tex`。
    - 自动生成 Preamble。
    - 渲染章节结构 (`\section` 等)。
    - 插入图表 (`figure` 环境 + 占位图/截图)。
    - 插入公式 (`equation` 环境 + OCR结果/占位)。

**Stage E — 资源提取 (ResourceHandler)**
- 基于 PaddleOCR 提供的 BBox，从原 PDF 中裁剪出图片和公式区域，保存为资源文件。

---

## 4. MCP 工具接口设计

### 4.1 Tool: `paper2latex.convert`

将论文输入转为 LaTeX 工程并返回产物位置。

**Input (JSON)**
- `source`:
    - `type`: `"path" | "url"`
    - `value`: string
- `output`:
    - `format`: `"zip" | "dir"` (default: "zip")
    - `path`: string (optional)
- `mode`: `"balanced"`
- `options`:
    - `paddle_pipeline`: `"PaddleOCR-VL" | "PP-StructureV2"` (default: "PaddleOCR-VL")
    - `paddle_source`: `"aistudio" | "local"` (default: "aistudio")
    - `formula_ocr`: `"pix2tex" | "none"` (default: "none")

**Output (JSON)**
- `status`: `"ok" | "failed"`
- `artifact`:
    - `path`: string
- `summary`:
    - `sections`: int
    - `bib_entries`: int
    - `formulas`: int

### 4.2 Tool: `paper2latex.extract_bib`

仅提取参考文献并输出 BibTeX。

**Input**
- `source`: 同上
- `output.path`: string (optional)

**Output**
- `status`: `"ok"`
- `bibtex_path`: string
- `bib_entries`: int

---

## 5. 关键数据模型

### 5.1 Document Model
```python
@dataclass
class Document:
    title: str
    abstract: str
    sections: List[Section]
    references: List[BibEntry]
    figures: List[Figure]
    formulas: List[FormulaCoord]
```

### 5.2 Block Types (Paddle Maps)
- `text` -> Paragraph
- `title` -> Document Title / Section Header
- `figure` -> Figure Environment
- `table` -> Table Environment
- `formula` -> Equation Environment
- `reference` -> Bibliography Item

---

## 6. 路线图 (Roadmap)

- **v0.1 (Legacy)**: GROBID based pipeline.
- **v0.2 (Current)**: PaddleOCR 核心重构。
    - [x] PaddleOCR MCP 集成 (Layout Analysis)
    - [x] StructureParser 实现
    - [x] ReferenceResolver (基础 `[1]` 支持)
    - [x] LaTeXGenerator (Main + Bib)
- **v0.3 (Next)**:
    - [ ] Formula OCR (pix2tex) 集成
    - [ ] 增强的引用匹配 (Author-Year 风格)
    - [ ] PDF 图像/公式自动裁剪 (ResourceHandler)
    - [ ] 编译验证 (latexmk)
