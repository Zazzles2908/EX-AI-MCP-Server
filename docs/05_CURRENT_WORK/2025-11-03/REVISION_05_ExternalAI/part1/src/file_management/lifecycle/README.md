# File Lifecycle Synchronization

A comprehensive file lifecycle management system that provides automated file lifecycle tracking, policy enforcement, and cloud storage synchronization.

## Features

### 🔄 File Lifecycle State Tracking
- **Uploaded**: Newly registered files awaiting processing
- **Processing**: Files currently being processed or indexed
- **Archived**: Files moved to long-term storage
- **Deleted**: Files removed from the system
- **Backup Pending**: Files queued for backup
- **Backup Complete**: Files successfully backed up
- **Expired**: Files exceeding retention periods

### 🧹 Automatic Cleanup
- **Orphaned File Detection**: Identifies files in storage not in registry
- **Expired File Handling**: Removes files past retention period
- **Backup Version Management**: Maintains configurable number of versions
- **Storage Space Optimization**: Automatically archives and deletes based on policies

### 📋 Lifecycle Policy Enforcement
- **Retention Periods**: Configurable time limits for file storage
- **Archival Rules**: Automatic archiving based on file age
- **Deletion Policies**: Automated cleanup of expired content
- **Backup Scheduling**: Regular backup creation for important files
- **Version Control**: Maintain multiple versions with automatic cleanup

### ☁️ Moonshot Storage Integration
- **Cloud Synchronization**: Sync metadata with Moonshot storage APIs
- **State Consistency**: Ensure local and cloud states remain synchronized
- **API Integration**: Seamless integration with existing storage infrastructure
- **Error Handling**: Robust error handling for network and API issues

### 🔗 State Synchronization
- **Registry Consistency**: Sync between local file system and registry database
- **Real-time Updates**: Immediate state changes when files are modified
- **Conflict Resolution**: Handle conflicts between local and cloud states
- **Audit Trail**: Complete operation log for compliance and debugging

### 💾 Automated Backup & Versioning
- **Scheduled Backups**: Configurable backup frequency per file type
- **Version Management**: Maintain configurable number of file versions
- **Differential Backups**: Efficient storage with checksum-based duplicate detection
- **Disaster Recovery**: Complete backup and restore functionality

## Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure the System**:
```bash
cp config_example.json config.json
# Edit config.json with your settings
```

3. **Set up Storage Directories**:
```bash
mkdir -p storage archive backup
```

## Configuration

### Basic Configuration (config.json)
```json
{
  "database_path": "file_registry.db",
  "local_storage_path": "./storage",
  "archive_path": "./archive",
  "backup_path": "./backup",
  "registry_sync_interval": 300,
  "cleanup_interval": 3600,
  "moonshot_api_base": "https://api.moonshot.cn",
  "moonshot_api_key": null
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `database_path` | Path to SQLite database | `file_registry.db` |
| `local_storage_path` | Main storage directory | `./storage` |
| `archive_path` | Archive storage directory | `./archive` |
| `backup_path` | Backup storage directory | `./backup` |
| `registry_sync_interval` | Sync frequency in seconds | `300` (5 minutes) |
| `cleanup_interval` | Cleanup frequency in seconds | `3600` (1 hour) |
| `moonshot_api_base` | Moonshot API base URL | `https://api.moonshot.cn` |
| `moonshot_api_key` | API key for authentication | `null` |

## Usage

### Basic Usage

```python
import asyncio
from lifecycle_sync import LifecycleSync, load_config

async def main():
    # Load configuration
    config = load_config("config.json")
    
    # Initialize lifecycle management
    lifecycle = LifecycleSync(config)
    
    # Register a file
    file_id = await lifecycle.register_file("./documents/report.pdf")
    print(f"File registered with ID: {file_id}")
    
    # Get file status
    status = await lifecycle.get_file_status(file_id)
    print(f"File status: {status.state}")
    
    # Run manual sync
    await lifecycle.sync_now()

asyncio.run(main())
```

### Advanced Usage with Scheduler

