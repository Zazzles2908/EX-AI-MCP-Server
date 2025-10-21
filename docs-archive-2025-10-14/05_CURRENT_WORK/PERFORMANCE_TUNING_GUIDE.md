# Performance Tuning Guide
**Date:** 2025-10-18  
**Version:** 1.0  
**Audience:** Developers, DevOps

---

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [File Cache Tuning](#file-cache-tuning)
4. [Parallel Reading Tuning](#parallel-reading-tuning)
5. [Path Cache Tuning](#path-cache-tuning)
6. [Consolidation Tuning](#consolidation-tuning)
7. [Memory Management](#memory-management)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 **Overview**

This guide helps you optimize the performance of the auto-execution system by tuning various caching and parallelization parameters.

### **Performance Targets:**

- File reading: 40-60% faster
- Path operations: 10-20% faster
- Consolidation: 15-25% faster
- Overall workflow: 20-30% faster
- Memory overhead: <20% increase

---

## 🚀 **Quick Start**

### **Default Configuration:**

The system ships with sensible defaults that work well for most use cases:

```python
# File Cache
MAX_CACHE_SIZE = 128 files
MAX_FILE_SIZE = 10 MB
TTL = Based on file modification time

# Parallel Reading
MAX_WORKERS = 4 threads
PARALLEL_THRESHOLD = 3 files

# Path Cache
PATH_CACHE_SIZE = 256 entries
MODEL_CACHE_SIZE = 64 entries

# Consolidation
INCREMENTAL_UPDATES = Enabled
CONTENT_HASHING = Enabled
```

### **When to Tune:**

Tune performance when you observe:
- Low cache hit rates (<50%)
- High memory usage (>500MB increase)
- Slow file reading (>1s for 10 files)
- Slow consolidation (>2s for 20 steps)

---

## 📁 **File Cache Tuning**

### **Cache Size (`max_cache_size`)**

**Default:** 128 files

**When to increase:**
- Working with large codebases (>1000 files)
- High file reuse across steps
- Sufficient memory available (>2GB free)

**When to decrease:**
- Limited memory (<1GB free)
- Low file reuse
- Many unique files per workflow

**Example:**

```python
from tools.workflow.file_cache import FileCache

# Increase for large codebases
cache = FileCache(max_cache_size=256)

# Decrease for memory-constrained environments
cache = FileCache(max_cache_size=64)
```

### **File Size Limit (`max_file_size`)**

**Default:** 10 MB

**When to increase:**
- Working with large data files
- Sufficient memory available
- Files are frequently reused

**When to decrease:**
- Limited memory
- Large files are rarely reused
- Risk of memory bloat

**Example:**

```python
# Increase for large files
cache = FileCache(max_file_size=20 * 1024 * 1024)  # 20MB

# Decrease for memory constraints
cache = FileCache(max_file_size=5 * 1024 * 1024)  # 5MB
```

### **Monitoring Cache Performance:**

```python
from tools.workflow.file_cache import get_file_cache

cache = get_file_cache()
stats = cache.get_stats()

print(f"Hit rate: {stats['hit_rate']:.1%}")
print(f"Cache size: {stats['cache_size']}/{cache.max_cache_size}")
print(f"Evictions: {stats['evictions']}")
print(f"Files skipped: {stats['files_skipped']}")

# Target metrics:
# - Hit rate: >70%
# - Evictions: <10% of total reads
# - Files skipped: <5% of total reads
```

---

## ⚡ **Parallel Reading Tuning**

### **Worker Count (`max_workers`)**

**Default:** 4 threads

**When to increase:**
- Many files to read (>50)
- Fast storage (SSD)
- High CPU core count (>8 cores)

**When to decrease:**
- Few files to read (<10)
- Slow storage (HDD)
- Low CPU core count (<4 cores)

**Example:**

```python
from tools.workflow.file_cache import get_file_cache

cache = get_file_cache()

# Increase for many files + fast storage
results = cache.read_files_parallel(files, max_workers=8)

# Decrease for few files or slow storage
results = cache.read_files_parallel(files, max_workers=2)
```

### **Parallel Threshold:**

**Default:** 3 files (parallel for >2 files)

**Rationale:** Parallel reading has overhead. For small file counts, sequential is faster.

**Recommendation:** Don't change unless benchmarks show benefit.

### **Monitoring Parallel Performance:**

```python
import time
from tools.workflow.file_cache import get_file_cache

cache = get_file_cache()

# Measure parallel reading time
start = time.time()
results = cache.read_files_parallel(files, max_workers=4)
parallel_time = time.time() - start

print(f"Parallel read: {len(files)} files in {parallel_time:.2f}s")
print(f"Throughput: {len(files)/parallel_time:.1f} files/sec")

# Target metrics:
# - Throughput: >10 files/sec for 10+ files
# - Time: <1s for 10 files, <5s for 100 files
```

---

## 🗂️ **Path Cache Tuning**

### **Path Cache Size:**

**Default:** 256 entries (LRU)

**When to increase:**
- Many unique paths validated
- High path reuse across steps
- Sufficient memory

**When to decrease:**
- Limited memory
- Low path reuse
- Few unique paths

**Example:**

```python
from functools import lru_cache
from tools.workflow.performance_optimizer import normalize_path

# Increase cache size
@lru_cache(maxsize=512)
def normalize_path_large(path: str) -> str:
    return normalize_path(path)
```

### **Model Cache Size:**

**Default:** 64 entries (LRU)

**Recommendation:** Rarely needs tuning (few unique models).

### **Monitoring Path Cache:**

```python
from tools.workflow.performance_optimizer import get_performance_optimizer

optimizer = get_performance_optimizer()
stats = optimizer.get_stats()

print(f"Path cache hit rate: {stats['path_cache_hit_rate']:.1%}")
print(f"Model cache hit rate: {stats['model_cache_hit_rate']:.1%}")

# Target metrics:
# - Path cache hit rate: >80%
# - Model cache hit rate: >90%
```

---

## 📝 **Consolidation Tuning**

### **Incremental Updates:**

**Default:** Enabled

**When to disable:**
- Content changes frequently
- Low step count (<5 steps)
- Debugging consolidation issues

**Example:**

```python
from tools.workflow.optimized_consolidation import get_optimized_consolidator

consolidator = get_optimized_consolidator()

# Force full consolidation
consolidated = consolidator.get_consolidated_text(force_full=True)
```

### **Content Hashing:**

**Default:** Enabled (MD5)

**Recommendation:** Don't disable (minimal overhead, prevents redundant work).

### **Monitoring Consolidation:**

```python
from tools.workflow.optimized_consolidation import get_optimized_consolidator

consolidator = get_optimized_consolidator()
stats = consolidator.get_stats()

print(f"Total consolidations: {stats['total_consolidations']}")
print(f"Incremental: {stats['incremental_consolidations']}")
print(f"Cache hits: {stats['cache_hits']}")

# Target metrics:
# - Incremental consolidations: >50% of total
# - Cache hits: >30% of total
```

---

## 💾 **Memory Management**

### **Monitoring Memory Usage:**

```python
from tools.workflow.performance_metrics import get_performance_metrics

metrics = get_performance_metrics()
metrics.start_workflow()

# ... do work ...

metrics.end_workflow()
summary = metrics.get_summary()

print(f"Memory start: {summary['memory_start_mb']:.1f}MB")
print(f"Memory end: {summary['memory_end_mb']:.1f}MB")
print(f"Memory delta: {summary['memory_delta_mb']:+.1f}MB")
print(f"Memory peak: {summary['memory_peak_mb']:.1f}MB")

# Target metrics:
# - Memory delta: <100MB for typical workflows
# - Memory peak: <500MB total
```

### **Reducing Memory Usage:**

1. **Reduce cache sizes:**
   ```python
   cache = FileCache(max_cache_size=64, max_file_size=5*1024*1024)
   ```

2. **Clear caches periodically:**
   ```python
   from tools.workflow.file_cache import get_file_cache
   cache = get_file_cache()
   cache.clear()
   ```

3. **Reduce parallel workers:**
   ```python
   results = cache.read_files_parallel(files, max_workers=2)
   ```

4. **Disable metrics (if not needed):**
   ```python
   # Don't start metrics tracking
   # metrics.start_workflow()
   ```

---

## 🔧 **Troubleshooting**

### **Low Cache Hit Rate (<50%)**

**Symptoms:**
- File cache hit rate <50%
- Slow file reading despite caching

**Causes:**
- Files changing frequently (invalidating cache)
- Many unique files (exceeding cache size)
- Cache size too small

**Solutions:**
1. Increase cache size
2. Check file modification patterns
3. Verify files are being reused

### **High Memory Usage (>500MB)**

**Symptoms:**
- Memory delta >500MB
- Out of memory errors
- Slow performance

**Causes:**
- Cache size too large
- Large files in cache
- Memory leak

**Solutions:**
1. Reduce cache size
2. Reduce max file size
3. Clear caches periodically
4. Check for memory leaks

### **Slow Parallel Reading**

**Symptoms:**
- Parallel reading slower than sequential
- Low throughput (<5 files/sec)

**Causes:**
- Too many workers (overhead)
- Slow storage (HDD)
- Small files (overhead dominates)

**Solutions:**
1. Reduce worker count
2. Use sequential for small file counts
3. Upgrade to SSD storage

### **Slow Consolidation**

**Symptoms:**
- Consolidation takes >2s for 20 steps
- High CPU usage during consolidation

**Causes:**
- Incremental updates disabled
- Large findings text
- Content hashing overhead

**Solutions:**
1. Enable incremental updates
2. Reduce findings text size
3. Force full consolidation less frequently

---

## 📊 **Performance Checklist**

Before deploying to production:

- [ ] Run benchmarks to measure actual improvements
- [ ] Monitor cache hit rates (target >70%)
- [ ] Monitor memory usage (target <100MB delta)
- [ ] Monitor parallel reading throughput (target >10 files/sec)
- [ ] Monitor consolidation time (target <2s for 20 steps)
- [ ] Test with realistic workloads
- [ ] Test with edge cases (large files, many files, memory pressure)
- [ ] Document any custom tuning parameters

---

**Status:** ✅ **PRODUCTION READY**

**Version:** 1.0

**Last Updated:** 2025-10-18

