"""
File Lifecycle Synchronization Module

Provides automated file lifecycle management with state tracking, policy enforcement,
and synchronization between local registry and cloud storage.
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
import threading
import schedule
import hashlib
import shutil
import aiofiles
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LifecycleState(Enum):
    """File lifecycle states"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ARCHIVED = "archived"
    DELETED = "deleted"
    BACKUP_PENDING = "backup_pending"
    BACKUP_COMPLETE = "backup_complete"
    EXPIRED = "expired"


class FileType(Enum):
    """File types for lifecycle management"""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    OTHER = "other"


@dataclass
class LifecyclePolicy:
    """Lifecycle policy configuration"""
    name: str
    file_types: List[FileType]
    retention_days: int
    archive_after_days: int
    delete_after_days: int
    backup_frequency_hours: int
    auto_archive: bool
    auto_delete: bool
    versioning_enabled: bool
    max_versions: int


@dataclass
class FileMetadata:
    """File metadata for lifecycle tracking"""
    file_id: str
    file_path: str
    file_name: str
    file_type: FileType
    file_size: int
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    state: LifecycleState
    policy_name: str
    checksum: str
    version: int
    parent_id: Optional[str] = None
    backup_path: Optional[str] = None
    archive_path: Optional[str] = None
    expiry_date: Optional[datetime] = None
    last_state_change: datetime = None


@dataclass
class SyncOperation:
    """Synchronization operation record"""
    operation_id: str
    file_id: str
    operation_type: str
    timestamp: datetime
    status: str
    details: str


