import warnings
import logging
from typing import Optional, Dict, Any, List
from src.file_management.unified_manager import UnifiedFileManager as NewUnifiedFileManager, UploadResult, FileUploadError

logger = logging.getLogger(__name__)
DEPRECATION_MESSAGE = "DEPRECATED: src.storage.unified_file_manager. Use src.file_management.unified_manager"

def _emit_deprecation_warning(method_name: str):
    warnings.warn(f"{DEPRECATION_MESSAGE} - {method_name}", DeprecationWarning, stacklevel=3)
    logger.warning(f"DEPRECATED: {method_name}")

class UnifiedFileManager:
    def __init__(self, *args, **kwargs):
        _emit_deprecation_warning("UnifiedFileManager.__init__")
        self._manager = NewUnifiedFileManager(*args, **kwargs)
    async def upload_file(self, file_path: str, provider: Optional[str] = None, purpose: Optional[str] = None, **kwargs) -> UploadResult:
        _emit_deprecation_warning("upload_file")
        return await self._manager.upload_file(file_path, provider, purpose, **kwargs)
    async def delete_file(self, file_id: str, provider: Optional[str] = None, **kwargs) -> bool:
        _emit_deprecation_warning("delete_file")
        return await self._manager.delete_file(file_id, provider, **kwargs)
    async def list_files(self, provider: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        _emit_deprecation_warning("list_files")
        return await self._manager.list_files(provider, **kwargs)
    def __getattr__(self, name: str):
        _emit_deprecation_warning(f"UnifiedFileManager.{name}")
        return getattr(self._manager, name)

warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
__all__ = ['UnifiedFileManager', 'UploadResult', 'FileUploadError']
