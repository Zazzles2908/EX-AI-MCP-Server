"""
Integration tests for Day 3 optimizations.

Tests that all optimizations work together correctly:
- File caching + parallel reading
- Path caching + file reading
- Optimized consolidation + metrics
- Error handling and edge cases
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.workflow.file_cache import get_file_cache, reset_file_cache
from tools.workflow.performance_optimizer import get_performance_optimizer, reset_performance_optimizer
from tools.workflow.optimized_consolidation import get_optimized_consolidator, reset_optimized_consolidator
from tools.workflow.performance_metrics import get_performance_metrics, reset_performance_metrics


def test_file_cache_and_parallel_reading():
    """Test that file caching works with parallel reading."""
    print("\n[TEST 1] File Cache + Parallel Reading Integration")
    
    # Create test files
    temp_dir = tempfile.mkdtemp()
    files = []
    for i in range(10):
        file_path = os.path.join(temp_dir, f"test_{i}.txt")
        with open(file_path, 'w') as f:
            f.write(f"Content {i}")
        files.append(file_path)
    
    try:
        reset_file_cache()
        cache = get_file_cache()
        
        # First read: parallel (should populate cache)
        results1 = cache.read_files_parallel(files, max_workers=4)
        assert len(results1) == 10, "Should read all 10 files"
        
        # Second read: should hit cache
        results2 = cache.read_files_parallel(files, max_workers=4)
        assert results1 == results2, "Results should be identical"
        
        # Check cache stats
        stats = cache.get_stats()
        assert stats['hits'] > 0, "Should have cache hits on second read"
        assert stats['hit_rate'] > 0.5, "Hit rate should be >50%"
        
        print(f"  ✅ PASS - Cache hit rate: {stats['hit_rate']:.1%}")
        return True
    
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
        return False
    
    finally:
        # Cleanup
        for file_path in files:
            try:
                os.remove(file_path)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass


def test_path_cache_with_file_reading():
    """Test that path caching works with file reading."""
    print("\n[TEST 2] Path Cache + File Reading Integration")
    
    # Create test files
    temp_dir = tempfile.mkdtemp()
    files = []
    for i in range(5):
        file_path = os.path.join(temp_dir, f"test_{i}.txt")
        with open(file_path, 'w') as f:
            f.write(f"Content {i}")
        files.append(file_path)
    
    try:
        reset_performance_optimizer()
        reset_file_cache()
        
        optimizer = get_performance_optimizer()
        cache = get_file_cache()
        
        # Validate paths and read files
        for file_path in files:
            # Path validation should be cached
            assert optimizer.is_valid_path(file_path), f"Path should be valid: {file_path}"
            # File reading should be cached
            content = cache.read_file(file_path)
            assert content, "Should read content"
        
        # Second iteration: should hit both caches
        for file_path in files:
            assert optimizer.is_valid_path(file_path), f"Path should be valid: {file_path}"
            content = cache.read_file(file_path)
            assert content, "Should read content"
        
        # Check stats
        path_stats = optimizer.get_stats()
        file_stats = cache.get_stats()
        
        assert path_stats['path_cache_hit_rate'] > 0, "Should have path cache hits"
        assert file_stats['hit_rate'] > 0, "Should have file cache hits"
        
        print(f"  ✅ PASS - Path cache: {path_stats['path_cache_hit_rate']:.1%}, File cache: {file_stats['hit_rate']:.1%}")
        return True
    
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
        return False
    
    finally:
        # Cleanup
        for file_path in files:
            try:
                os.remove(file_path)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass


def test_consolidation_with_metrics():
    """Test that optimized consolidation works with performance metrics."""
    print("\n[TEST 3] Optimized Consolidation + Performance Metrics")
    
    try:
        reset_optimized_consolidator()
        reset_performance_metrics()
        
        consolidator = get_optimized_consolidator()
        metrics = get_performance_metrics()
        
        # Start workflow
        metrics.start_workflow()
        
        # Add steps with metrics tracking
        for step in range(1, 6):
            metrics.start_step(step)
            
            consolidator.add_step(
                step_number=step,
                findings=f"Findings for step {step}",
                confidence="medium"
            )
            
            # Get consolidated text
            consolidated = consolidator.get_consolidated_text()
            assert consolidated, "Should have consolidated text"
            
            metrics.end_step(step)
        
        # End workflow
        total_time = metrics.end_workflow()
        
        # Check consolidation stats
        cons_stats = consolidator.get_stats()
        assert cons_stats['total_steps'] == 5, "Should have 5 steps"
        assert cons_stats['incremental_consolidations'] > 0, "Should have incremental consolidations"
        
        # Check metrics stats
        metrics_summary = metrics.get_summary()
        assert metrics_summary['total_steps'] == 5, "Should have tracked 5 steps"
        assert total_time > 0, "Should have positive workflow time"
        
        print(f"  ✅ PASS - Incremental consolidations: {cons_stats['incremental_consolidations']}, Total time: {total_time:.3f}s")
        return True
    
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
        return False


def test_error_handling_large_files():
    """Test error handling for large files."""
    print("\n[TEST 4] Error Handling - Large Files")
    
    # Create a large file (>10MB)
    temp_dir = tempfile.mkdtemp()
    large_file = os.path.join(temp_dir, "large_file.txt")
    
    try:
        # Create 15MB file
        with open(large_file, 'w') as f:
            f.write("x" * (15 * 1024 * 1024))
        
        reset_file_cache()
        cache = get_file_cache()
        
        # Try to read large file (should skip cache but still read)
        content = cache.read_file(large_file)
        assert content, "Should still read large file"
        
        # Check that it was skipped from cache
        stats = cache.get_stats()
        assert stats['files_skipped'] > 0, "Should have skipped large file from cache"
        
        print(f"  ✅ PASS - Large file handled correctly (skipped from cache)")
        return True
    
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
        return False
    
    finally:
        # Cleanup
        try:
            os.remove(large_file)
            os.rmdir(temp_dir)
        except:
            pass


def test_error_handling_missing_files():
    """Test error handling for missing files."""
    print("\n[TEST 5] Error Handling - Missing Files")
    
    try:
        reset_file_cache()
        reset_performance_optimizer()
        
        cache = get_file_cache()
        optimizer = get_performance_optimizer()
        
        missing_file = "/nonexistent/path/to/file.txt"
        
        # Path validation should return False
        assert not optimizer.is_valid_path(missing_file), "Should detect missing file"
        
        # File reading should raise exception
        try:
            cache.read_file(missing_file)
            print(f"  ❌ FAIL - Should have raised exception for missing file")
            return False
        except Exception:
            # Expected behavior
            pass
        
        print(f"  ✅ PASS - Missing files handled correctly")
        return True
    
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
        return False


def test_cache_invalidation():
    """Test that cache invalidation works correctly."""
    print("\n[TEST 6] Cache Invalidation on File Modification")
    
    # Create test file
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.txt")
    
    try:
        # Write initial content
        with open(test_file, 'w') as f:
            f.write("Initial content")
        
        reset_file_cache()
        cache = get_file_cache()
        
        # Read file (should cache)
        content1 = cache.read_file(test_file)
        assert content1 == "Initial content", "Should read initial content"
        
        # Modify file
        import time
        time.sleep(0.1)  # Ensure mtime changes
        with open(test_file, 'w') as f:
            f.write("Modified content")
        
        # Read again (should detect modification and re-read)
        content2 = cache.read_file(test_file)
        assert content2 == "Modified content", "Should read modified content"
        assert content1 != content2, "Content should be different"
        
        print(f"  ✅ PASS - Cache invalidation works correctly")
        return True
    
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
        return False
    
    finally:
        # Cleanup
        try:
            os.remove(test_file)
            os.rmdir(temp_dir)
        except:
            pass


def test_all_optimizations_together():
    """Test all optimizations working together in a realistic workflow."""
    print("\n[TEST 7] All Optimizations Together (Realistic Workflow)")
    
    # Create test files
    temp_dir = tempfile.mkdtemp()
    files = []
    for i in range(20):
        file_path = os.path.join(temp_dir, f"test_{i}.txt")
        with open(file_path, 'w') as f:
            f.write(f"Content for file {i}\n" * 100)
        files.append(file_path)
    
    try:
        # Reset all components
        reset_file_cache()
        reset_performance_optimizer()
        reset_optimized_consolidator()
        reset_performance_metrics()
        
        # Get all components
        cache = get_file_cache()
        optimizer = get_performance_optimizer()
        consolidator = get_optimized_consolidator()
        metrics = get_performance_metrics()
        
        # Start workflow
        metrics.start_workflow()
        
        # Simulate multi-step workflow
        for step in range(1, 6):
            metrics.start_step(step)
            
            # Validate paths (with caching)
            valid_files = [f for f in files if optimizer.is_valid_path(f)]
            assert len(valid_files) == 20, "All files should be valid"
            
            # Read files in parallel (with caching)
            contents = cache.read_files_parallel(valid_files[:10], max_workers=4)
            assert len(contents) == 10, "Should read 10 files"
            
            # Add findings to consolidation
            consolidator.add_step(
                step_number=step,
                findings=f"Step {step}: Analyzed {len(contents)} files",
                files_checked=valid_files[:10],
                relevant_files=valid_files[:5],
                confidence="medium"
            )
            
            # Get consolidated findings
            consolidated = consolidator.get_consolidated_text()
            assert consolidated, "Should have consolidated text"
            
            metrics.end_step(step)
        
        # End workflow
        total_time = metrics.end_workflow()
        
        # Verify all components worked
        cache_stats = cache.get_stats()
        path_stats = optimizer.get_stats()
        cons_stats = consolidator.get_stats()
        metrics_summary = metrics.get_summary()
        
        assert cache_stats['hit_rate'] > 0, "Should have cache hits"
        assert path_stats['path_cache_hit_rate'] > 0, "Should have path cache hits"
        assert cons_stats['incremental_consolidations'] > 0, "Should have incremental consolidations"
        assert metrics_summary['total_steps'] == 5, "Should have tracked 5 steps"
        
        print(f"  ✅ PASS - All optimizations working together")
        print(f"    - File cache hit rate: {cache_stats['hit_rate']:.1%}")
        print(f"    - Path cache hit rate: {path_stats['path_cache_hit_rate']:.1%}")
        print(f"    - Incremental consolidations: {cons_stats['incremental_consolidations']}")
        print(f"    - Total workflow time: {total_time:.3f}s")
        return True
    
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for file_path in files:
            try:
                os.remove(file_path)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass


def run_all_integration_tests():
    """Run all integration tests."""
    print("\n" + "="*80)
    print("INTEGRATION TESTS - DAY 3 OPTIMIZATIONS")
    print("="*80)
    
    tests = [
        test_file_cache_and_parallel_reading,
        test_path_cache_with_file_reading,
        test_consolidation_with_metrics,
        test_error_handling_large_files,
        test_error_handling_missing_files,
        test_cache_invalidation,
        test_all_optimizations_together,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ EXCEPTION - {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Print summary
    print("\n" + "="*80)
    passed = sum(results)
    total = len(results)
    print(f"INTEGRATION TEST SUMMARY: {passed}/{total} tests passed")
    print("="*80 + "\n")
    
    return all(results)


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)