class LifecycleSync:
    """File Lifecycle Synchronization Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the lifecycle sync manager
        
        Args:
            config: Configuration dictionary containing paths and settings
        """
        self.config = config
        self.db_path = config.get('database_path', 'file_registry.db')
        self.local_storage_path = Path(config.get('local_storage_path', './storage'))
        self.archive_path = Path(config.get('archive_path', './archive'))
        self.backup_path = Path(config.get('backup_path', './backup'))
        self.registry_sync_interval = config.get('registry_sync_interval', 300)  # 5 minutes
        self.cleanup_interval = config.get('cleanup_interval', 3600)  # 1 hour
        
        # API endpoints for Moonshot storage integration
        self.moonshot_api_base = config.get('moonshot_api_base', 'https://api.moonshot.cn')
        self.moonshot_api_key = config.get('moonshot_api_key')
        
        # Initialize directories
        self._init_directories()
        
        # Initialize database
        self._init_database()
        
        # Load policies
        self.policies = self._load_policies()
        
        # Threading
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._running = False
        
        logger.info("LifecycleSync initialized successfully")
    
    def _init_directories(self):
        """Initialize required directories"""
        directories = [
            self.local_storage_path,
            self.archive_path,
            self.backup_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory initialized: {directory}")
    
    def _init_database(self):
        """Initialize SQLite database for registry"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS file_registry (
                    file_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    modified_at TIMESTAMP NOT NULL,
                    accessed_at TIMESTAMP NOT NULL,
                    state TEXT NOT NULL,
                    policy_name TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    parent_id TEXT,
                    backup_path TEXT,
                    archive_path TEXT,
                    expiry_date TIMESTAMP,
                    last_state_change TIMESTAMP NOT NULL,
                    FOREIGN KEY (parent_id) REFERENCES file_registry (file_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_operations (
                    operation_id TEXT PRIMARY KEY,
                    file_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (file_id) REFERENCES file_registry (file_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS lifecycle_policies (
                    name TEXT PRIMARY KEY,
                    file_types TEXT NOT NULL,
                    retention_days INTEGER NOT NULL,
                    archive_after_days INTEGER NOT NULL,
                    delete_after_days INTEGER NOT NULL,
                    backup_frequency_hours INTEGER NOT NULL,
                    auto_archive BOOLEAN NOT NULL,
                    auto_delete BOOLEAN NOT NULL,
                    versioning_enabled BOOLEAN NOT NULL,
                    max_versions INTEGER NOT NULL
                )
            ''')
            
            conn.commit()
            logger.debug("Database initialized successfully")
    
    def _load_policies(self) -> Dict[str, LifecyclePolicy]:
        """Load lifecycle policies from database"""
        policies = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM lifecycle_policies')
            rows = cursor.fetchall()
            
            for row in rows:
                policy = LifecyclePolicy(
                    name=row[0],
                    file_types=[FileType(ft) for ft in json.loads(row[1])],
                    retention_days=row[2],
                    archive_after_days=row[3],
                    delete_after_days=row[4],
                    backup_frequency_hours=row[5],
                    auto_archive=bool(row[6]),
                    auto_delete=bool(row[7]),
                    versioning_enabled=bool(row[8]),
                    max_versions=row[9]
                )
                policies[policy.name] = policy
        
        # Load default policies if none exist
        if not policies:
            default_policies = self._get_default_policies()
            for policy in default_policies:
                self.create_policy(policy)
                policies[policy.name] = policy
        
        return policies
    
    def _get_default_policies(self) -> List[LifecyclePolicy]:
        """Get default lifecycle policies"""
        return [
            LifecyclePolicy(
                name="documents",
                file_types=[FileType.DOCUMENT],
                retention_days=365,
                archive_after_days=90,
                delete_after_days=365,
                backup_frequency_hours=24,
                auto_archive=True,
                auto_delete=True,
                versioning_enabled=True,
                max_versions=5
            ),
            LifecyclePolicy(
                name="media",
                file_types=[FileType.IMAGE, FileType.VIDEO, FileType.AUDIO],
                retention_days=730,
                archive_after_days=180,
                delete_after_days=730,
                backup_frequency_hours=12,
                auto_archive=True,
                auto_delete=False,
                versioning_enabled=True,
                max_versions=3
            ),
            LifecyclePolicy(
                name="archives",
                file_types=[FileType.ARCHIVE],
                retention_days=1825,  # 5 years
                archive_after_days=30,
                delete_after_days=1825,
                backup_frequency_hours=168,  # Weekly
                auto_archive=False,
                auto_delete=False,
                versioning_enabled=True,
                max_versions=2
            )
        ]
    
    async def start_sync(self):
        """Start the lifecycle synchronization service"""
        if self._running:
            logger.warning("Lifecycle sync is already running")
            return
        
        self._running = True
        logger.info("Starting lifecycle synchronization service")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._registry_sync_loop()),
            asyncio.create_task(self._cleanup_loop()),
            asyncio.create_task(self._backup_loop()),
            asyncio.create_task(self._policy_enforcement_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Lifecycle sync service stopped")
        finally:
            self._running = False
    
    async def stop_sync(self):
        """Stop the lifecycle synchronization service"""
        self._running = False
        self._executor.shutdown(wait=True)
        logger.info("Lifecycle synchronization service stopped")
    
    async def _registry_sync_loop(self):
        """Main registry synchronization loop"""
        while self._running:
            try:
                await self._sync_registry_state()
                await asyncio.sleep(self.registry_sync_interval)
            except Exception as e:
                logger.error(f"Error in registry sync loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _cleanup_loop(self):
        """Cleanup loop for orphaned and expired files"""
        while self._running:
            try:
                await self._cleanup_orphaned_files()
                await self._cleanup_expired_files()
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _backup_loop(self):
        """Backup loop for files requiring backup"""
        while self._running:
            try:
                await self._process_backup_queue()
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"Error in backup loop: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retry
    
    async def _policy_enforcement_loop(self):
        """Policy enforcement loop"""
        while self._running:
            try:
                await self._enforce_policies()
                await asyncio.sleep(1800)  # Check every 30 minutes
            except Exception as e:
                logger.error(f"Error in policy enforcement loop: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retry
    
    async def _sync_registry_state(self):
        """Synchronize registry state with actual file system"""
        logger.debug("Starting registry state synchronization")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM file_registry WHERE state != ?', (LifecycleState.DELETED.value,))
            files = cursor.fetchall()
            
            for file_data in files:
                file_metadata = self._row_to_metadata(file_data)
                try:
                    # Check if file still exists
                    if not Path(file_metadata.file_path).exists():
                        # Mark as deleted if file is missing
                        await self._update_file_state(file_metadata.file_id, LifecycleState.DELETED)
                        continue
                    
                    # Update file metadata
                    updated_metadata = await self._update_file_metadata(file_metadata)
                    await self._save_file_metadata(updated_metadata)
                    
                    # Sync with cloud storage if applicable
                    if self.moonshot_api_key:
                        await self._sync_with_cloud_storage(updated_metadata)
                    
                except Exception as e:
                    logger.error(f"Error syncing file {file_metadata.file_id}: {e}")
        
        logger.debug("Registry state synchronization completed")
    
    async def _update_file_metadata(self, metadata: FileMetadata) -> FileMetadata:
        """Update file metadata from actual file"""
        file_path = Path(metadata.file_path)
        
        if not file_path.exists():
            return metadata
        
        stat = file_path.stat()
        
        # Update timestamps and size
        metadata.file_size = stat.st_size
        metadata.modified_at = datetime.fromtimestamp(stat.st_mtime)
        metadata.accessed_at = datetime.fromtimestamp(stat.st_atime)
        
        # Update checksum if needed
        metadata.checksum = await self._calculate_file_checksum(file_path)
        
        return metadata
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _sync_with_cloud_storage(self, metadata: FileMetadata):
        """Synchronize file metadata with Moonshot cloud storage"""
        if not self.moonshot_api_key:
            return
        
        try:
            headers = {
                'Authorization': f'Bearer {self.moonshot_api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                # Get cloud metadata
                cloud_url = f"{self.moonshot_api_base}/storage/files/{metadata.file_id}"
                async with session.get(cloud_url, headers=headers) as response:
                    if response.status == 200:
                        cloud_data = await response.json()
                        # Compare and sync state if needed
                        if metadata.state != cloud_data.get('state'):
                            await self._sync_state_with_cloud(metadata.file_id, metadata.state)
        except Exception as e:
            logger.error(f"Error syncing with cloud storage for {metadata.file_id}: {e}")
    
    async def _sync_state_with_cloud(self, file_id: str, state: LifecycleState):
        """Synchronize state with cloud storage"""
        if not self.moonshot_api_key:
            return
        
        try:
            headers = {
                'Authorization': f'Bearer {self.moonshot_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {'state': state.value}
            
            async with aiohttp.ClientSession() as session:
                cloud_url = f"{self.moonshot_api_base}/storage/files/{file_id}/state"
                async with session.patch(cloud_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        logger.debug(f"State synced with cloud for file {file_id}")
                    else:
                        logger.warning(f"Failed to sync state with cloud for file {file_id}")
        except Exception as e:
            logger.error(f"Error syncing state with cloud for {file_id}: {e}")
    
    async def _cleanup_orphaned_files(self):
        """Clean up orphaned files in the storage"""
        logger.debug("Starting cleanup of orphaned files")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT file_path FROM file_registry WHERE state != ?', (LifecycleState.DELETED.value,))
            registered_files = {row[0] for row in cursor.fetchall()}
        
        # Check all files in storage directory
        for file_path in self.local_storage_path.rglob('*'):
            if file_path.is_file() and str(file_path) not in registered_files:
                # Check if file is older than 24 hours (avoid deleting recently uploaded files)
                if time.time() - file_path.stat().st_mtime > 86400:
                    try:
                        await self._register_orphaned_file(file_path)
                        logger.info(f"Registered orphaned file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error registering orphaned file {file_path}: {e}")
        
        logger.debug("Orphaned files cleanup completed")
    
    async def _register_orphaned_file(self, file_path: Path):
        """Register an orphaned file in the registry"""
        file_id = hashlib.sha256(f"{file_path}_{file_path.stat().st_mtime}".encode()).hexdigest()[:16]
        
        metadata = FileMetadata(
            file_id=file_id,
            file_path=str(file_path),
            file_name=file_path.name,
            file_type=self._detect_file_type(file_path.suffix),
            file_size=file_path.stat().st_size,
            created_at=datetime.fromtimestamp(file_path.stat().st_ctime),
            modified_at=datetime.fromtimestamp(file_path.stat().st_mtime),
            accessed_at=datetime.fromtimestamp(file_path.stat().st_atime),
            state=LifecycleState.UPLOADED,
            policy_name="default",
            checksum=await self._calculate_file_checksum(file_path),
            version=1
        )
        
        await self._save_file_metadata(metadata)
    
    def _detect_file_type(self, extension: str) -> FileType:
        """Detect file type from extension"""
        extension = extension.lower()
        
        type_mapping = {
            '.txt': FileType.DOCUMENT,
            '.pdf': FileType.DOCUMENT,
            '.doc': FileType.DOCUMENT,
            '.docx': FileType.DOCUMENT,
            '.jpg': FileType.IMAGE,
            '.jpeg': FileType.IMAGE,
            '.png': FileType.IMAGE,
            '.gif': FileType.IMAGE,
            '.mp4': FileType.VIDEO,
            '.avi': FileType.VIDEO,
            '.mov': FileType.VIDEO,
            '.mp3': FileType.AUDIO,
            '.wav': FileType.AUDIO,
            '.zip': FileType.ARCHIVE,
            '.rar': FileType.ARCHIVE,
            '.7z': FileType.ARCHIVE
        }
        
        return type_mapping.get(extension, FileType.OTHER)
    
    async def _cleanup_expired_files(self):
        """Clean up files that have exceeded their retention period"""
        logger.debug("Starting cleanup of expired files")
        
        current_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM file_registry 
                WHERE expiry_date IS NOT NULL 
                AND expiry_date < ? 
                AND state != ?
            ''', (current_time, LifecycleState.DELETED.value))
            
            expired_files = cursor.fetchall()
        
        for file_data in expired_files:
            metadata = self._row_to_metadata(file_data)
            try:
                policy = self.policies.get(metadata.policy_name)
                if policy and policy.auto_delete:
                    await self._delete_file(metadata)
                else:
                    await self._update_file_state(metadata.file_id, LifecycleState.EXPIRED)
            except Exception as e:
                logger.error(f"Error processing expired file {metadata.file_id}: {e}")
        
        logger.debug("Expired files cleanup completed")
    
    async def _process_backup_queue(self):
        """Process files in the backup queue"""
        logger.debug("Processing backup queue")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM file_registry 
                WHERE state = ? OR state = ?
            ''', (LifecycleState.BACKUP_PENDING.value, LifecycleState.BACKUP_COMPLETE.value))
            
            backup_files = cursor.fetchall()
        
        for file_data in backup_files:
            metadata = self._row_to_metadata(file_data)
            try:
                policy = self.policies.get(metadata.policy_name)
                if policy and policy.versioning_enabled:
                    await self._create_backup(metadata, policy)
            except Exception as e:
                logger.error(f"Error creating backup for {metadata.file_id}: {e}")
        
        logger.debug("Backup queue processing completed")
    
    async def _create_backup(self, metadata: FileMetadata, policy: LifecyclePolicy):
        """Create backup of file"""
        source_path = Path(metadata.file_path)
        
        if not source_path.exists():
            logger.warning(f"Source file not found for backup: {metadata.file_id}")
            return
        
        # Create backup directory structure
        backup_dir = self.backup_path / metadata.file_type.value / str(datetime.now().year)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup filename with version
        backup_filename = f"{metadata.file_id}_v{metadata.version}{source_path.suffix}"
        backup_file_path = backup_dir / backup_filename
        
        try:
            # Copy file to backup location
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                shutil.copy2,
                source_path,
                backup_file_path
            )
            
            # Update metadata
            metadata.backup_path = str(backup_file_path)
            metadata.version += 1
            await self._update_file_state(metadata.file_id, LifecycleState.BACKUP_COMPLETE)
            
            # Clean up old versions if needed
            if policy.max_versions and metadata.version > policy.max_versions:
                await self._cleanup_old_versions(metadata, policy)
            
            logger.info(f"Backup created for {metadata.file_id}")
        except Exception as e:
            logger.error(f"Error creating backup for {metadata.file_id}: {e}")
            await self._update_file_state(metadata.file_id, LifecycleState.BACKUP_PENDING)
    
    async def _cleanup_old_versions(self, metadata: FileMetadata, policy: LifecyclePolicy):
        """Clean up old versions of files"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM file_registry 
                WHERE parent_id = ? 
                ORDER BY version DESC
            ''', (metadata.file_id,))
            
            versions = cursor.fetchall()
        
        # Keep only the latest versions
        versions_to_delete = versions[policy.max_versions:]
        
        for version_data in versions_to_delete:
            version_metadata = self._row_to_metadata(version_data)
            await self._delete_backup_file(version_metadata)
    
    async def _delete_backup_file(self, metadata: FileMetadata):
        """Delete a backup file"""
        if metadata.backup_path and Path(metadata.backup_path).exists():
            try:
                Path(metadata.backup_path).unlink()
                await self._update_file_state(metadata.file_id, LifecycleState.DELETED)
                logger.debug(f"Backup file deleted: {metadata.backup_path}")
            except Exception as e:
                logger.error(f"Error deleting backup file {metadata.backup_path}: {e}")
    
    async def _enforce_policies(self):
        """Enforce lifecycle policies on files"""
        logger.debug("Enforcing lifecycle policies")
        
        current_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM file_registry WHERE state != ?', (LifecycleState.DELETED.value,))
            files = cursor.fetchall()
        
        for file_data in files:
            metadata = self._row_to_metadata(file_data)
            policy = self.policies.get(metadata.policy_name)
            
            if not policy:
                continue
            
            try:
                # Check if file should be archived
                if policy.auto_archive and current_time - metadata.created_at > timedelta(days=policy.archive_after_days):
                    if metadata.state == LifecycleState.UPLOADED:
                        await self._archive_file(metadata, policy)
                
                # Check if file should be deleted
                if policy.auto_delete and current_time - metadata.created_at > timedelta(days=policy.delete_after_days):
                    await self._delete_file(metadata)
                
                # Update expiry date
                if not metadata.expiry_date:
                    expiry_date = metadata.created_at + timedelta(days=policy.retention_days)
                    metadata.expiry_date = expiry_date
                    await self._save_file_metadata(metadata)
                    
            except Exception as e:
                logger.error(f"Error enforcing policy for {metadata.file_id}: {e}")
        
        logger.debug("Lifecycle policies enforcement completed")
    
    async def _archive_file(self, metadata: FileMetadata, policy: LifecyclePolicy):
        """Archive a file"""
        source_path = Path(metadata.file_path)
        
        if not source_path.exists():
            logger.warning(f"Source file not found for archiving: {metadata.file_id}")
            return
        
        # Create archive directory structure
        archive_dir = self.archive_path / metadata.file_type.value / str(datetime.now().year)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create archived filename
        archive_filename = f"{metadata.file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{source_path.suffix}"
        archive_file_path = archive_dir / archive_filename
        
        try:
            # Move file to archive location
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                shutil.move,
                source_path,
                archive_file_path
            )
            
            # Update metadata
            metadata.file_path = str(archive_file_path)
            metadata.archive_path = str(archive_file_path)
            await self._update_file_state(metadata.file_id, LifecycleState.ARCHIVED)
            
            logger.info(f"File archived: {metadata.file_id}")
        except Exception as e:
            logger.error(f"Error archiving file {metadata.file_id}: {e}")
    
    async def _delete_file(self, metadata: FileMetadata):
        """Delete a file and its backup versions"""
        file_path = Path(metadata.file_path)
        
        try:
            # Delete main file
            if file_path.exists():
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    file_path.unlink
                )
            
            # Delete backup files
            await self._delete_all_backups(metadata.file_id)
            
            # Mark as deleted in registry
            await self._update_file_state(metadata.file_id, LifecycleState.DELETED)
            
            logger.info(f"File deleted: {metadata.file_id}")
        except Exception as e:
            logger.error(f"Error deleting file {metadata.file_id}: {e}")
    
    async def _delete_all_backups(self, file_id: str):
        """Delete all backup versions of a file"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM file_registry 
                WHERE file_id = ? OR parent_id = ?
            ''', (file_id, file_id))
            
            backup_files = cursor.fetchall()
        
        for file_data in backup_files:
            backup_metadata = self._row_to_metadata(file_data)
            await self._delete_backup_file(backup_metadata)
    
    async def _update_file_state(self, file_id: str, new_state: LifecycleState):
        """Update file state in registry"""
        current_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE file_registry 
                SET state = ?, last_state_change = ?
                WHERE file_id = ?
            ''', (new_state.value, current_time, file_id))
            
            conn.commit()
        
        # Record sync operation
        operation = SyncOperation(
            operation_id=hashlib.sha256(f"{file_id}_{time.time()}".encode()).hexdigest()[:16],
            file_id=file_id,
            operation_type="state_change",
            timestamp=current_time,
            status="completed",
            details=f"State changed to {new_state.value}"
        )
        
        await self._save_sync_operation(operation)
        
        logger.debug(f"File state updated: {file_id} -> {new_state.value}")
    
    async def _save_file_metadata(self, metadata: FileMetadata):
        """Save file metadata to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO file_registry (
                    file_id, file_path, file_name, file_type, file_size,
                    created_at, modified_at, accessed_at, state, policy_name,
                    checksum, version, parent_id, backup_path, archive_path,
                    expiry_date, last_state_change
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.file_id, metadata.file_path, metadata.file_name,
                metadata.file_type.value, metadata.file_size,
                metadata.created_at, metadata.modified_at, metadata.accessed_at,
                metadata.state.value, metadata.policy_name, metadata.checksum,
                metadata.version, metadata.parent_id, metadata.backup_path,
                metadata.archive_path, metadata.expiry_date,
                metadata.last_state_change or datetime.now()
            ))
            
            conn.commit()
    
    async def _save_sync_operation(self, operation: SyncOperation):
        """Save sync operation to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO sync_operations (
                    operation_id, file_id, operation_type, timestamp, status, details
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                operation.operation_id, operation.file_id, operation.operation_type,
                operation.timestamp, operation.status, operation.details
            ))
            
            conn.commit()
    
    def _row_to_metadata(self, row) -> FileMetadata:
        """Convert database row to FileMetadata object"""
        return FileMetadata(
            file_id=row[0],
            file_path=row[1],
            file_name=row[2],
            file_type=FileType(row[3]),
            file_size=row[4],
            created_at=datetime.fromisoformat(row[5]),
            modified_at=datetime.fromisoformat(row[6]),
            accessed_at=datetime.fromisoformat(row[7]),
            state=LifecycleState(row[8]),
            policy_name=row[9],
            checksum=row[10],
            version=row[11],
            parent_id=row[12],
            backup_path=row[13],
            archive_path=row[14],
            expiry_date=datetime.fromisoformat(row[15]) if row[15] else None,
            last_state_change=datetime.fromisoformat(row[16])
        )
    
    # Public API methods
    
    async def register_file(self, file_path: str, policy_name: str = "default") -> str:
        """Register a new file in the lifecycle system
        
        Args:
            file_path: Path to the file
            policy_name: Name of the lifecycle policy to apply
            
        Returns:
            Unique file ID
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate unique file ID
        file_id = hashlib.sha256(f"{file_path}_{time.time()}".encode()).hexdigest()[:16]
        
        metadata = FileMetadata(
            file_id=file_id,
            file_path=str(path.absolute()),
            file_name=path.name,
            file_type=self._detect_file_type(path.suffix),
            file_size=path.stat().st_size,
            created_at=datetime.fromtimestamp(path.stat().st_ctime),
            modified_at=datetime.fromtimestamp(path.stat().st_mtime),
            accessed_at=datetime.fromtimestamp(path.stat().st_atime),
            state=LifecycleState.UPLOADED,
            policy_name=policy_name,
            checksum=await self._calculate_file_checksum(path),
            version=1,
            last_state_change=datetime.now()
        )
        
        # Set expiry date based on policy
        policy = self.policies.get(policy_name)
        if policy:
            metadata.expiry_date = metadata.created_at + timedelta(days=policy.retention_days)
        
        await self._save_file_metadata(metadata)
        
        # Record operation
        operation = SyncOperation(
            operation_id=hashlib.sha256(f"{file_id}_{time.time()}".encode()).hexdigest()[:16],
            file_id=file_id,
            operation_type="register",
            timestamp=datetime.now(),
            status="completed",
            details=f"File registered with policy {policy_name}"
        )
        
        await self._save_sync_operation(operation)
        
        logger.info(f"File registered: {file_path} (ID: {file_id})")
        return file_id
    
    async def unregister_file(self, file_id: str):
        """Unregister a file from the lifecycle system"""
        await self._update_file_state(file_id, LifecycleState.DELETED)
        logger.info(f"File unregistered: {file_id}")
    
    async def change_file_policy(self, file_id: str, new_policy_name: str):
        """Change the lifecycle policy for a file"""
        if new_policy_name not in self.policies:
            raise ValueError(f"Unknown policy: {new_policy_name}")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE file_registry 
                SET policy_name = ?, last_state_change = ?
                WHERE file_id = ?
            ''', (new_policy_name, datetime.now(), file_id))
            
            conn.commit()
        
        logger.info(f"Policy changed for file {file_id}: {new_policy_name}")
    
    def create_policy(self, policy: LifecyclePolicy):
        """Create a new lifecycle policy"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO lifecycle_policies (
                    name, file_types, retention_days, archive_after_days,
                    delete_after_days, backup_frequency_hours, auto_archive,
                    auto_delete, versioning_enabled, max_versions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                policy.name,
                json.dumps([ft.value for ft in policy.file_types]),
                policy.retention_days,
                policy.archive_after_days,
                policy.delete_after_days,
                policy.backup_frequency_hours,
                policy.auto_archive,
                policy.auto_delete,
                policy.versioning_enabled,
                policy.max_versions
            ))
            
            conn.commit()
        
        self.policies[policy.name] = policy
        logger.info(f"Policy created: {policy.name}")
    
    async def get_file_status(self, file_id: str) -> Optional[FileMetadata]:
        """Get current status of a file"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM file_registry WHERE file_id = ?', (file_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_metadata(row)
        
        return None
    
    async def get_files_by_state(self, state: LifecycleState) -> List[FileMetadata]:
        """Get all files in a specific state"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM file_registry WHERE state = ?', (state.value,))
            rows = cursor.fetchall()
            
            return [self._row_to_metadata(row) for row in rows]
    
    async def get_expired_files(self) -> List[FileMetadata]:
        """Get all files that have exceeded their retention period"""
        current_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM file_registry 
                WHERE expiry_date IS NOT NULL 
                AND expiry_date < ? 
                AND state != ?
            ''', (current_time, LifecycleState.DELETED.value))
            
            rows = cursor.fetchall()
            
            return [self._row_to_metadata(row) for row in rows]
    
    async def force_archive(self, file_id: str):
        """Force archive a file"""
        metadata = await self.get_file_status(file_id)
        if not metadata:
            raise ValueError(f"File not found: {file_id}")
        
        policy = self.policies.get(metadata.policy_name)
        if not policy:
            raise ValueError(f"Policy not found: {metadata.policy_name}")
        
        await self._archive_file(metadata, policy)
    
    async def force_backup(self, file_id: str):
        """Force backup a file"""
        metadata = await self.get_file_status(file_id)
        if not metadata:
            raise ValueError(f"File not found: {file_id}")
        
        policy = self.policies.get(metadata.policy_name)
        if not policy:
            raise ValueError(f"Policy not found: {metadata.policy_name}")
        
        await self._create_backup(metadata, policy)
    
    async def force_delete(self, file_id: str):
        """Force delete a file"""
        metadata = await self.get_file_status(file_id)
        if not metadata:
            raise ValueError(f"File not found: {file_id}")
        
        await self._delete_file(metadata)
    
    async def sync_now(self):
        """Force immediate synchronization of all files"""
        logger.info("Forcing immediate synchronization")
        await self._sync_registry_state()
        await self._cleanup_orphaned_files()
        await self._cleanup_expired_files()
        await self._process_backup_queue()
        await self._enforce_policies()
        logger.info("Forced synchronization completed")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get lifecycle management statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT state, COUNT(*) FROM file_registry GROUP BY state')
            state_counts = dict(cursor.fetchall())
            
            cursor = conn.execute('SELECT COUNT(*) FROM file_registry')
            total_files = cursor.fetchone()[0]
            
            cursor = conn.execute('SELECT COUNT(*) FROM sync_operations WHERE timestamp > ?', 
                                (datetime.now() - timedelta(days=1),))
            recent_operations = cursor.fetchone()[0]
        
        return {
            'total_files': total_files,
            'files_by_state': state_counts,
            'policies_count': len(self.policies),
            'recent_operations_24h': recent_operations,
            'running': self._running
        }


# Scheduler-based sync for standalone operation
class LifecycleScheduler:
    """Scheduler for standalone lifecycle sync operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.lifecycle_sync = None
        self._running = False
    
    async def start(self):
        """Start the scheduler"""
        self.lifecycle_sync = LifecycleSync(self.config)
        self._running = True
        
        # Schedule periodic tasks
        schedule.every(self.config.get('cleanup_interval', 3600) // 60).minutes.do(
            lambda: asyncio.create_task(self._run_cleanup())
        )
        
        schedule.every(self.config.get('registry_sync_interval', 300) // 60).minutes.do(
            lambda: asyncio.create_task(self._run_sync())
        )
        
        # Start the sync service
        await self.lifecycle_sync.start_sync()
    
    async def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self.lifecycle_sync:
            await self.lifecycle_sync.stop_sync()
        
        schedule.clear()
    
    async def _run_cleanup(self):
        """Run cleanup tasks"""
        if self.lifecycle_sync:
            await self.lifecycle_sync._cleanup_orphaned_files()
            await self.lifecycle_sync._cleanup_expired_files()
    
    async def _run_sync(self):
        """Run sync tasks"""
        if self.lifecycle_sync:
            await self.lifecycle_sync._sync_registry_state()


# Configuration and utility functions
def load_config(config_path: str = "lifecycle_config.json") -> Dict[str, Any]:
    """Load configuration from file"""
    default_config = {
        "database_path": "file_registry.db",
        "local_storage_path": "./storage",
        "archive_path": "./archive", 
        "backup_path": "./backup",
        "registry_sync_interval": 300,
        "cleanup_interval": 3600,
        "moonshot_api_base": "https://api.moonshot.cn",
        "moonshot_api_key": None
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
    except Exception as e:
        logger.warning(f"Error loading config from {config_path}: {e}")
        logger.info("Using default configuration")
    
    return default_config


async def main():
    """Main entry point for standalone operation"""
    config = load_config()
    
    scheduler = LifecycleScheduler(config)
    
    try:
        await scheduler.start()
        logger.info("File Lifecycle Synchronization service started")
        
        # Keep running until interrupted
        while scheduler._running:
            schedule.run_pending()
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Shutting down lifecycle synchronization service")
    finally:
        await scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main())