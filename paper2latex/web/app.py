"""
FastAPI backend for paper2latex web interface.
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional
import subprocess
import time
import logging
import traceback
import sys

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("🚀 paper2latex Web Interface - Starting Import Phase")
logger.info("=" * 80)

# Import paper2latex with error handling
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    logger.info(f"Added to sys.path: {Path(__file__).parent.parent / 'src'}")
    
    from paper2latex.pipeline import Pipeline
    from paper2latex.core.config import Config
    logger.info("✅ Successfully imported paper2latex modules")
except Exception as e:
    logger.error("❌ FATAL: Failed to import paper2latex modules")
    logger.error(f"Error: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)


def check_grobid_running(endpoint: str = "http://localhost:8070") -> bool:
    """Check if GROBID service is running."""
    try:
        response = requests.get(f"{endpoint}/api/isalive", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_grobid_docker(port: int = 8070, max_wait: int = 60) -> bool:
    """
    Start GROBID service using Docker.
    
    Args:
        port: Port to run GROBID on
        max_wait: Maximum seconds to wait for startup
        
    Returns:
        True if started successfully, False otherwise
    """
    logger.info("🚀 Starting GROBID service with Docker...")
    
    try:
        # Check if container already exists
        check_cmd = ["docker", "ps", "-a", "--filter", "name=paper2latex-grobid", "--format", "{{.Names}}"]
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        
        if "paper2latex-grobid" in result.stdout:
            # Container exists, try to start it
            logger.info("📦 Found existing GROBID container, starting...")
            subprocess.run(["docker", "start", "paper2latex-grobid"], check=True)
        else:
            # Create new container
            logger.info("📦 Creating new GROBID container...")
            docker_cmd = [
                "docker", "run", "-d",
                "--name", "paper2latex-grobid",
                "-p", f"{port}:8070",
                "lfoppiano/grobid:0.8.0"
            ]
            subprocess.run(docker_cmd, check=True)
        
        # Wait for GROBID to be ready
        logger.info("⏳ Waiting for GROBID to start...")
        endpoint = f"http://localhost:{port}"
        
        for i in range(max_wait):
            if check_grobid_running(endpoint):
                logger.info(f"✅ GROBID is ready at {endpoint}")
                return True
            time.sleep(1)
            if i % 10 == 0 and i > 0:
                logger.info(f"   Still waiting... ({i}s)")
        
        logger.error("❌ GROBID failed to start within timeout")
        return False
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Docker command failed: {e}")
        logger.info("💡 Make sure Docker is installed and running")
        return False
    except FileNotFoundError:
        logger.error("❌ Docker not found")
        logger.info("💡 Please install Docker: https://docs.docker.com/get-docker/")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to start GROBID: {e}")
        return False


def ensure_grobid_running(config: Config) -> bool:
    """
    Ensure GROBID is running, start if necessary.
    
    Args:
        config: Configuration object
        
    Returns:
        True if GROBID is available, False otherwise
    """
    endpoint = config.grobid_endpoint
    
    if check_grobid_running(endpoint):
        logger.info(f"✅ GROBID service is already running at {endpoint}")
        return True
    
    logger.warning(f"⚠️  GROBID service not found at {endpoint}")
    
    # Try to start GROBID with Docker
    # Extract port from endpoint (e.g., http://localhost:8070 -> 8070)
    try:
        port = int(endpoint.split(":")[-1].split("/")[0])
    except:
        port = 8070
    
    return start_grobid_docker(port)


app = FastAPI(title="paper2latex Web Interface")

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with detailed logging."""
    logger.error("=" * 80)
    logger.error(f"❌ UNHANDLED EXCEPTION in {request.url}")
    logger.error(f"Exception type: {type(exc).__name__}")
    logger.error(f"Exception message: {str(exc)}")
    logger.error("Traceback:")
    logger.error(traceback.format_exc())
    logger.error("=" * 80)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import tempfile

# Directories
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# Use system temporary directory for uploads and outputs
TEMP_BASE = Path(tempfile.gettempdir()) / "paper2latex_web"
UPLOAD_DIR = TEMP_BASE / "uploads"
OUTPUT_DIR = TEMP_BASE / "outputs"

logger.info(f"📂 BASE_DIR: {BASE_DIR}")
logger.info(f"📂 STATIC_DIR: {STATIC_DIR}")
logger.info(f"📂 UPLOAD_DIR: {UPLOAD_DIR}")
logger.info(f"📂 OUTPUT_DIR: {OUTPUT_DIR}")

try:
    UPLOAD_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    logger.info("✅ Created upload and output directories")
