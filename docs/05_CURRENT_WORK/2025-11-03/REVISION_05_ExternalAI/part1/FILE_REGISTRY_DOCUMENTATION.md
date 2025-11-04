# Cross-Platform File Registry Documentation

## Overview

The Cross-Platform File Registry is a comprehensive file management system that provides efficient file tracking, metadata storage, and cross-platform compatibility. It supports file registration, search, categorization, and integration with various storage providers.

## Key Features

### 1. File Registration and Tracking
- Unique ID generation for each file
- Automatic metadata extraction (size, type, timestamps, checksums)
- Cross-platform path handling
- Duplicate detection and prevention

### 2. Metadata Storage
- **Basic Info**: Name, path, size, type, extension
- **Timestamps**: Upload time, modification time, last access
- **File Properties**: MIME type, permissions, hidden status
- **Custom Data**: Tags, custom metadata, retrieval count
- **Storage Info**: Provider, storage path

### 3. Cross-Platform Compatibility
- Automatic path normalization (Windows/Unix)
- Platform-specific file permissions handling
- Consistent encoding and formatting

### 4. Search and Discovery
- Text-based filename search
- Type-based filtering (document, image, video, etc.)
- Tag-based filtering
- Directory-based filtering
- Size and date range filtering
- Combined search criteria

### 5. Storage Provider Integration
- Plugin architecture for storage providers
- Built-in Moonshot storage hooks
- Support for cloud and local storage

### 6. Efficient Indexing
- SQLite database backend
- Indexed columns for fast queries
- In-memory caching for frequently accessed files
- Thread-safe operations

## Installation

```python
from file_management.registry import FileRegistry, FileType
```

## Basic Usage

### Initialize Registry

```python
# Initialize with default database path
registry = FileRegistry()

# Initialize with custom database path
registry = FileRegistry("my_files.db")
```

### Register Files

```python
# Register a single file
file_id = registry.register_file(
    "/path/to/document.pdf",
    tags=["important", "project-a"],
    custom_metadata={"author": "John Doe", "department": "Legal"}
)

# Register multiple files
file_ids = []
for file_path in file_list:
    file_id = registry.register_file(file_path, tags=["batch-upload"])
    file_ids.append(file_id)
```

### Retrieve Files

```python
# Get file metadata
metadata = registry.get_file(file_id)

if metadata:
    print(f"File: {metadata.name}")
    print(f"Type: {metadata.file_type}")
    print(f"Size: {metadata.size} bytes")
    print(f"Path: {metadata.absolute_path}")
    print(f"Tags: {metadata.tags}")
```

### Search Files

```python
# Search by name
results = registry.search_files(query="document")

# Search by type
docs = registry.search_files(file_type=FileType.DOCUMENT.value)

# Search by tags
important_files = registry.search_files(tags=["important"])

# Combined search
recent_docs = registry.search_files(
    query="report",
    file_type=FileType.DOCUMENT.value,
    date_from="2024-01-01",
    min_size=1024
)

# Search results
for metadata in results:
    print(f"Found: {metadata.name} ({metadata.file_type})")
```

### File Management

```python
# Update file metadata
registry.update_file(
    file_id,
    tags=["updated", "reviewed"],
    custom_metadata={"status": "approved"}
)

# Remove file from registry
registry.remove_file(file_id)

# Get registry statistics
stats = registry.get_file_stats()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_mb']} MB")
```

### File Discovery

```python
# Discover and register all files in a directory
registered_ids = registry.discover_files("/path/to/directory")

# Non-recursive discovery
registered_ids = registry.discover_files(
    "/path/to/directory", 
    recursive=False
)

# Include hidden files
registered_ids = registry.discover_files(
    "/path/to/directory",
    include_hidden=True
)
```

### Export and Import

```python
# Export to JSON
registry.export_registry("backup.json", format="json")

# Export to CSV
registry.export_registry("backup.csv", format="csv")

# Import registry data
registry.import_registry("backup.json", merge=True)

# Import without merging (replace existing)
registry.import_registry("backup.json", merge=False)
```

### Storage Provider Integration

```python
# Register a storage provider
registry.register_storage_provider("moonshot", MoonshotStorageProvider)

# Upload file to storage
storage_path = registry.upload_to_storage(
    file_id, 
    "moonshot",
    bucket="my-bucket"
)
```

## Advanced Features

### Custom Metadata

