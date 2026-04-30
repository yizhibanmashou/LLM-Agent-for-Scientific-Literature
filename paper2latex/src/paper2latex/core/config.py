"""
Configuration management for paper2latex MCP server.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _load_root_dotenv() -> None:
    path = PROJECT_ROOT / ".env"
    if not path.is_file():
        return
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and os.getenv(key) is None:
            os.environ[key] = value


@dataclass
class Config:
    """Configuration for paper2latex."""
    
    # GROBID
    grobid_endpoint: str = "http://localhost:8070"
    
    # Formula processing
    formula_dpi: int = 300
    formula_ocr: str = "none"  # "pix2tex" | "none" | "custom"
    
    # Figure extraction
    figure_extract: bool = True
    
    # Compilation
    enable_compile_check: bool = False
    
    # Paths
    temp_dir: str = str(PROJECT_ROOT / "tmp" / "paper2latex")
    config_dir: str = "~/.config/paper2latex-mcp"
    
    # Processing
    timeout_sec: int = 600
    keep_intermediates: bool = True
    max_pages: Optional[int] = None
    
    # Language
    language_hint: str = "auto"
    
    # PaddleOCR (MCP/Cloud)
    paddle_pipeline: str = "PaddleOCR-VL"
    paddle_source: str = "local"  # "local" | "aistudio"
    paddle_server_url: str = "https://xd8cd4ufsei1h4u9.aistudio-app.com"
    paddle_access_token: Optional[str] = None
    
    def __post_init__(self):
        """Expand user paths and load env vars."""
        _load_root_dotenv()
        self.temp_dir = os.path.expanduser(self.temp_dir)
        self.config_dir = os.path.expanduser(self.config_dir)
        
        # Load env vars if not set
        self.paddle_pipeline = os.getenv("PAPER2LATEX_PADDLE_PIPELINE", self.paddle_pipeline)
        self.paddle_source = os.getenv("PAPER2LATEX_PADDLE_SOURCE", self.paddle_source)
        self.paddle_server_url = os.getenv("PAPER2LATEX_PADDLE_API_URL", self.paddle_server_url)
        if not self.paddle_access_token:
            self.paddle_access_token = (
                os.getenv("PAPER2LATEX_PADDLE_API_TOKEN")
                or os.getenv("PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN")
            )


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file. If None, uses default location.
        
    Returns:
        Config object
    """
    if config_path is None:
        config_path = os.path.expanduser("~/.config/paper2latex-mcp/config.yaml")
    
    config = Config()
    
    # Load from file if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}
            
            # Update config with file values
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
    
    return config


def save_default_config(config_path: Optional[str] = None) -> str:
    """
    Save default configuration to file.
    
    Args:
        config_path: Path to save config. If None, uses default location.
        
    Returns:
        Path where config was saved
    """
    if config_path is None:
        config_path = os.path.expanduser("~/.config/paper2latex-mcp/config.yaml")
    
    # Create directory if needed
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Default config as dict
    default_config = {
        "grobid_endpoint": "http://localhost:8070",
        "formula_dpi": 300,
        "formula_ocr": "none",
        "figure_extract": True,
        "enable_compile_check": False,
        "temp_dir": str(PROJECT_ROOT / "tmp" / "paper2latex"),
        "timeout_sec": 600,
        "keep_intermediates": True,
        "language_hint": "auto",
    }
    
    with open(config_path, "w") as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    return config_path
