# Troubleshooting Guide - Auto-Execution System
**Date:** 2025-10-18  
**Version:** 1.0  
**Audience:** Developers, Support Engineers

---

## 📋 **Table of Contents**

1. [Common Issues](#common-issues)
2. [Performance Issues](#performance-issues)
3. [Memory Issues](#memory-issues)
4. [Cache Issues](#cache-issues)
5. [Parallel Reading Issues](#parallel-reading-issues)
6. [Debugging Tools](#debugging-tools)

---

## 🔍 **Common Issues**

### **Issue: Auto-execution not working**

**Symptoms:**
- Tool only executes one step
- No recursive execution
- Manual step calls required

**Diagnosis:**
```python
# Check if next_step_required is set correctly
request.next_step_required = True  # Should be True to continue

# Check confidence level
request.confidence = "medium"  # Should NOT be "certain", "very_high", or "almost_certain"

# Check step count
# Should be less than MAX_AUTO_STEPS for the tool type
```

**Solutions:**
1. Ensure `next_step_required=True` in request
2. Set confidence to "low", "medium", or "high"
3. Verify step count hasn't exceeded limit
4. Check logs for auto-execution decision

**Prevention:**
- Always set `next_step_required=True` unless investigation is complete
- Use appropriate confidence levels
- Monitor step counts

---

### **Issue: Files not being cached**

**Symptoms:**
- Cache hit rate is 0%
- Every file read is a cache miss
- Slow file reading despite caching

**Diagnosis:**
```python
from tools.workflow.file_cache import get_file_cache

cache = get_file_cache()
stats = cache.get_stats()

print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate']:.1%}")
print(f"Files skipped: {stats['files_skipped']}")
```

**Solutions:**
1. **Files too large:** Reduce `max_file_size` or increase limit
2. **Files changing:** Check file modification times
3. **Cache full:** Increase `max_cache_size`
4. **Cache cleared:** Check for cache.clear() calls

**Prevention:**
- Monitor cache statistics
- Set appropriate cache size limits
- Avoid clearing cache unnecessarily

---

### **Issue: Parallel reading slower than sequential**

**Symptoms:**
- Parallel reading takes longer than sequential
- Low throughput (<5 files/sec)
- High CPU usage

**Diagnosis:**
```python
import time
from tools.workflow.file_cache import get_file_cache

cache = get_file_cache()

# Measure sequential
start = time.time()
for file in files:
    cache.read_file(file)
seq_time = time.time() - start

# Measure parallel
cache.clear()
start = time.time()
cache.read_files_parallel(files, max_workers=4)
par_time = time.time() - start

print(f"Sequential: {seq_time:.2f}s")
print(f"Parallel: {par_time:.2f}s")
print(f"Speedup: {seq_time/par_time:.2f}x")
```

**Solutions:**
1. **Too many workers:** Reduce `max_workers` to 2
2. **Small files:** Use sequential for <10 files
3. **Slow storage:** Upgrade to SSD or reduce workers
4. **Overhead:** Increase file count threshold

**Prevention:**
- Use parallel only for >10 files
- Tune worker count based on storage speed
- Monitor throughput metrics

---

## ⚡ **Performance Issues**

### **Issue: Slow workflow execution**

**Symptoms:**
- Workflow takes >30s for 10 steps
- High CPU usage
- Slow file reading

**Diagnosis:**
```python
from tools.workflow.performance_metrics import get_performance_metrics

metrics = get_performance_metrics()
summary = metrics.get_summary()

print(f"Total step time: {summary['total_step_time']:.2f}s")
print(f"Avg step time: {summary['avg_step_time']:.2f}s")
print(f"File read time: {summary['total_file_read_time']:.2f}s")
print(f"Consolidation time: {summary['total_consolidation_time']:.2f}s")
```

**Solutions:**
1. **Slow file reading:** Enable caching, use parallel reading
2. **Slow consolidation:** Enable incremental updates
3. **Too many steps:** Reduce step count or increase confidence threshold
4. **Large files:** Reduce file size or skip from cache

**Prevention:**
- Monitor performance metrics
- Optimize file reading
- Use appropriate step limits

---

### **Issue: High consolidation time**

**Symptoms:**
- Consolidation takes >2s for 20 steps
- High CPU usage during consolidation
- Slow workflow completion

**Diagnosis:**
```python
from tools.workflow.optimized_consolidation import get_optimized_consolidator

consolidator = get_optimized_consolidator()
stats = consolidator.get_stats()

print(f"Total consolidations: {stats['total_consolidations']}")
print(f"Incremental: {stats['incremental_consolidations']}")
print(f"Cache hits: {stats['cache_hits']}")
```

**Solutions:**
1. **Incremental disabled:** Enable incremental updates
2. **Large findings:** Reduce findings text size
3. **Many steps:** Reduce step count
4. **Content hashing overhead:** Disable if not needed

**Prevention:**
- Use incremental consolidation
- Keep findings concise
- Monitor consolidation statistics

---

## 💾 **Memory Issues**

### **Issue: High memory usage**

**Symptoms:**
- Memory usage >500MB
- Out of memory errors
- Slow performance
- System swapping

**Diagnosis:**
```python
from tools.workflow.performance_metrics import get_performance_metrics

metrics = get_performance_metrics()
summary = metrics.get_summary()

print(f"Memory start: {summary['memory_start_mb']:.1f}MB")
print(f"Memory end: {summary['memory_end_mb']:.1f}MB")
print(f"Memory delta: {summary['memory_delta_mb']:+.1f}MB")
print(f"Memory peak: {summary['memory_peak_mb']:.1f}MB")
```

**Solutions:**
1. **Large cache:** Reduce `max_cache_size` to 64
2. **Large files:** Reduce `max_file_size` to 5MB
3. **Too many workers:** Reduce `max_workers` to 2
4. **Memory leak:** Clear caches periodically

**Prevention:**
- Monitor memory usage
- Set appropriate cache limits
- Clear caches after workflows
- Use memory profiling tools

---

### **Issue: Memory leak**

**Symptoms:**
- Memory usage grows over time
- Never decreases
- Eventually runs out of memory

**Diagnosis:**
```python
import gc
from tools.workflow.file_cache import get_file_cache

# Force garbage collection
gc.collect()

# Check cache size
cache = get_file_cache()
stats = cache.get_stats()
print(f"Cache size: {stats['cache_size']}")

# Check for circular references
import sys
print(f"Ref count: {sys.getrefcount(cache)}")
```

**Solutions:**
1. **Clear caches:** Call `cache.clear()` periodically
2. **Force GC:** Call `gc.collect()` after workflows
3. **Reset singletons:** Use reset functions
4. **Check circular refs:** Use memory profiler

**Prevention:**
- Clear caches after workflows
- Monitor memory over time
- Use memory profiling in development

---

## 🗂️ **Cache Issues**

### **Issue: Cache invalidation not working**

**Symptoms:**
- Modified files return old content
- Cache doesn't detect file changes
- Stale data in cache

**Diagnosis:**
```python
import os
from tools.workflow.file_cache import get_file_cache

cache = get_file_cache()

# Check file modification time
file_path = "test.txt"
mtime = os.path.getmtime(file_path)
print(f"File mtime: {mtime}")

# Read file
content = cache.read_file(file_path)

# Modify file
with open(file_path, 'w') as f:
    f.write("New content")

# Check new mtime
new_mtime = os.path.getmtime(file_path)
print(f"New mtime: {new_mtime}")

# Read again (should detect change)
new_content = cache.read_file(file_path)
print(f"Content changed: {content != new_content}")
```

**Solutions:**
1. **Mtime not changing:** Ensure file system supports mtime
2. **Cache key issue:** Clear cache and retry
3. **Race condition:** Add delay between writes
4. **Manual invalidation:** Call `cache.invalidate(path)`

**Prevention:**
- Use file systems with mtime support
- Add delays between file modifications
- Monitor cache invalidation

---

## ⚡ **Parallel Reading Issues**

### **Issue: ThreadPoolExecutor errors**

**Symptoms:**
- Parallel reading fails
- ThreadPoolExecutor exceptions
- Resource leaks

**Diagnosis:**
```python
from tools.workflow.file_cache import get_file_cache

cache = get_file_cache()

try:
    results = cache.read_files_parallel(files, max_workers=4)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

**Solutions:**
1. **Too many workers:** Reduce `max_workers`
2. **Resource leak:** Ensure executor.shutdown() is called
3. **File errors:** Check file permissions
4. **Timeout:** Increase timeout or reduce file count

**Prevention:**
- Use try/finally for executor cleanup
- Monitor thread count
- Handle file errors gracefully

---

## 🛠️ **Debugging Tools**

### **Enable Debug Logging:**

```python
import logging

# Enable debug logging for all workflow components
logging.getLogger('tools.workflow').setLevel(logging.DEBUG)
logging.getLogger('tools.workflow.file_cache').setLevel(logging.DEBUG)
logging.getLogger('tools.workflow.performance_optimizer').setLevel(logging.DEBUG)
logging.getLogger('tools.workflow.optimized_consolidation').setLevel(logging.DEBUG)
logging.getLogger('tools.workflow.performance_metrics').setLevel(logging.DEBUG)
```

### **Performance Profiling:**

```python
import cProfile
import pstats
from tools.workflow.file_cache import get_file_cache

# Profile file reading
cache = get_file_cache()
profiler = cProfile.Profile()

profiler.enable()
results = cache.read_files_parallel(files, max_workers=4)
profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### **Memory Profiling:**

```python
from memory_profiler import profile

@profile
def test_workflow():
    from tools.workflow.file_cache import get_file_cache
    cache = get_file_cache()
    results = cache.read_files_parallel(files, max_workers=4)
    return results

test_workflow()
```

### **Cache Inspection:**

```python
from tools.workflow.file_cache import get_file_cache

cache = get_file_cache()

# Inspect cache contents
print(f"Cache keys: {list(cache._cache.keys())}")
print(f"Cache size: {len(cache._cache)}")

# Inspect specific entry
for key, value in cache._cache.items():
    print(f"Key: {key}")
    print(f"File: {value['file_path']}")
    print(f"Size: {len(value['content'])} bytes")
    print(f"Mtime: {value['mtime']}")
    print("---")
```

---

## 📞 **Getting Help**

If you're still experiencing issues:

1. **Check logs:** Review debug logs for errors
2. **Run diagnostics:** Use debugging tools above
3. **Collect metrics:** Gather performance statistics
4. **Create issue:** File GitHub issue with:
   - Symptoms
   - Diagnosis results
   - Logs
   - Metrics
   - Steps to reproduce

---

**Status:** ✅ **PRODUCTION READY**

**Version:** 1.0

**Last Updated:** 2025-10-18