except Exception as e:
    logger.error(f"❌ Failed to create directories: {e}")
    logger.error(traceback.format_exc())

# Mount static files
try:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    logger.info(f"✅ Mounted static files from {STATIC_DIR}")
except Exception as e:
    logger.error(f"❌ Failed to mount static files: {e}")
    logger.error(traceback.format_exc())


@app.on_event("startup")
async def startup_event():
    """Check and start GROBID on startup."""
    try:
        logger.info("=" * 80)
        logger.info("🚀 Running startup event...")
        logger.info("=" * 80)
        
        config = Config()
        logger.info(f"✅ Loaded config: GROBID endpoint = {config.grobid_endpoint}")
        
        # Try to ensure GROBID is running, but don't fail if it's not
        try:
            if not ensure_grobid_running(config):
                logger.warning("⚠️  GROBID service not available")
                logger.warning("⚠️  PDF conversion will not work until GROBID is started")
                logger.info("💡 To start GROBID manually:")
                logger.info("   1. Start Docker Desktop")
                logger.info("   2. Run: docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0")
        except Exception as e:
            logger.warning(f"⚠️  Could not start GROBID: {e}")
            logger.warning("⚠️  Server will start anyway, but conversion won't work")
            logger.debug(traceback.format_exc())
        
        logger.info("=" * 80)
        logger.info("✨ Server is ready!")
        logger.info("📍 Open http://localhost:8080 in your browser")
        logger.info("=" * 80)
    except Exception as e:
        logger.error("❌ Startup event failed!")
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())


@app.get("/")
async def root():
    """Serve the main page."""
    try:
        logger.debug("GET / - Serving index.html")
        index_path = STATIC_DIR / "index.html"
        if not index_path.exists():
            logger.error(f"❌ index.html not found at {index_path}")
            raise HTTPException(404, "index.html not found")
        return FileResponse(index_path)
    except Exception as e:
        logger.error(f"❌ Error serving index.html: {e}")
        logger.error(traceback.format_exc())
        raise


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "paper2latex-web",
        "grobid": check_grobid_running()
    }


@app.post("/api/convert")
async def convert_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    engine: str = Form("grobid"),
    token: str = Form(None)
):
    """
    Upload PDF and start conversion job.
    """
    job_id = str(uuid.uuid4())
    job_dir = OUTPUT_DIR / job_id
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
        
    try:
        job_dir.mkdir(parents=True, exist_ok=True)
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"❌ Failed to create directories: {e}")
        raise HTTPException(500, f"Server storage error: {str(e)}")
    
    # Save uploaded file
    upload_path = UPLOAD_DIR / f"{job_id}.pdf"
    logger.info(f"Saving upload to: {upload_path} (Engine: {engine})")
    
    try:
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        logger.error(f"❌ Failed to save file: {e}")
        raise HTTPException(500, f"File upload failed: {str(e)}")
    
    # Run conversion in background
    background_tasks.add_task(run_conversion_task, job_id, upload_path, engine, token)
    
    return {
        "status": "processing",
        "job_id": job_id,
        "message": "Conversion started"
    }

