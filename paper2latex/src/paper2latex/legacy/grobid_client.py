"""
GROBID client for TEI XML extraction.
"""

import requests
import logging
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class GROBIDClient:
    """Client for GROBID REST API."""
    
    def __init__(self, endpoint: str = "http://localhost:8070", timeout: int = 600):
        """
        Initialize GROBID client.
        
        Args:
            endpoint: GROBID service endpoint
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
    
    def process_fulltext(
        self,
        pdf_path: str,
        enable_coordinates: bool = True,
    ) -> str:
        """
        Process PDF to extract fulltext as TEI XML.
        
        Args:
            pdf_path: Path to PDF file
            enable_coordinates: Include coordinate information
            
        Returns:
            TEI XML string
            
        Raises:
            RuntimeError: If GROBID processing fails
        """
        url = f"{self.endpoint}/api/processFulltextDocument"
        
        # Prepare request
        files = {
            "input": open(pdf_path, "rb")
        }
        
        data = {}
        if enable_coordinates:
            data["teiCoordinates"] = "biblStruct,figure,formula,ref,s,persName,head"
        
        try:
            logger.info(f"Sending PDF to GROBID: {pdf_path}")
            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                logger.info("GROBID processing successful")
                return response.text
            else:
                error_msg = f"GROBID returned status {response.status_code}: {response.text[:200]}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.Timeout:
            raise RuntimeError(f"GROBID request timed out after {self.timeout}s")
        except requests.RequestException as e:
            raise RuntimeError(f"GROBID request failed: {e}")
        finally:
            files["input"].close()
    
    def health_check(self) -> bool:
        """
        Check if GROBID service is available.
        
        Returns:
            True if service is healthy
        """
        try:
            url = f"{self.endpoint}/api/isalive"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"GROBID health check failed: {e}")
            return False
