# paper2latex Web Interface

Modern web interface for converting scientific papers (PDF) to LaTeX projects.

## Features

- 📤 **Drag & Drop Upload**: Easy PDF upload with visual feedback
- 📁 **File Tree Browser**: Navigate through generated LaTeX files
- 👀 **Live Preview**: View LaTeX source code with syntax highlighting
- 📄 **PDF Compilation**: Compile LaTeX to PDF in-browser
- 📊 **Statistics Dashboard**: View conversion metrics (pages, citations, formulas)
- 💾 **Download**: Download complete LaTeX project as ZIP

## Screenshots

![Upload Interface](screenshots/upload.png)
![Results View](screenshots/results.png)

## Prerequisites

1. **GROBID Service** (required for conversion):
   ```bash
   docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0
   ```

2. **LaTeX Compiler** (required for PDF compilation):
   - Install **tectonic** (recommended):
     ```bash
     # macOS
     brew install tectonic
     
     # Linux
     curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh
     ```
   
   - Or install **latexmk**:
     ```bash
     # macOS
     brew install --cask mactex
     
     # Linux
     sudo apt-get install texlive-full
     ```

3. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rudaoshi/paper2latex.git
   cd paper2latex
   ```

2. **Install paper2latex**:
   ```bash
   pip install -e .
   ```

3. **Install web dependencies**:
   ```bash
   cd web
   pip install -r requirements.txt
   ```

## Running the Server

### Method 1: Quick Start Script (Bash)

```bash
# Can be run from anywhere
/path/to/paper2latex/web/start.sh

# Or if you're in the web directory
./start.sh
```

### Method 2: Python Launcher

```bash
# Can be run from anywhere
python /path/to/paper2latex/web/launch.py

# Or add to PATH
python -m paper2latex.web.launch
```

### Method 3: Direct Run

```bash
cd /path/to/paper2latex/web
python app.py
```

The web interface will be available at: **http://localhost:8080**

## Usage

1. **Upload PDF**: Click "Choose PDF File" or drag & drop a PDF
2. **Convert**: Click "Convert to LaTeX"
3. **Browse Files**: Click on files in the tree to view content
4. **Compile**: Click "Compile PDF" to generate the final document
5. **Download**: Click "Download LaTeX" to get the complete project

## API Endpoints

### POST /api/convert
Upload and convert PDF to LaTeX.

**Request**:
- Form data with `file` field (PDF)

**Response**:
```json
{
  "job_id": "uuid",
  "status": "success",
  "summary": {
    "title": "Paper Title",
    "pages": 10,
    "sections": 5,
    "bib_entries": 25
  }
}
```

### GET /api/job/{job_id}/files
Get file tree for a conversion job.

**Response**:
```json
{
  "files": [
    {"name": "main.tex", "path": "main.tex", "type": "file"},
    {"name": "refs.bib", "path": "refs.bib", "type": "file"}
  ]
}
```

### GET /api/job/{job_id}/file/{file_path}
Get content of a specific file.

**Response**:
```json
{
  "content": "\\documentclass{article}...",
  "encoding": "utf-8"
}
```

### POST /api/job/{job_id}/compile
Compile LaTeX to PDF.

**Response**:
```json
{
  "status": "success",
  "pdf_url": "/api/job/{job_id}/pdf"
}
```

### GET /api/job/{job_id}/pdf
Download compiled PDF.

### GET /api/job/{job_id}/download
Download LaTeX project as ZIP.

## Configuration

Create `config.yaml` in the project root:

```yaml
grobid_endpoint: "http://localhost:8070"
formula_dpi: 300
timeout_sec: 600
keep_intermediates: true
```

## Development

Run in development mode with auto-reload:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -e . && \
    pip install -r web/requirements.txt

WORKDIR /app/web
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

Build and run:
```bash
docker build -t paper2latex-web .
docker run -p 8080:8080 paper2latex-web
```

### Production (with nginx)

See [deployment guide](../docs/deployment.md) for production setup with nginx reverse proxy.

## Troubleshooting

### "GROBID service not available"
- Ensure GROBID is running: `curl http://localhost:8070/api/isalive`
- Check GROBID endpoint in config

### "LaTeX compiler not found"
- Install tectonic or latexmk (see Prerequisites)
- Verify installation: `tectonic --version` or `latexmk -version`

### "Compilation failed"
- Check compilation log in browser console
- Some PDFs may have complex structures requiring manual LaTeX fixes

## Technologies

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JavaScript, Modern CSS
- **PDF Processing**: PyMuPDF
- **Structure Extraction**: GROBID
- **LaTeX Compilation**: Tectonic or Latexmk

## License

MIT License - see [LICENSE](../LICENSE) for details

## Links

- **Main Project**: https://github.com/rudaoshi/paper2latex
- **Issues**: https://github.com/rudaoshi/paper2latex/issues
- **Documentation**: https://github.com/rudaoshi/paper2latex#readme
