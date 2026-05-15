
"""
Layout Analysis Module for paper2latex.
Defines the interface and implementations for extracting layout information from PDFs.
"""

import logging
import asyncio
import os
import shutil
import sys
from abc import ABC, abstractmethod
from typing import Optional

# MCP Imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)

class LayoutAnalyzer(ABC):
    """Abstract base class for layout analysis engines."""
    
    @abstractmethod
    def convert(self, pdf_path: str, output_mode: str = "simple") -> str:
        """
        Convert PDF to layout representation.
        
        Args:
            pdf_path: Path to the input PDF.
            output_mode: "simple" (text only) or "detailed" (JSON structure).
            
        Returns:
            String containing the result (JSON or text).
        """
        pass

class PaddleOCR(LayoutAnalyzer):
    """
    PaddleOCR implementation of LayoutAnalyzer.
    Uses paddleocr-mcp library to connect to AI Studio services via MCP protocol.
    """
    
    def __init__(self, config):
        if not MCP_AVAILABLE:
            raise ImportError("mcp library not installed. Please install with: pip install mcp")
        
        self.config = config
        self.last_raw_response = None
        
        # Determine command to run the server
        if shutil.which("paddleocr_mcp"):
            self.command = "paddleocr_mcp"
            self.args = []
        else:
            self.command = sys.executable
            self.args = ["-m", "paddleocr_mcp"]

        # Environment variables for the server
        self.env = os.environ.copy()
        if hasattr(config, 'paddle_pipeline'):
             self.env["PADDLEOCR_MCP_PIPELINE"] = config.paddle_pipeline
        
        if hasattr(config, 'paddle_source'):
            self.env["PADDLEOCR_MCP_PPOCR_SOURCE"] = config.paddle_source
            
        if hasattr(config, 'paddle_server_url') and config.paddle_server_url:
            self.env["PADDLEOCR_MCP_SERVER_URL"] = config.paddle_server_url
            
        if hasattr(config, 'paddle_access_token') and config.paddle_access_token:
            self.env["PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN"] = config.paddle_access_token
        self.env.setdefault("PADDLEOCR_MCP_TIMEOUT", os.getenv("PADDLEOCR_MCP_TIMEOUT", "900"))
            
        logger.info(f"Initialized Paddle OCR Engine for {getattr(config, 'paddle_pipeline', 'Unknown')}")

    async def _convert_async(self, pdf_path: str, output_mode: str = "simple") -> str:
        """Async conversion via MCP protocol"""
        
        server_params = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=self.env
        )
        
        logger.info(f"🚀 Starting MCP Server: {self.command} {' '.join(self.args)}")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools_result = await session.list_tools()
                tool_names = [t.name for t in tools_result.tools]
                
                # Determine tool name based on pipeline config
                tool_name = "ocr"
                pipeline = getattr(self.config, 'paddle_pipeline', "PaddleOCR-VL")
                
                if pipeline.startswith("PaddleOCR-VL"):
                    tool_name = "paddleocr_vl"
                elif pipeline == "PP-StructureV3":
                    tool_name = "pp_structurev3"
                
                if tool_name not in tool_names:
                     if "ocr" in tool_names: tool_name = "ocr"
                     else: raise RuntimeError(f"Tool {tool_name} not found in {tool_names}")

                logger.info(f"📤 invoking tool '{tool_name}' with mode '{output_mode}'")
                
                result = await session.call_tool(
                    tool_name,
                    arguments={
                        "input_data": str(pdf_path),
                        "output_mode": output_mode,
                        "file_type": "pdf",
                        "return_images": True
                    }
                )

                self.last_raw_response = self._serialize_tool_result(result)
                
                # Parse result
                final_output = ""
                found_json = False
                all_json_data = []
                is_list_structure = False
                
                for content in result.content:
                    if content.type == 'text':
                        text = content.text
                        if output_mode == "detailed":
                            try:
                                import json
                                parsed = json.loads(text)
                                if isinstance(parsed, list):
                                    is_list_structure = True
                                    all_json_data.extend(parsed)
                                    found_json = True
                                elif isinstance(parsed, dict):
                                    all_json_data.append(parsed)
                                    found_json = True
                            except json.JSONDecodeError:
                                pass
                        
                        if output_mode == "simple" or not found_json:
                             final_output += text + "\n"

                if found_json and output_mode == "detailed":
                    import json
                    if len(all_json_data) == 1 and isinstance(all_json_data[0], dict) and not is_list_structure:
                        return json.dumps(all_json_data[0], ensure_ascii=False)
                    return json.dumps(all_json_data, ensure_ascii=False)
                
                return final_output

    def convert(self, pdf_path: str, output_mode: str = "simple") -> str:
        """Synchronous wrapper for conversion."""
        return asyncio.run(self._convert_async(pdf_path, output_mode))

    def _serialize_tool_result(self, result):
        """Keep a JSON-serializable copy of the MCP tool response for audit."""
        contents = []
        for content in getattr(result, "content", []) or []:
            item = {"type": getattr(content, "type", "")}
            text = getattr(content, "text", None)
            if text is not None:
                item["text"] = text
            mime_type = getattr(content, "mimeType", None) or getattr(content, "mime_type", None)
            if mime_type is not None:
                item["mime_type"] = mime_type
            data = getattr(content, "data", None)
            if data is not None:
                item["data_length"] = len(data) if hasattr(data, "__len__") else None
            contents.append(item)
        return {"content": contents}