```python
# Register with extensive metadata
file_id = registry.register_file(
    "document.pdf",
    tags=["legal", "contract", "confidential"],
    custom_metadata={
        "author": "Jane Smith",
        "version": "1.2",
        "keywords": ["agreement", "terms", "2024"],
        "review_date": "2024-12-01"
    }
)

# Update custom metadata
registry.update_file_metadata(file_id, {
    "review_status": "approved",
    "approved_by": "legal_team"
})
```

### Cleanup Operations

```python
# Remove entries for non-existent files
cleanup_stats = registry.cleanup_registry()
print(f"Removed {cleanup_stats['removed_entries']} stale entries")
```

### Statistics and Monitoring

```python
# Get detailed statistics
stats = registry.get_file_stats()

# Analyze file distribution
for file_type, count in stats['files_by_type'].items():
    print(f"{file_type}: {count} files")

# Recent activity
print(f"Recent files: {stats['recent_files_30_days']}")
```

## File Types Supported

The registry automatically detects these file types:

- **Document**: PDF, DOC, DOCX, TXT, RTF, ODT, TEX
- **Image**: JPG, JPEG, PNG, GIF, BMP, SVG, WEBP, TIFF
- **Video**: MP4, AVI, MKV, MOV, WMV, FLV, WEBM, M4V
- **Audio**: MP3, WAV, FLAC, AAC, OGG, WMA, M4A
- **Archive**: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ
- **Code**: PY, JS, HTML, CSS, JAVA, CPP, C, PHP, RB
- **Data**: JSON, XML, CSV, XLSX, XLS, SQL, DB

## Thread Safety

The FileRegistry is thread-safe and can be used in multi-threaded applications:

```python
import threading

def register_worker(registry, file_list):
    for file_path in file_list:
        registry.register_file(file_path)

# Use with multiple threads
threads = []
for batch in file_batches:
    thread = threading.Thread(target=register_worker, args=(registry, batch))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
```

## Error Handling

```python
try:
    file_id = registry.register_file("/path/to/file.pdf")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Registration failed: {e}")

# Check if file exists before operations
if registry.get_file(file_id):
    # File exists, proceed with operations
    pass
```

## Performance Considerations

1. **Database Indexing**: The registry uses indexed columns for fast queries
2. **Memory Caching**: Frequently accessed files are cached in memory
3. **Batch Operations**: Use bulk discovery for large directory trees
4. **Cleanup**: Regularly run cleanup to remove stale entries
5. **Export/Import**: Use JSON for structured data, CSV for spreadsheet compatibility

## Integration Examples

### With Flask Web Application

```python
from flask import Flask, request, jsonify
from file_management.registry import FileRegistry

app = Flask(__name__)
registry = FileRegistry()

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(file.filename)
    
    file_id = registry.register_file(
        file.filename,
        tags=request.form.getlist('tags')
    )
    
    return jsonify({'file_id': file_id})

@app.route('/search')
def search_files():
    query = request.args.get('q', '')
    results = registry.search_files(query=query)
    
    return jsonify([{
        'id': meta.id,
        'name': meta.name,
        'type': meta.file_type,
        'size': meta.size
    } for meta in results])
```

### With Moonshot Storage

```python
class MoonshotStorageProvider:
    def __init__(self, api_key, bucket):
        self.api_key = api_key
        self.bucket = bucket
    
    def upload(self, local_path, filename):
        # Upload to Moonshot storage
        # Return storage URL
        pass

# Register and use
registry.register_storage_provider("moonshot", MoonshotStorageProvider)
storage_url = registry.upload_to_storage(file_id, "moonshot", 
                                        api_key="xxx", bucket="files")
```

## Best Practices

1. **Use Tags Effectively**: Organize files with meaningful tags
2. **Regular Cleanup**: Run cleanup_registry() periodically
3. **Backup Registry**: Export registry data regularly
4. **Custom Metadata**: Store relevant business metadata
5. **Error Handling**: Always handle FileNotFoundError and exceptions
6. **Performance**: Use search filters to limit result sets
7. **Thread Safety**: Use registry instance consistently across threads

## Troubleshooting

### Common Issues

1. **File Not Found After Registration**
   - File may have been moved or deleted
   - Run cleanup_registry() to remove stale entries

2. **Search Returns No Results**
   - Check search criteria and filters
   - Verify file was actually registered
   - Check case sensitivity in queries

3. **Permission Errors**
   - Ensure registry has read access to file system
   - Check file permissions on target files

4. **Database Locked**
   - Registry may be in use by another process
   - Wait for concurrent operations to complete
   - Consider using separate registry instances

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check registry state
print(f"Registry: {registry}")
stats = registry.get_file_stats()
print(f"Stats: {stats}")
```