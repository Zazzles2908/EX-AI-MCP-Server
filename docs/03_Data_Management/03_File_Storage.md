# File Storage Management

## Purpose & Responsibility

This component manages file storage operations across multiple backends (S3, local filesystem), handling uploads, downloads, and cleanup with support for both cloud and local storage.

## Storage Backends

### Storage Interface

```python
# interfaces/storage_backend.py
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class StorageBackend(ABC):
    @abstractmethod
    async def upload(
        self,
        file_path: str,
        file_data: BinaryIO,
        metadata: dict = None
    ) -> str:
        """Upload file and return file ID"""
        pass
    
    @abstractmethod
    async def download(self, file_id: str) -> bytes:
        """Download file by ID"""
        pass
    
    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        """Delete file by ID"""
        pass
    
    @abstractmethod
    async def exists(self, file_id: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    async def get_metadata(self, file_id: str) -> dict:
        """Get file metadata"""
        pass
```

### Local Storage Backend

```python
# backends/local_storage.py
import os
import json
import shutil
from pathlib import Path
from typing import BinaryIO, Optional
from interfaces.storage_backend import StorageBackend

class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path = self.base_path / "metadata"
        self.metadata_path.mkdir(exist_ok=True)
    
    async def upload(
        self,
        file_path: str,
        file_data: BinaryIO,
        metadata: dict = None
    ) -> str:
        """Upload file to local storage"""
        import uuid
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        storage_path = self.base_path / file_id
        with open(storage_path, 'wb') as f:
            shutil.copyfileobj(file_data, f)
        
        # Save metadata
        metadata = metadata or {}
        metadata.update({
            "file_id": file_id,
            "original_path": file_path,
            "size": os.path.getsize(storage_path)
        })
        
        metadata_file = self.metadata_path / f"{file_id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        return file_id
    
    async def download(self, file_id: str) -> bytes:
        """Download file from local storage"""
        storage_path = self.base_path / file_id
        
        if not storage_path.exists():
            raise FileNotFoundError(f"File {file_id} not found")
        
        with open(storage_path, 'rb') as f:
            return f.read()
    
    async def delete(self, file_id: str) -> bool:
        """Delete file from local storage"""
        storage_path = self.base_path / file_id
        metadata_file = self.metadata_path / f"{file_id}.json"
        
        deleted = False
        
        if storage_path.exists():
            storage_path.unlink()
            deleted = True
        
        if metadata_file.exists():
            metadata_file.unlink()
        
        return deleted
    
    async def exists(self, file_id: str) -> bool:
        """Check if file exists"""
        storage_path = self.base_path / file_id
        return storage_path.exists()
    
    async def get_metadata(self, file_id: str) -> dict:
        """Get file metadata"""
        metadata_file = self.metadata_path / f"{file_id}.json"
        
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata for {file_id} not found")
        
        with open(metadata_file, 'r') as f:
            return json.load(f)
```

### S3 Storage Backend

```python
# backends/s3_storage.py
import boto3
from typing import BinaryIO, Optional
from interfaces.storage_backend import StorageBackend

class S3StorageBackend(StorageBackend):
    def __init__(
        self,
        bucket_name: str,
        aws_access_key: str,
        aws_secret_key: str,
        region: str = "us-east-1"
    ):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
    
    async def upload(
        self,
        file_path: str,
        file_data: BinaryIO,
        metadata: dict = None
    ) -> str:
        """Upload file to S3"""
        import uuid
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Upload to S3
        self.s3_client.upload_fileobj(
            file_data,
            self.bucket_name,
            file_id,
            ExtraArgs={
                'Metadata': metadata or {}
            }
        )
        
        return file_id
    
    async def download(self, file_id: str) -> bytes:
        """Download file from S3"""
        from io import BytesIO
        
        buffer = BytesIO()
        self.s3_client.download_fileobj(
            self.bucket_name,
            file_id,
            buffer
        )
        
        buffer.seek(0)
        return buffer.read()
    
    async def delete(self, file_id: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_id
            )
            return True
        except Exception:
            return False
    
    async def exists(self, file_id: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_id
            )
            return True
        except:
            return False
    
    async def get_metadata(self, file_id: str) -> dict:
        """Get file metadata from S3"""
        response = self.s3_client.head_object(
            Bucket=self.bucket_name,
            Key=file_id
        )
        
        return {
            "file_id": file_id,
            "size": response['ContentLength'],
            "last_modified": response['LastModified'],
            "metadata": response.get('Metadata', {})
        }
```

## File Service

### Unified File Service

