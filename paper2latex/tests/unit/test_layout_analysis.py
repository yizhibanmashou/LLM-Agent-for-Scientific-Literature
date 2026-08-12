
import json
import unittest
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("mcp", reason="MCP client dependency is not installed in this environment")

from paper2latex.converters.layout_analysis import PaddleOCR
from paper2latex.core.config import Config


class TestPaddleOCR(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.config.paddle_pipeline = "PaddleOCR-VL"
        self.config.paddle_source = "aistudio"  # triggers MCP usage or cloud logic
        
    @patch("paper2latex.converters.layout_analysis.ClientSession")
    @patch("paper2latex.converters.layout_analysis.stdio_client")
    def test_convert_detailed_json_parsing(self, mock_stdio, MockSession):
        from unittest.mock import AsyncMock
        
        # Setup Mock Session
        mock_session_instance = MockSession.return_value
        mock_session_instance.__aenter__.return_value = mock_session_instance
        
        # Configure async methods
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock()
        mock_session_instance.call_tool = AsyncMock()
        
        # Setup Mock stdio_client context
        # stdio_client is an async context manager yielding (read, write)
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        
        # Mock tools result
        mock_tools_res = MagicMock()
        mock_tools_res.tools = [MagicMock(name="paddleocr_vl")]
        # Ensure the mock object's name attribute is correct for the logic
        mock_tools_res.tools[0].name = "paddleocr_vl"
        mock_session_instance.list_tools.return_value = mock_tools_res
        
        # Mock result from MCPServer
        mock_content = MagicMock()
        mock_content.type = "text"
        fake_layout = [{"type": "title", "text": "Test Doc"}]
        mock_content.text = json.dumps(fake_layout)
        
        mock_result = MagicMock()
        mock_result.content = [mock_content]
        mock_session_instance.call_tool.return_value = mock_result
        
        # Initialize Converter
        converter = PaddleOCR(self.config)
        
        # Run conversion
        result = converter.convert("dummy.pdf", output_mode="detailed")
                 
        # Verify result is valid JSON string
        parsed = json.loads(result)
        self.assertEqual(parsed, fake_layout)
        self.assertEqual(len(parsed), 1)

    @patch("paper2latex.converters.layout_analysis.ClientSession")
    @patch("paper2latex.converters.layout_analysis.stdio_client")
    def test_convert_fallback_text(self, mock_stdio, MockSession):
        from unittest.mock import AsyncMock
        
        mock_session_instance = MockSession.return_value
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock()
        mock_session_instance.call_tool = AsyncMock()

        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        
        mock_tools_res = MagicMock()
        mock_tools_res.tools = [MagicMock(name="paddleocr_vl")]
        mock_tools_res.tools[0].name = "paddleocr_vl"
        mock_session_instance.list_tools.return_value = mock_tools_res

        mock_content = MagicMock()
        mock_content.type = "text"
        mock_content.text = "Just some raw text."
        
        mock_result = MagicMock()
        mock_result.content = [mock_content]
        mock_session_instance.call_tool.return_value = mock_result
        
        converter = PaddleOCR(self.config)
        result = converter.convert("dummy.pdf", output_mode="simple")
             
        self.assertEqual(result.strip(), "Just some raw text.")

if __name__ == '__main__':
    unittest.main()
