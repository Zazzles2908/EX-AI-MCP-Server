"""
Cross-Platform File Registry Implementation

A comprehensive file registry system that provides cross-platform file management
capabilities including registration, metadata tracking, search, and retrieval.
"""

import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import mimetypes
import logging

# Optional imports
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


logger = logging.getLogger(__name__)

class FileType(Enum):
    """File type enumeration"""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"
    OTHER = "other"


@dataclass
class FileMetadata:
    """File metadata structure"""
    id: str
    name: str
    original_name: str
    path: str
    absolute_path: str
    size: int
    file_type: str
    mime_type: str
    extension: str
    upload_timestamp: str
    modification_timestamp: str
    checksum: str
    parent_directory: str
    is_hidden: bool
    permissions: str
    tags: List[str]
    custom_metadata: Dict[str, Any]
    storage_provider: str = "local"
    storage_path: Optional[str] = None
    retrieval_count: int = 0
    last_accessed: Optional[str] = None


logger = logging.getLogger(__name__)

class CrossPlatformPath:
    """Cross-platform path handling utility"""
    
    @staticmethod
    def normalize_path(path: Union[str, Path]) -> str:
        """Normalize path for cross-platform compatibility"""
        if isinstance(path, Path):
            path = str(path)
        
        # Handle Windows vs Unix path separators
        path = os.path.normpath(path)
        
        # Convert to forward slashes for consistency
        if platform.system() == "Windows":
            path = path.replace("\\", "/")
        
        return path
    
    @staticmethod
    def get_absolute_path(path: Union[str, Path]) -> str:
        """Get absolute path across platforms"""
        return os.path.abspath(path)
    
    @staticmethod
    def split_path(path: Union[str, Path]) -> Tuple[str, str]:
        """Split path into directory and filename"""
        path = CrossPlatformPath.normalize_path(path)
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        return directory, filename
    
    @staticmethod
    def join_path(*parts) -> str:
        """Join path parts cross-platform"""
        return CrossPlatformPath.normalize_path(os.path.join(*parts))


logger = logging.getLogger(__name__)

