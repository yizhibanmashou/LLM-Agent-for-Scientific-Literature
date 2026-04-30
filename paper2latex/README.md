# paper2latex

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**paper2latex** is an MCP (Model Context Protocol) server that converts scientific papers (PDF) to compilable, editable LaTeX projects with proper structure, citations, bibliography, and formulas.

> **v0.2 Update**: Now uses **PaddleOCR** as the primary engine for robust layout analysis, replacing the legacy GROBID dependency.

## Features

- 📄 **Layout Analysis (e.g. PaddleOCR)**: Robust handling of multi-column, complex layouts
- 🧠 **Structure Parsing**: Semantic extraction of Title, Abstract, Sections, and Paragraphs
- 📚 **Citation Mapping**: Converts `[1]` style citations to `\cite{key}` commands
- 📖 **BibTeX Generation**: Creates `refs.bib` with stable citation keys from parsed references
- 🔢 **Formula Handling**: Extracts formula coordinates and creates placeholders (OCR coming soon)
- 🖼️ **Figure Extraction**: Extracts figures with captions (placeholder support)
- ⚙️ **Configurable**: YAML-based configuration

## Installation

### From Source

```bash
git clone https://github.com/rudaoshi/paper2latex.git
cd paper2latex
# Using uv (recommended)
uv sync
# Or pip
pip install -e .
```

## Prerequisites

### Layout Analysis Engine (PaddleOCR)

paper2latex relies on `paddleocr-mcp` for layout analysis. Ensure you have access to it or the PaddleOCR Cloud API.

```bash
uvx --from paddleocr-mcp paddleocr_mcp
```

## Quick Start

### 1. Start the MCP Server

```bash
paper2latex
# Server starts on http://localhost:8000/mcp
```

### 2. Use in Your MCP Client

Example with Claude Desktop or any MCP-compatible client:

```json
{
  "mcpServers": {
    "paper2latex": {
      "command": "uv",
      "args": ["run", "paper2latex"]
    }
  }
}
```

## MCP Tools

### `convert` - Full PDF to LaTeX Conversion

Convert a PDF to a complete LaTeX project:

```json
{
  "source": {
    "type": "path",
    "value": "/path/to/paper.pdf"
  },
  "output": {
    "format": "dir",
    "path": "/path/to/output"
  },
  "options": {
      "paddle_pipeline": "PaddleOCR-VL"
  }
}
```

**Output Structure:**
```
output/
├── main.tex          # Main LaTeX document
├── refs.bib          # Bibliography
├── figures/          # Extracted figures
├── intermediate/     # Debug files (JSON layout)
└── report.md         # Quality report
```

### `extract_bib` - Extract Bibliography Only

Extract only the bibliography as BibTeX:

```json
{
  "source": {
    "type": "path",
    "value": "/path/to/paper.pdf"
  },
  "output": {
    "path": "/path/to/refs.bib"
  }
}
```

## Architecture

```
paper2latex/
├── server.py             # MCP server and tools
├── pipeline.py           # Main conversion orchestrator
├── core/
│   ├── config.py         # Configuration management
│   └── models.py         # Data models (Document, Section, Block)
├── converters/
│   ├── paddle_cloud_manager.py # PaddleOCR MCP client
│   └── structure_parser.py     # JSON -> Document Model parser
├── processors/
│   ├── reference_resolver.py   # Citation linking logic
│   ├── formula_extractor.py    # Formula extraction
│   └── figure_extractor.py     # Figure extraction
└── generators/
    └── latex_generator.py      # LaTeX generation
```

## Roadmap

- **v0.1**: GROBID based pipeline (Legacy)
- **v0.2** (Current): Layout Analysis core rewrite (Structure + citations + bib)
- **v0.3**: Formula OCR integration (pix2tex)
- **v0.4**: Scanned PDF support (OCR fallback)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for layout analysis implementation
- [MCP](https://modelcontextprotocol.io/) for the protocol specification
