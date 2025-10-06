"""
File Uploader - Handle file uploads to Kimi and GLM

Supports:
- Kimi file upload API
- GLM file upload API
- File tracking
- Upload verification

Created: 2025-10-05
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv(".env.testing")

logger = logging.getLogger(__name__)


class FileUploader:
    """
    Handle file uploads to Kimi and GLM providers.
    
    Features:
    - Upload files to Kimi
    - Upload files to GLM
    - Track uploaded files
    - Verify uploads
    """
    
    def __init__(self):
        """Initialize the file uploader."""
        self.kimi_api_key = os.getenv("KIMI_API_KEY")
        self.kimi_base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
        
        self.glm_api_key = os.getenv("GLM_API_KEY")
        self.glm_base_url = os.getenv("GLM_BASE_URL", "https://api.z.ai/api/paas/v4")
        
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE_BYTES", "10485760"))  # 10 MB
        
        # Track uploaded files
        self.uploaded_files = {
            "kimi": {},
            "glm": {}
        }
        
        logger.info("File uploader initialized")
    
    def upload_to_kimi(self, file_path: str, purpose: str = "file-extract") -> Dict[str, Any]:
        """
        Upload file to Kimi.
        
        Args:
            file_path: Path to file
            purpose: Upload purpose (file-extract, etc.)
        
        Returns:
            Upload response with file_id
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
        
        url = f"{self.kimi_base_url}/files"
        headers = {
            "Authorization": f"Bearer {self.kimi_api_key}"
        }
        
        try:
            with open(file_path, "rb") as f:
                files = {
                    "file": (file_path.name, f, self._get_content_type(file_path)),
                    "purpose": (None, purpose)
                }
                
                response = requests.post(
                    url,
                    headers=headers,
                    files=files,
                    timeout=60
                )
                response.raise_for_status()
            
            result = response.json()
            file_id = result.get("id")
            
            # Track uploaded file
            self.uploaded_files["kimi"][file_id] = {
                "file_id": file_id,
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_size": file_size,
                "purpose": purpose,
                "response": result
            }
            
            logger.info(f"Uploaded file to Kimi: {file_path.name} (ID: {file_id})")
            
            return result
        
        except Exception as e:
            logger.error(f"Kimi file upload failed: {e}")
            raise
    
    def upload_to_glm(self, file_path: str, purpose: str = "retrieval") -> Dict[str, Any]:
        """
        Upload file to GLM.
        
        Args:
            file_path: Path to file
            purpose: Upload purpose (retrieval, etc.)
        
        Returns:
            Upload response with file_id
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
        
        url = f"{self.glm_base_url}/files"
        headers = {
            "Authorization": f"Bearer {self.glm_api_key}"
        }
        
        try:
            with open(file_path, "rb") as f:
                files = {
                    "file": (file_path.name, f, self._get_content_type(file_path)),
                    "purpose": (None, purpose)
                }
                
                response = requests.post(
                    url,
                    headers=headers,
                    files=files,
                    timeout=60
                )
                response.raise_for_status()
            
            result = response.json()
            file_id = result.get("id")
            
            # Track uploaded file
            self.uploaded_files["glm"][file_id] = {
                "file_id": file_id,
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_size": file_size,
                "purpose": purpose,
                "response": result
            }
            
            logger.info(f"Uploaded file to GLM: {file_path.name} (ID: {file_id})")
            
            return result
        
        except Exception as e:
            logger.error(f"GLM file upload failed: {e}")
            raise
    
    def get_uploaded_file(self, provider: str, file_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an uploaded file."""
        return self.uploaded_files.get(provider, {}).get(file_id)
    
    def list_uploaded_files(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """List all uploaded files."""
        if provider:
            return {provider: self.uploaded_files.get(provider, {})}
        return self.uploaded_files
    
    def _get_content_type(self, file_path: Path) -> str:
        """Get content type for file."""
        suffix = file_path.suffix.lower()
        
        content_types = {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".json": "application/json",
            ".csv": "text/csv",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".py": "text/x-python",
            ".js": "text/javascript",
            ".html": "text/html",
            ".xml": "application/xml"
        }
        
        return content_types.get(suffix, "application/octet-stream")


# Example usage
if __name__ == "__main__":
    uploader = FileUploader()
    
    # Create a test file
    test_file = Path("tool_validation_suite/fixtures/sample_files/test.txt")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("This is a test file for upload validation.")
    
    # Upload to Kimi
    try:
        kimi_result = uploader.upload_to_kimi(str(test_file))
        print(f"Kimi upload: {kimi_result.get('id')}")
    except Exception as e:
        print(f"Kimi upload failed: {e}")
    
    # Upload to GLM
    try:
        glm_result = uploader.upload_to_glm(str(test_file))
        print(f"GLM upload: {glm_result.get('id')}")
    except Exception as e:
        print(f"GLM upload failed: {e}")
    
    # List uploaded files
    print(json.dumps(uploader.list_uploaded_files(), indent=2))