class FileRegistry:
    """
    Cross-Platform File Registry
    
    A comprehensive file management system with:
    - File registration and tracking with unique IDs
    - Metadata storage and retrieval
    - Cross-platform compatibility
    - Search and filtering capabilities
    - Integration hooks for storage providers
    - Efficient indexing and retrieval
    """
    
    def __init__(self, registry_path: Union[str, Path] = "file_registry.db"):
        """
        Initialize the file registry
        
        Args:
            registry_path: Path to the registry database
        """
        self.registry_path = CrossPlatformPath.normalize_path(registry_path)
        self._lock = threading.RLock()
        self._storage_hooks = {}
        self._file_index = {}
        
        # Initialize database
        self._init_database()
        
        # Load existing files into memory index
        self._rebuild_index()
    
    def _init_database(self):
        """Initialize the SQLite database"""
        with sqlite3.connect(self.registry_path) as conn:
            cursor = conn.cursor()
            
            # Create files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    absolute_path TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    file_type TEXT NOT NULL,
                    mime_type TEXT,
                    extension TEXT,
                    upload_timestamp TEXT NOT NULL,
                    modification_timestamp TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    parent_directory TEXT,
                    is_hidden BOOLEAN DEFAULT FALSE,
                    permissions TEXT,
                    tags TEXT DEFAULT '[]',
                    custom_metadata TEXT DEFAULT '{}',
                    storage_provider TEXT DEFAULT 'local',
                    storage_path TEXT,
                    retrieval_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)
            
            # Create indexes for efficient searching
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_name 
                ON files(name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_type 
                ON files(file_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_extension 
                ON files(extension)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_upload_time 
                ON files(upload_timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_parent_dir 
                ON files(parent_directory)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_tags 
                ON files(tags)
            """)
            
            conn.commit()
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def _detect_file_type(self, file_path: str, mime_type: str = None) -> str:
        """Detect file type based on extension and MIME type"""
        extension = Path(file_path).suffix.lower()
        mime_type = mime_type or mimetypes.guess_type(file_path)[0] or ""
        
        # Define file type mappings
        type_mappings = {
            FileType.DOCUMENT: ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.tex'],
            FileType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff'],
            FileType.VIDEO: ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            FileType.AUDIO: ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            FileType.ARCHIVE: ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
            FileType.CODE: ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb'],
            FileType.DATA: ['.json', '.xml', '.csv', '.xlsx', '.xls', '.sql', '.db']
        }
        
        # Check file extensions
        for file_type, extensions in type_mappings.items():
            if extension in extensions:
                return file_type.value
        
        # Check MIME types
        if mime_type.startswith('image/'):
            return FileType.IMAGE.value
        elif mime_type.startswith('video/'):
            return FileType.VIDEO.value
        elif mime_type.startswith('audio/'):
            return FileType.AUDIO.value
        elif mime_type.startswith('text/') or mime_type.startswith('application/'):
            if mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                return FileType.DOCUMENT.value
            elif mime_type in ['application/json', 'application/xml']:
                return FileType.DATA.value
        
        return FileType.OTHER.value
    
    def _get_file_permissions(self, file_path: str) -> str:
        """Get file permissions as string"""
        try:
            return oct(os.stat(file_path).st_mode)[-3:]
        except Exception:
            return "000"
    
    def register_file(self, file_path: Union[str, Path], 
                     tags: List[str] = None, 
                     custom_metadata: Dict[str, Any] = None,
                     storage_provider: str = "local") -> str:
        """
        Register a file in the registry
        
        Args:
            file_path: Path to the file to register
            tags: Optional list of tags
            custom_metadata: Optional custom metadata dictionary
            storage_provider: Storage provider identifier
            
        Returns:
            Unique file ID
        """
        with self._lock:
            # Normalize and validate path
            normalized_path = CrossPlatformPath.normalize_path(file_path)
            absolute_path = CrossPlatformPath.get_absolute_path(normalized_path)
            
            if not os.path.exists(absolute_path):
                raise FileNotFoundError(f"File not found: {absolute_path}")
            
            # Check if file is already registered
            existing_id = self._find_file_by_path(absolute_path)
            if existing_id:
                return existing_id
            
            # Generate unique ID
            file_id = str(uuid.uuid4())
            
            # Get file information
            file_stat = os.stat(absolute_path)
            file_name = os.path.basename(absolute_path)
            directory, _ = CrossPlatformPath.split_path(absolute_path)
            extension = Path(absolute_path).suffix.lower()
            mime_type = mimetypes.guess_type(absolute_path)[0]
            
            # Detect file type
            file_type = self._detect_file_type(absolute_path, mime_type)
            
            # Calculate checksum
            checksum = self._calculate_checksum(absolute_path)
            
            # Get permissions
            permissions = self._get_file_permissions(absolute_path)
            
            # Create metadata
            metadata = FileMetadata(
                id=file_id,
                name=file_name,
                original_name=file_name,
                path=normalized_path,
                absolute_path=absolute_path,
                size=file_stat.st_size,
                file_type=file_type,
                mime_type=mime_type or "",
                extension=extension,
                upload_timestamp=datetime.now().isoformat(),
                modification_timestamp=datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                checksum=checksum,
                parent_directory=directory,
                is_hidden=file_name.startswith('.'),
                permissions=permissions,
                tags=tags or [],
                custom_metadata=custom_metadata or {},
                storage_provider=storage_provider,
                storage_path=absolute_path
            )
            
            # Store in database
            self._save_metadata(metadata)
            
            # Update memory index
            self._file_index[file_id] = metadata
            
            return file_id
    
    def _save_metadata(self, metadata: FileMetadata):
        """Save metadata to database"""
        with sqlite3.connect(self.registry_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO files (
                    id, name, original_name, path, absolute_path, size, file_type,
                    mime_type, extension, upload_timestamp, modification_timestamp,
                    checksum, parent_directory, is_hidden, permissions, tags,
                    custom_metadata, storage_provider, storage_path, retrieval_count,
                    last_accessed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.id, metadata.name, metadata.original_name, metadata.path,
                metadata.absolute_path, metadata.size, metadata.file_type,
                metadata.mime_type, metadata.extension, metadata.upload_timestamp,
                metadata.modification_timestamp, metadata.checksum, metadata.parent_directory,
                metadata.is_hidden, metadata.permissions, json.dumps(metadata.tags),
                json.dumps(metadata.custom_metadata), metadata.storage_provider,
                metadata.storage_path, metadata.retrieval_count, metadata.last_accessed
            ))
            
            conn.commit()
    
    def _find_file_by_path(self, absolute_path: str) -> Optional[str]:
        """Find file ID by absolute path"""
        with sqlite3.connect(self.registry_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM files WHERE absolute_path = ?", (absolute_path,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_file(self, file_id: str) -> Optional[FileMetadata]:
        """
        Retrieve file metadata by ID
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            FileMetadata object or None if not found
        """
        with self._lock:
            # Check memory index first
            if file_id in self._file_index:
                metadata = self._file_index[file_id]
                # Update access tracking
                metadata.retrieval_count += 1
                metadata.last_accessed = datetime.now().isoformat()
                self._save_metadata(metadata)
                return metadata
            
            # Load from database
            return self._load_metadata(file_id)
    
    def _load_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Load metadata from database"""
        with sqlite3.connect(self.registry_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, original_name, path, absolute_path, size, file_type,
                       mime_type, extension, upload_timestamp, modification_timestamp,
                       checksum, parent_directory, is_hidden, permissions, tags,
                       custom_metadata, storage_provider, storage_path, retrieval_count,
                       last_accessed
                FROM files WHERE id = ?
            """, (file_id,))
            
            result = cursor.fetchone()
            if result:
                metadata = FileMetadata(
                    id=result[0], name=result[1], original_name=result[2],
                    path=result[3], absolute_path=result[4], size=result[5],
                    file_type=result[6], mime_type=result[7], extension=result[8],
                    upload_timestamp=result[9], modification_timestamp=result[10],
                    checksum=result[11], parent_directory=result[12], is_hidden=result[13],
                    permissions=result[14], tags=json.loads(result[15] or '[]'),
                    custom_metadata=json.loads(result[16] or '{}'),
                    storage_provider=result[17], storage_path=result[18],
                    retrieval_count=result[19], last_accessed=result[20]
                )
                
                # Update memory index
                self._file_index[file_id] = metadata
                return metadata
            
            return None
    
    def search_files(self, query: str = "", 
                    file_type: str = None,
                    extension: str = None,
                    tags: List[str] = None,
                    directory: str = None,
                    min_size: int = None,
                    max_size: int = None,
                    date_from: str = None,
                    date_to: str = None) -> List[FileMetadata]:
        """
        Search files with various filters
        
        Args:
            query: Text search in filename
            file_type: Filter by file type
            extension: Filter by file extension
            tags: Filter by tags (files must have all tags)
            directory: Filter by parent directory
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes
            date_from: Search from date (ISO format)
            date_to: Search to date (ISO format)
            
        Returns:
            List of matching FileMetadata objects
        """
        with self._lock:
            # Build SQL query dynamically
            sql = """
                SELECT id, name, original_name, path, absolute_path, size, file_type,
                       mime_type, extension, upload_timestamp, modification_timestamp,
                       checksum, parent_directory, is_hidden, permissions, tags,
                       custom_metadata, storage_provider, storage_path, retrieval_count,
                       last_accessed
                FROM files WHERE 1=1
            """
            params = []
            
            # Add filters
            if query:
                sql += " AND (name LIKE ? OR original_name LIKE ?)"
                search_term = f"%{query}%"
                params.extend([search_term, search_term])
            
            if file_type:
                sql += " AND file_type = ?"
                params.append(file_type)
            
            if extension:
                sql += " AND extension = ?"
                params.append(extension)
            
            if tags:
                for tag in tags:
                    sql += " AND tags LIKE ?"
                    params.append(f'%"{tag}"%')
            
            if directory:
                sql += " AND parent_directory = ?"
                params.append(directory)
            
            if min_size is not None:
                sql += " AND size >= ?"
                params.append(min_size)
            
            if max_size is not None:
                sql += " AND size <= ?"
                params.append(max_size)
            
            if date_from:
                sql += " AND upload_timestamp >= ?"
                params.append(date_from)
            
            if date_to:
                sql += " AND upload_timestamp <= ?"
                params.append(date_to)
            
            sql += " ORDER BY upload_timestamp DESC"
            
            # Execute search
            with sqlite3.connect(self.registry_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                
                results = []
                for row in cursor.fetchall():
                    metadata = FileMetadata(
                        id=row[0], name=row[1], original_name=row[2],
                        path=row[3], absolute_path=row[4], size=row[5],
                        file_type=row[6], mime_type=row[7], extension=row[8],
                        upload_timestamp=row[9], modification_timestamp=row[10],
                        checksum=row[11], parent_directory=row[12], is_hidden=row[13],
                        permissions=row[14], tags=json.loads(row[15] or '[]'),
                        custom_metadata=json.loads(row[16] or '{}'),
                        storage_provider=row[17], storage_path=row[18],
                        retrieval_count=row[19], last_accessed=row[20]
                    )
                    results.append(metadata)
                
                return results
    
    def discover_files(self, directory: Union[str, Path], 
                      recursive: bool = True,
                      include_hidden: bool = False) -> List[str]:
        """
        Discover and register files in a directory
        
        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            include_hidden: Whether to include hidden files
            
        Returns:
            List of registered file IDs
        """
        directory = CrossPlatformPath.get_absolute_path(directory)
        
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise ValueError(f"Directory not found: {directory}")
        
        registered_ids = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories if not including hidden
                if not include_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file_name in files:
                    if not include_hidden and file_name.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, file_name)
                    try:
                        file_id = self.register_file(file_path)
                        registered_ids.append(file_id)
                    except Exception as e:
                        logger.info(f"Warning: Could not register {file_path}: {e}")
        else:
            # Non-recursive search
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    if include_hidden or not item.startswith('.'):
                        try:
                            file_id = self.register_file(item_path)
                            registered_ids.append(file_id)
                        except Exception as e:
                            logger.info(f"Warning: Could not register {item_path}: {e}")
        
        return registered_ids
    
    def update_file(self, file_id: str, 
                   tags: List[str] = None,
                   custom_metadata: Dict[str, Any] = None) -> bool:
        """
        Update file metadata
        
        Args:
            file_id: File ID to update
            tags: New tags (replaces existing)
            custom_metadata: New custom metadata (merges with existing)
            
        Returns:
            True if update successful
        """
        with self._lock:
            metadata = self.get_file(file_id)
            if not metadata:
                return False
            
            # Update fields
            if tags is not None:
                metadata.tags = tags
            
            if custom_metadata is not None:
                metadata.custom_metadata.update(custom_metadata)
            
            # Save changes
            self._save_metadata(metadata)
            return True
    
    def remove_file(self, file_id: str) -> bool:
        """
        Remove file from registry
        
        Args:
            file_id: File ID to remove
            
        Returns:
            True if removal successful
        """
        with self._lock:
            # Remove from database
            with sqlite3.connect(self.registry_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
                conn.commit()
            
            # Remove from memory index
            if file_id in self._file_index:
                del self._file_index[file_id]
            
            return True
    
    def get_file_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        with self._lock:
            with sqlite3.connect(self.registry_path) as conn:
                cursor = conn.cursor()
                
                # Total files
                cursor.execute("SELECT COUNT(*) FROM files")
                total_files = cursor.fetchone()[0]
                
                # Files by type
                cursor.execute("""
                    SELECT file_type, COUNT(*) 
                    FROM files 
                    GROUP BY file_type
                """)
                files_by_type = dict(cursor.fetchall())
                
                # Total size
                cursor.execute("SELECT SUM(size) FROM files")
                total_size = cursor.fetchone()[0] or 0
                
                # Recent files (last 30 days)
                thirty_days_ago = (datetime.now().timestamp() - 30 * 24 * 3600)
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM files 
                    WHERE upload_timestamp > ?
                """, (datetime.fromtimestamp(thirty_days_ago).isoformat(),))
                recent_files = cursor.fetchone()[0]
                
                return {
                    "total_files": total_files,
                    "files_by_type": files_by_type,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "recent_files_30_days": recent_files,
                    "registry_path": self.registry_path
                }
    
    def _rebuild_index(self):
        """Rebuild memory index from database"""
        with sqlite3.connect(self.registry_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM files")
            
            for row in cursor.fetchall():
                file_id = row[0]
                metadata = self._load_metadata(file_id)
                if metadata:
                    self._file_index[file_id] = metadata
    
    def register_storage_provider(self, name: str, provider_class):
        """
        Register a storage provider
        
        Args:
            name: Provider name identifier
            provider_class: Provider class with required methods
        """
        self._storage_hooks[name] = provider_class
    
    def upload_to_storage(self, file_id: str, provider: str, **kwargs) -> str:
        """
        Upload file to storage provider
        
        Args:
            file_id: File ID to upload
            provider: Storage provider name
            **kwargs: Additional provider-specific arguments
            
        Returns:
            Storage URL or identifier
        """
        metadata = self.get_file(file_id)
        if not metadata:
            raise ValueError(f"File not found: {file_id}")
        
        if provider not in self._storage_hooks:
            raise ValueError(f"Storage provider not registered: {provider}")
        
        provider_class = self._storage_hooks[provider]
        provider_instance = provider_class(**kwargs)
        
        # Upload file and get storage path
        storage_path = provider_instance.upload(metadata.absolute_path, metadata.name)
        
        # Update metadata with storage information
        self.update_file_metadata(file_id, {
            "storage_provider": provider,
            "storage_path": storage_path
        })
        
        return storage_path
    
    def update_file_metadata(self, file_id: str, updates: Dict[str, Any]):
        """Update specific metadata fields"""
        with self._lock:
            metadata = self.get_file(file_id)
            if not metadata:
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            
            self._save_metadata(metadata)
            return True
    
    def export_registry(self, output_path: Union[str, Path], 
                       format: str = "json") -> bool:
        """
        Export registry data
        
        Args:
            output_path: Output file path
            format: Export format ("json" or "csv")
            
        Returns:
            True if export successful
        """
        output_path = CrossPlatformPath.normalize_path(output_path)
        
        if format.lower() == "json":
            return self._export_json(output_path)
        elif format.lower() == "csv":
            return self._export_csv(output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, output_path: str) -> bool:
        """Export to JSON format"""
        with self._lock:
            files = self.search_files()  # Get all files
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "registry_path": self.registry_path,
                "total_files": len(files),
                "files": [asdict(metadata) for metadata in files]
            }
            
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                return True
            except Exception:
                return False
    
    def _export_csv(self, output_path: str) -> bool:
        """Export to CSV format"""
        import csv
        
        with self._lock:
            files = self.search_files()  # Get all files
            
            try:
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    if not files:
                        return True
                    
                    # Get all field names from first metadata
                    fieldnames = asdict(files[0]).keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for metadata in files:
                        # Convert lists and dicts to strings for CSV
                        row = asdict(metadata)
                        for key, value in row.items():
                            if isinstance(value, (list, dict)):
                                row[key] = json.dumps(value)
                        writer.writerow(row)
                return True
            except Exception:
                return False
    
    def import_registry(self, input_path: Union[str, Path], 
                      merge: bool = True) -> bool:
        """
        Import registry data
        
        Args:
            input_path: Input file path
            merge: Whether to merge with existing data
            
        Returns:
            True if import successful
        """
        input_path = CrossPlatformPath.normalize_path(input_path)
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "files" not in import_data:
                return False
            
            if not merge:
                # Clear existing data
                with sqlite3.connect(self.registry_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM files")
                    conn.commit()
                self._file_index.clear()
            
            # Import files
            imported_count = 0
            for file_data in import_data["files"]:
                try:
                    # Reconstruct FileMetadata
                    metadata = FileMetadata(**file_data)
                    
                    # Check if file already exists
                    if self._find_file_by_path(metadata.absolute_path) and merge:
                        continue
                    
                    self._save_metadata(metadata)
                    self._file_index[metadata.id] = metadata
                    imported_count += 1
                except Exception as e:
                    logger.info(f"Warning: Could not import file {file_data.get('name', 'unknown')}: {e}")
            
            return imported_count > 0
        except Exception:
            return False
    
    def cleanup_registry(self) -> Dict[str, Any]:
        """
        Clean up registry by removing entries for non-existent files
        
        Returns:
            Cleanup statistics
        """
        with self._lock:
            files = self.search_files()
            removed_count = 0
            missing_files = []
            
            for metadata in files:
                if not os.path.exists(metadata.absolute_path):
                    self.remove_file(metadata.id)
                    removed_count += 1
                    missing_files.append(metadata.name)
            
            return {
                "removed_entries": removed_count,
                "missing_files": missing_files,
                "remaining_files": len(self.search_files())
            }
    
    def __str__(self) -> str:
        """String representation"""
        stats = self.get_file_stats()
        return f"FileRegistry({stats['total_files']} files, {stats['total_size_mb']} MB)"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"FileRegistry(path='{self.registry_path}')"