async def run_conversion_task(job_id: str, pdf_path: Path, engine: str = "grobid", token: str = None):
    """
    Background task to run the conversion pipeline.
    """
    job_dir = OUTPUT_DIR / job_id
    
    try:
        logger.info(f"🚀 Starting conversion for job {job_id} using {engine}")
        
        if engine == "paddle":
            from paper2latex.core.config import Config
            from paper2latex.converters.layout_analysis import PaddleOCR
            
            # Configure Paddle
            config = Config()
            config.paddle_source = "aistudio"
            config.paddle_pipeline = "PaddleOCR-VL"
            if token:
                config.paddle_access_token = token
            elif os.getenv("PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN"):
                config.paddle_access_token = os.getenv("PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN")
            
            # Run Paddle Converter
            try:
                converter = PaddleOCR(config)
                # Need to implement simple markdown conversion or use valid output mode
                # The LayoutAnalyzer interface has convert(input_path, output_mode)
                # PaddleOCR.convert(output_mode="simple") returns text.
                markdown = converter.convert(str(pdf_path), "simple")
                
                # Save results
                # 1. Report
                report_path = job_dir / "latex" / "report.md"
                report_path.parent.mkdir(parents=True, exist_ok=True)
                with open(report_path, "w") as f:
                    f.write("# PaddleOCR Conversion Result\n\n")
                    f.write(markdown)
                
                # 2. Main.tex (Wrapper)
                main_tex_path = job_dir / "latex" / "main.tex"
                with open(main_tex_path, "w") as f:
                    f.write("\\documentclass{article}\n")
                    f.write("\\usepackage{markdown}\n")
                    f.write("\\begin{document}\n")
                    f.write("% Content generated by PaddleOCR-VL\n")
                    # Simple sanitize
                    clean_md = markdown.replace("{", "\\{").replace("}", "\\}").replace("_", "\\_")
                    f.write(clean_md)
                    f.write("\n\\end{document}")
                
                # Copy original
                shutil.copy2(pdf_path, job_dir / "latex" / "original.pdf")
                
                logger.info(f"✅ Paddle conversion completed for {job_id}")
                
                # Create metadata
                import json
                metadata = {
                    "job_id": job_id,
                    "status": "success",
                    "engine": "paddle",
                    "summary": {"pages": 0, "sections": 0} # TODO
                }
                with open(job_dir / "metadata.json", "w") as f:
                    json.dump(metadata, f)
                
            except Exception as e:
                logger.error(f"❌ Paddle conversion failed: {e}")
                # Write error log
                error_dir = job_dir / "latex"
                error_dir.mkdir(parents=True, exist_ok=True)
                with open(error_dir / "error.log", "w") as f:
                    f.write(str(e))
                
                # Create fail metadata
                import json
                with open(job_dir / "metadata.json", "w") as f:
                    json.dump({"job_id": job_id, "status": "failed", "error": str(e)}, f)
        
        else:
            # GROBID
            config = Config()
            pipeline = Pipeline(config)
            result = pipeline.run_conversion(str(pdf_path), str(job_dir))
            
            # Save metadata (was missing in previous version of this function block in replacement?)
            # Actually run_conversion saves its own artifacts but we need metadata.json for the frontend
            import json
            metadata = {
                "job_id": job_id,
                "status": result.status,
                "summary": result.summary,
                "quality_report": result.quality_report
            }
            with open(job_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            if result.status == "failed":
                logger.error(f"❌ Job {job_id} failed")
            else:
                logger.info(f"✅ Job {job_id} completed successfully")
            
    except Exception as e:
        logger.error(f"❌ Unexpected error in background task: {e}")
        # Ensure metadata exists even on crash
        try:
             import json
             with open(job_dir / "metadata.json", "w") as f:
                json.dump({"job_id": job_id, "status": "failed", "error": str(e)}, f)
        except:
            pass


@app.get("/api/job/{job_id}/files")
async def get_file_tree(job_id: str):
    """
    Get file tree for a job.
    
    Returns:
        {
            "files": [
                {"name": "main.tex", "path": "main.tex", "type": "file", "size": 1234},
                {"name": "refs.bib", "path": "refs.bib", "type": "file", "size": 567},
                ...
            ]
        }
    """
    job_dir = OUTPUT_DIR / job_id / "latex"
    
    if not job_dir.exists():
        raise HTTPException(404, "Job not found")
    
    files = []
    
    def scan_directory(path: Path, rel_path: str = ""):
        """Recursively scan directory."""
        items = []
        
        for item in sorted(path.iterdir()):
            rel = os.path.join(rel_path, item.name) if rel_path else item.name
            
            if item.is_file():
                items.append({
                    "name": item.name,
                    "path": rel,
                    "type": "file",
                    "size": item.stat().st_size,
                })
            elif item.is_dir() and item.name not in ["__pycache__", ".git"]:
                children = scan_directory(item, rel)
                items.append({
                    "name": item.name,
                    "path": rel,
                    "type": "directory",
                    "children": children,
                })
        
        return items
    
    files = scan_directory(job_dir)
    
    return {"files": files}


@app.get("/api/job/{job_id}/file/{file_path:path}")
async def get_file_content(job_id: str, file_path: str):
    """
    Get content of a specific file.
    
    For text files: returns JSON with content.
    For binary files: returns the file directly.
    """
    try:
        job_dir = OUTPUT_DIR / job_id / "latex"
        full_path = job_dir / file_path
        
        logger.debug(f"GET file: {file_path} from job {job_id}")
        
        # Security: prevent path traversal
        if not str(full_path.resolve()).startswith(str(job_dir.resolve())):
            logger.warning(f"⚠️  Path traversal attempt: {file_path}")
            raise HTTPException(403, "Access denied")
        
        if not full_path.exists() or not full_path.is_file():
            logger.warning(f"⚠️  File not found: {full_path}")
            raise HTTPException(404, "File not found")
        
        # Determine if file is binary based on extension
        binary_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico'}
        is_binary = full_path.suffix.lower() in binary_extensions
        
        if is_binary:
            # Return binary file directly
            logger.debug(f"Serving binary file: {file_path}")
            media_type = {
                '.pdf': 'application/pdf',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
            }.get(full_path.suffix.lower(), 'application/octet-stream')
            
            headers = {
                "Content-Disposition": f"inline; filename={full_path.name}"
            }
            
            return FileResponse(
                full_path,
                media_type=media_type,
                filename=full_path.name,
                headers=headers
            )
        else:
            # Read text file
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                logger.debug(f"Served text file: {file_path} ({len(content)} chars)")
                return {
                    "content": content,
                    "encoding": "utf-8"
                }
            except UnicodeDecodeError:
                # Fallback: if UTF-8 fails, return as binary
                logger.warning(f"⚠️  Could not decode {file_path} as UTF-8, serving as binary")
                return FileResponse(
                    full_path,
                    media_type='application/octet-stream',
                    filename=full_path.name
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error serving file {file_path}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Error reading file: {str(e)}")


@app.post("/api/job/{job_id}/compile")
async def compile_latex(job_id: str):
    """
    Compile LaTeX to PDF.
    """
    try:
        job_dir = OUTPUT_DIR / job_id / "latex"
        logger.info(f"Compiling LaTeX for job {job_id} in {job_dir}")
        
        if not job_dir.exists():
            logger.error(f"❌ Job directory not found: {job_dir}")
            raise HTTPException(404, "Job not found")
        
        main_tex = job_dir / "main.tex"
        if not main_tex.exists():
            logger.error(f"❌ main.tex not found in {job_dir}")
            raise HTTPException(404, "main.tex not found")
        
        # Check for compilers
        has_tectonic = shutil.which("tectonic") is not None
        has_latexmk = shutil.which("latexmk") is not None
        
        logger.info(f"Compilers found: tectonic={has_tectonic}, latexmk={has_latexmk}")
        
        if not has_tectonic and not has_latexmk:
            logger.error("❌ No LaTeX compiler found (tectonic or latexmk required)")
            raise HTTPException(500, "LaTeX compiler not found. Please install tectonic or latexmk.")

        # Compile
        try:
            if has_tectonic:
                logger.info("🔧 Compiling with tectonic...")
                cmd = ["tectonic", "main.tex"]
                result = subprocess.run(
                    cmd,
                    cwd=str(job_dir),
                    capture_output=True,
                    text=True,
                    timeout=300,  # Allow 5 mins for first-time package downloads
                )
            else:
                logger.info("🔧 Compiling with latexmk...")
                cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"]
                result = subprocess.run(
                    cmd,
                    cwd=str(job_dir),
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            
            logger.info(f"Compilation return code: {result.returncode}")
            
            if result.returncode == 0:
                logger.info("✅ Compilation successful")
                return {
                    "status": "success",
                    "pdf_url": f"/api/job/{job_id}/pdf",
                    "log": result.stdout
                }
            else:
                logger.warning("⚠️  Compilation failed")
                logger.warning(f"STDOUT: {result.stdout[:500]}...")
                logger.warning(f"STDERR: {result.stderr[:500]}...")
                return {
                    "status": "error",
                    "message": "LaTeX compilation failed",
                    "log": result.stdout + "\n" + result.stderr
                }
        
        except subprocess.TimeoutExpired:
            logger.error("❌ Compilation timed out")
            raise HTTPException(500, "LaTeX compilation timed out")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during compilation: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Compilation error: {str(e)}")


@app.get("/api/job/{job_id}/pdf")
async def get_compiled_pdf(job_id: str):
    """Serve the compiled PDF."""
    pdf_path = OUTPUT_DIR / job_id / "latex" / "main.pdf"
    
    if not pdf_path.exists():
        raise HTTPException(404, "PDF not found. Please compile first.")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="converted.pdf"
    )


@app.get("/api/job/{job_id}/download")
async def download_latex(job_id: str):
    """Download LaTeX project as ZIP."""
    import zipfile
    import io
    
    job_dir = OUTPUT_DIR / job_id / "latex"
    
    if not job_dir.exists():
        raise HTTPException(404, "Job not found")
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in job_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(job_dir)
                zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)
    
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=latex_{job_id}.zip"}
    )


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("🎨 paper2latex Web Interface")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:8080")
    print("🔄 Auto-reload: ENABLED (dev mode)")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,  # Enable auto-reload
        reload_dirs=[str(Path(__file__).parent)],  # Watch web directory
        log_level="info"
    )