```python
import asyncio
from lifecycle_sync import LifecycleScheduler

async def main():
    config = load_config("config.json")
    
    # Start background scheduler
    scheduler = LifecycleScheduler(config)
    await scheduler.start()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        await scheduler.stop()

asyncio.run(main())
```

### Custom Policies

```python
from lifecycle_sync import LifecyclePolicy, FileType

# Create custom policy
policy = LifecyclePolicy(
    name="quick_cleanup",
    file_types=[FileType.IMAGE, FileType.DOCUMENT],
    retention_days=30,
    archive_after_days=7,
    delete_after_days=30,
    backup_frequency_hours=24,
    auto_archive=True,
    auto_delete=True,
    versioning_enabled=True,
    max_versions=3
)

# Apply policy to lifecycle management
lifecycle.create_policy(policy)

# Register file with custom policy
file_id = await lifecycle.register_file("./file.txt", "quick_cleanup")
```

### Force Operations

```python
# Force backup of specific file
await lifecycle.force_backup(file_id)

# Force archive of specific file
await lifecycle.force_archive(file_id)

# Force deletion of specific file
await lifecycle.force_delete(file_id)

# Change file policy
await lifecycle.change_file_policy(file_id, "new_policy_name")
```

### Query Operations

```python
# Get files by state
archived_files = await lifecycle.get_files_by_state(LifecycleState.ARCHIVED)

# Get expired files
expired_files = await lifecycle.get_expired_files()

# Get statistics
stats = await lifecycle.get_statistics()
print(f"Total files: {stats['total_files']}")
print(f"Files by state: {stats['files_by_state']}")
```

## API Reference

### Classes

#### LifecycleSync
Main class for file lifecycle management.

**Methods:**
- `register_file(file_path, policy_name="default") -> str`
- `unregister_file(file_id)`
- `change_file_policy(file_id, new_policy_name)`
- `get_file_status(file_id) -> Optional[FileMetadata]`
- `get_files_by_state(state) -> List[FileMetadata]`
- `get_expired_files() -> List[FileMetadata]`
- `force_archive(file_id)`
- `force_backup(file_id)`
- `force_delete(file_id)`
- `sync_now()`
- `get_statistics() -> Dict[str, Any]`

#### LifecycleScheduler
Background scheduler for automated operations.

**Methods:**
- `start()`
- `stop()`

### Enumerations

#### LifecycleState
- `UPLOADED`
- `PROCESSING`
- `ARCHIVED`
- `DELETED`
- `BACKUP_PENDING`
- `BACKUP_COMPLETE`
- `EXPIRED`

#### FileType
- `DOCUMENT`
- `IMAGE`
- `VIDEO`
- `AUDIO`
- `ARCHIVE`
- `OTHER`

### Data Classes

#### LifecyclePolicy
Configuration for file lifecycle rules.

#### FileMetadata
Complete file information for lifecycle tracking.

#### SyncOperation
Record of synchronization operations.

## Default Policies

The system comes with three default policies:

### Documents Policy
- **File Types**: Documents (txt, pdf, doc, docx)
- **Retention**: 365 days
- **Archive**: After 90 days
- **Delete**: After 365 days
- **Backup**: Daily
- **Auto Archive**: Yes
- **Auto Delete**: Yes
- **Versions**: 5

### Media Policy
- **File Types**: Images, Videos, Audio
- **Retention**: 730 days
- **Archive**: After 180 days
- **Delete**: After 730 days
- **Backup**: Every 12 hours
- **Auto Archive**: Yes
- **Auto Delete**: No
- **Versions**: 3

### Archives Policy
- **File Types**: Archives (zip, rar, 7z)
- **Retention**: 1825 days (5 years)
- **Archive**: After 30 days
- **Delete**: After 1825 days
- **Backup**: Weekly
- **Auto Archive**: No
- **Auto Delete**: No
- **Versions**: 2

## Background Operations

The system runs several background operations:

### Registry Sync Loop (Every 5 minutes)
- Synchronizes registry with actual file system
- Updates file metadata (timestamps, sizes, checksums)
- Syncs state with cloud storage
- Handles orphaned files

### Cleanup Loop (Every hour)
- Detects orphaned files in storage
- Removes expired files based on policies
- Cleans up old backup versions
- Optimizes storage space

### Backup Loop (Every hour)
- Processes files requiring backup
- Creates versioned backups
- Manages backup retention
- Handles backup errors

### Policy Enforcement Loop (Every 30 minutes)
- Enforces retention policies
- Archives files based on age
- Deletes files exceeding retention
- Updates expiry dates

## Database Schema

### file_registry Table
```sql
CREATE TABLE file_registry (
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
    last_state_change TIMESTAMP NOT NULL
);
```

### sync_operations Table
```sql
CREATE TABLE sync_operations (
    operation_id TEXT PRIMARY KEY,
    file_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    details TEXT
);
```

### lifecycle_policies Table
```sql
CREATE TABLE lifecycle_policies (
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
);
```

## Monitoring and Logging

### Logging Levels
- `INFO`: General operation information
- `DEBUG`: Detailed operation debugging
- `WARNING`: Non-critical issues
- `ERROR`: Critical errors requiring attention

### Statistics
Access comprehensive statistics via `get_statistics()`:
- Total files managed
- Files by lifecycle state
- Number of configured policies
- Recent operations (24 hours)
- System running status

### Example Monitoring Script
```python
async def monitor_lifecycle():
    lifecycle = LifecycleSync(load_config())
    
    while True:
        stats = await lifecycle.get_statistics()
        
        print(f"Total files: {stats['total_files']}")
        print(f"Uploading files: {stats['files_by_state'].get('uploaded', 0)}")
        print(f"Archived files: {stats['files_by_state'].get('archived', 0)}")
        print(f"Recent operations: {stats['recent_operations_24h']}")
        
        await asyncio.sleep(300)  # Every 5 minutes
```

## Error Handling

### Robust Error Recovery
- Automatic retry for transient failures
- Comprehensive error logging
- Graceful degradation for API failures
- Data integrity protection

### Common Error Scenarios
- **File Not Found**: Automatically marks as deleted
- **Network API Failures**: Continues with local operations
- **Disk Space Issues**: Optimizes storage usage
- **Corrupted Database**: Rebuilds from file system scan

## Performance Considerations

### Optimization Features
- **Concurrent Operations**: Uses ThreadPoolExecutor for I/O operations
- **Efficient Database**: SQLite with proper indexing
- **Lazy Loading**: File metadata loaded on demand
- **Batch Operations**: Processes multiple files efficiently

### Scalability
- Suitable for managing thousands of files
- Configurable worker threads
- Efficient memory usage with async operations
- Database optimization for large datasets

## Security Features

### Data Protection
- **File Checksums**: SHA-256 hashing for integrity verification
- **Secure Deletion**: Optional secure file deletion
- **Access Control**: File permission preservation
- **Audit Trail**: Complete operation logging

### Privacy Compliance
- **Retention Enforcement**: Automatic compliance with retention policies
- **Data Minimization**: Remove unnecessary file copies
- **Encryption Ready**: Support for encrypted storage paths
- **GDPR Compliance**: Automated data lifecycle management

## Troubleshooting

### Common Issues

**Files not being archived automatically**
- Check if `auto_archive` is enabled in the policy
- Verify file age exceeds `archive_after_days`
- Check system logs for errors

**Backup operations failing**
- Verify backup directory permissions
- Check available disk space
- Review API authentication if using cloud backup

**Synchronization issues**
- Check database connectivity
- Verify file system permissions
- Review network connectivity for cloud sync

**High memory usage**
- Adjust worker thread pool size
- Increase sync intervals for large file sets
- Monitor database size and optimize

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

See `usage_example.py` for comprehensive usage examples including:
- Basic file registration
- Custom policy creation
- Background scheduling
- Force operations
- Monitoring and statistics

## License

This file lifecycle synchronization system is part of the larger file management infrastructure.