```python
# services/file_service.py
from typing import BinaryIO, Optional
from interfaces.storage_backend import StorageBackend
from backends.local_storage import LocalStorageBackend
from backends.s3_storage import S3StorageBackend

class FileService:
    def __init__(self, backend: str = "local", **backend_config):
        self.backend = self._initialize_backend(backend, backend_config)
    
    def _initialize_backend(
        self,
        backend: str,
        config: dict
    ) -> StorageBackend:
        """Initialize storage backend"""
        if backend == "local":
            return LocalStorageBackend(
                base_path=config.get("base_path", "./storage")
            )
        elif backend == "s3":
            return S3StorageBackend(
                bucket_name=config["bucket_name"],
                aws_access_key=config["aws_access_key"],
                aws_secret_key=config["aws_secret_key"],
                region=config.get("region", "us-east-1")
            )
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    async def upload_file(
        self,
        file_path: str,
        file_data: BinaryIO,
        metadata: dict = None
    ) -> str:
        """Upload file to storage"""
        file_id = await self.backend.upload(file_path, file_data, metadata)
        
        # Log to Supabase (fire-and-forget)
        asyncio.create_task(
            self.log_upload(file_id, file_path, metadata)
        )
        
        return file_id
    
    async def download_file(self, file_id: str) -> bytes:
        """Download file from storage"""
        return await self.backend.download(file_id)
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from storage"""
        deleted = await self.backend.delete(file_id)
        
        if deleted:
            # Log deletion to Supabase
            asyncio.create_task(
                self.log_deletion(file_id)
            )
        
        return deleted
    
    async def cleanup_old_files(self, days: int = 30):
        """Cleanup files older than specified days"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get old files from Supabase
        old_files = await self.get_old_files(cutoff_date)
        
        deleted_count = 0
        for file_id in old_files:
            if await self.delete_file(file_id):
                deleted_count += 1
        
        return deleted_count
    
    async def log_upload(self, file_id: str, file_path: str, metadata: dict):
        """Log file upload to Supabase"""
        from services.supabase_service import SupabaseService
        
        supabase = SupabaseService()
        await supabase.insert("file_uploads", {
            "file_id": file_id,
            "file_path": file_path,
            "metadata": metadata,
            "uploaded_at": datetime.now()
        })
    
    async def log_deletion(self, file_id: str):
        """Log file deletion to Supabase"""
        from services.supabase_service import SupabaseService
        
        supabase = SupabaseService()
        await supabase.update(
            "file_uploads",
            {"file_id": file_id},
            {"deleted_at": datetime.now()}
        )
```

## API Integration

### File Endpoints

```python
# routes/files.py
from fastapi import APIRouter, UploadFile, HTTPException
from services.file_service import FileService

router = APIRouter()
file_service = FileService(backend="local")

@router.post("/upload")
async def upload_file(file: UploadFile):
    """Upload a file"""
    try:
        file_id = await file_service.upload_file(
            file_path=file.filename,
            file_data=file.file,
            metadata={
                "content_type": file.content_type,
                "filename": file.filename
            }
        )
        
        return {
            "file_id": file_id,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download a file"""
    try:
        file_data = await file_service.download_file(file_id)
        
        from fastapi.responses import Response
        return Response(
            content=file_data,
            media_type="application/octet-stream"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

@router.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    """Delete a file"""
    deleted = await file_service.delete_file(file_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"message": "File deleted successfully"}

@router.post("/cleanup")
async def cleanup_files(days: int = 30):
    """Cleanup old files"""
    deleted_count = await file_service.cleanup_old_files(days)
    
    return {
        "message": f"Deleted {deleted_count} files",
        "deleted_count": deleted_count
    }
```

## Configuration

### Storage Configuration

```yaml
# config/storage.yaml
storage:
  backend: "local"  # or "s3"
  
  local:
    base_path: "./storage"
  
  s3:
    bucket_name: "exai-files"
    region: "us-east-1"
    # AWS credentials from environment variables
  
  cleanup:
    enabled: true
    retention_days: 30
    schedule: "0 2 * * *"  # Daily at 2 AM
```

## Best Practices

1. **Backend Abstraction**: Use interface for easy backend switching
2. **Metadata Tracking**: Store file metadata in Supabase
3. **Cleanup Strategy**: Implement automated cleanup for old files
4. **Error Handling**: Handle storage errors gracefully
5. **Security**: Validate file types and sizes before upload

## Integration Points

- **AI Providers**: Upload files for AI model processing
- **Supabase**: Tracks file metadata and audit trail
- **API Layer**: Exposes file operations via REST
- **Cleanup Jobs**: Automated file cleanup scheduling

