"""
Phase 2.2.6: Load Testing for Concurrent Request Handling

Tests the session manager under realistic load conditions:
- 50+ concurrent requests
- Real API calls (mocked for testing)
- Performance metrics collection
- Graceful shutdown under load
- No hanging or deadlocks

Created: 2025-10-21
Phase: 2.2.6 - Load Testing
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from src.utils.concurrent_session_manager import (
    ConcurrentSessionManager,
    get_session_manager,
    SessionState
)


class TestLoadTesting:
    """Load testing for concurrent session management."""
    
    def test_50_concurrent_sessions(self):
        """Test 50 concurrent session creations and completions."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=200)
        num_sessions = 50
        results = []
        
        def create_and_complete_session(index: int) -> Dict[str, Any]:
            """Create, use, and complete a session."""
            start_time = time.time()
            
            try:
                # Create session
                session = manager.create_session(
                    provider="test",
                    model=f"model-{index}",
                    test_data=f"data-{index}"
                )
                
                # Simulate work
                session.start()
                time.sleep(0.01)  # 10ms simulated work
                session.complete(result=f"result-{index}")
                
                # Release session
                manager.release_session(session.request_id)
                
                duration = time.time() - start_time
                return {
                    'success': True,
                    'duration': duration,
                    'index': index
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'index': index
                }
        
        # Execute concurrently
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(create_and_complete_session, i) for i in range(num_sessions)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all succeeded
        successes = [r for r in results if r['success']]
        failures = [r for r in results if not r['success']]
        
        assert len(successes) == num_sessions, f"Expected {num_sessions} successes, got {len(successes)}"
        assert len(failures) == 0, f"Unexpected failures: {failures}"
        
        # Check performance
        durations = [r['duration'] for r in successes]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        
        print(f"\n50 Concurrent Sessions Performance:")
        print(f"  Average duration: {avg_duration*1000:.2f}ms")
        print(f"  Max duration: {max_duration*1000:.2f}ms")
        print(f"  Min duration: {min(durations)*1000:.2f}ms")
        
        # Verify metrics
        stats = manager.get_statistics()
        assert stats['lifetime_total_created'] == num_sessions
        assert stats['lifetime_total_completed'] == num_sessions
        assert stats['active_sessions'] == 0
    
    def test_100_concurrent_sessions(self):
        """Test 100 concurrent sessions to stress test capacity."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=200)
        num_sessions = 100
        
        def create_session_only(index: int) -> bool:
            """Create session without completing (to test capacity)."""
            try:
                manager.create_session(
                    provider="test",
                    model=f"model-{index}",
                    data=f"data-{index}"
                )
                return True
            except Exception:
                return False
        
        # Create all sessions concurrently
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(create_session_only, i) for i in range(num_sessions)]
            results = [future.result() for future in as_completed(futures)]
        
        # All should succeed (within 200 limit)
        assert sum(results) == num_sessions
        
        # Verify capacity tracking
        stats = manager.get_statistics()
        assert stats['active_sessions'] == num_sessions
        assert stats['peak_concurrent_sessions'] == num_sessions
    
    def test_capacity_limit_enforcement_under_load(self):
        """Test that capacity limits are enforced under concurrent load."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=50)
        
        # Create 50 sessions (at limit)
        sessions = []
        for i in range(50):
            session = manager.create_session(provider="test", model=f"model-{i}")
            sessions.append(session)
        
        # Try to create more concurrently
        def try_create_session(index: int) -> bool:
            """Try to create session, return True if rejected."""
            try:
                manager.create_session(provider="test", model=f"overflow-{index}")
                return False  # Should not succeed
            except RuntimeError as e:
                if "Maximum concurrent sessions" in str(e):
                    return True  # Correctly rejected
                raise
        
        # Try 10 concurrent overflow attempts
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(try_create_session, i) for i in range(10)]
            rejections = [future.result() for future in as_completed(futures)]
        
        # All should be rejected
        assert sum(rejections) == 10
        
        # Verify rejection metrics
        stats = manager.get_statistics()
        assert stats['sessions_rejected_capacity'] == 10
    
    def test_no_hanging_with_concurrent_requests(self):
        """Verify concurrent requests don't hang or deadlock."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=200)
        num_requests = 75
        timeout_seconds = 10.0  # If test takes longer, something is hanging
        
        def process_request(index: int) -> float:
            """Process a complete request and return duration."""
            start = time.time()
            session = manager.create_session(provider="test", model=f"model-{index}")
            session.start()
            time.sleep(0.005)  # 5ms work
            session.complete(result=f"result-{index}")
            manager.release_session(session.request_id)
            return time.time() - start
        
        start_time = time.time()
        
        # Execute all requests concurrently
        with ThreadPoolExecutor(max_workers=75) as executor:
            futures = [executor.submit(process_request, i) for i in range(num_requests)]
            durations = [future.result(timeout=timeout_seconds) for future in as_completed(futures)]
        
        total_duration = time.time() - start_time
        
        # Verify no hanging (should complete well under timeout)
        assert total_duration < timeout_seconds, f"Test took {total_duration}s, possible hanging"
        
        # Verify all completed
        assert len(durations) == num_requests
        
        print(f"\n75 Concurrent Requests (No Hanging Test):")
        print(f"  Total duration: {total_duration:.2f}s")
        print(f"  Average per request: {sum(durations)/len(durations)*1000:.2f}ms")
    
    def test_graceful_shutdown_under_load(self):
        """Test graceful shutdown with active sessions."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=200)
        
        # Create 20 active sessions
        sessions = []
        for i in range(20):
            session = manager.create_session(provider="test", model=f"model-{i}")
            session.start()
            sessions.append(session)
        
        # Start shutdown in background
        shutdown_stats = {}
        def shutdown_thread():
            nonlocal shutdown_stats
            shutdown_stats.update(manager.shutdown(timeout_seconds=5.0))
        
        thread = threading.Thread(target=shutdown_thread)
        thread.start()
        
        # Complete sessions gradually
        for i, session in enumerate(sessions):
            time.sleep(0.1)  # Stagger completions
            session.complete(result=f"result-{i}")
        
        # Wait for shutdown to complete
        thread.join(timeout=10.0)
        
        # Verify shutdown stats
        assert shutdown_stats['initial_active_sessions'] == 20
        assert shutdown_stats['final_active_sessions'] == 0
        assert not shutdown_stats['timeout_reached']
        assert shutdown_stats['sessions_completed_during_shutdown'] == 20
    
    def test_metrics_accuracy_under_load(self):
        """Verify metrics remain accurate under concurrent load."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=200)
        num_sessions = 60
        
        # Create sessions with different outcomes
        def create_session_with_outcome(index: int) -> str:
            """Create session with predetermined outcome."""
            session = manager.create_session(provider="test", model=f"model-{index}")
            session.start()
            
            # Vary outcomes: 70% success, 20% error, 10% timeout
            if index % 10 == 0:
                session.timeout()
                outcome = 'timeout'
            elif index % 5 == 0:
                session.fail(error="test error")
                outcome = 'error'
            else:
                session.complete(result="success")
                outcome = 'success'
            
            manager.release_session(session.request_id)
            return outcome
        
        # Execute concurrently
        with ThreadPoolExecutor(max_workers=60) as executor:
            futures = [executor.submit(create_session_with_outcome, i) for i in range(num_sessions)]
            outcomes = [future.result() for future in as_completed(futures)]
        
        # Count expected outcomes
        expected_success = sum(1 for o in outcomes if o == 'success')
        expected_error = sum(1 for o in outcomes if o == 'error')
        expected_timeout = sum(1 for o in outcomes if o == 'timeout')
        
        # Verify metrics match
        metrics = manager.get_metrics()
        assert metrics['lifetime_total_created'] == num_sessions
        assert metrics['lifetime_total_completed'] == expected_success
        assert metrics['lifetime_total_error'] == expected_error
        assert metrics['lifetime_total_timeout'] == expected_timeout
        
        # Verify rates
        total_completed = expected_success + expected_error + expected_timeout
        expected_success_rate = expected_success / total_completed
        assert abs(metrics['success_rate'] - expected_success_rate) < 0.01
    
    def test_metadata_tracking_under_load(self):
        """Verify metadata byte tracking remains accurate under load."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=200)
        
        # Create 30 sessions with varying metadata sizes
        sessions = []
        for i in range(30):
            session = manager.create_session(
                provider="test",
                model=f"model-{i}",
                data="x" * (i * 100)  # Varying sizes
            )
            sessions.append(session)
        
        # Check metadata bytes increased
        stats = manager.get_statistics()
        initial_bytes = stats['current_metadata_bytes']
        assert initial_bytes > 0
        
        # Release half the sessions
        for i in range(15):
            manager.release_session(sessions[i].request_id)
        
        # Check metadata bytes decreased
        stats = manager.get_statistics()
        mid_bytes = stats['current_metadata_bytes']
        assert mid_bytes < initial_bytes
        assert mid_bytes > 0  # Still have 15 sessions
        
        # Release remaining sessions
        for i in range(15, 30):
            manager.release_session(sessions[i].request_id)
        
        # Check metadata bytes at zero
        stats = manager.get_statistics()
        final_bytes = stats['current_metadata_bytes']
        assert final_bytes == 0
    
    def test_performance_baseline(self):
        """Establish performance baseline for future comparison."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=200)
        num_iterations = 100
        
        # Measure session creation time
        creation_times = []
        for i in range(num_iterations):
            start = time.time()
            session = manager.create_session(provider="test", model=f"model-{i}")
            creation_times.append(time.time() - start)
            manager.release_session(session.request_id)
        
        avg_creation = sum(creation_times) / len(creation_times)
        max_creation = max(creation_times)
        
        print(f"\nPerformance Baseline (100 iterations):")
        print(f"  Average session creation: {avg_creation*1000:.3f}ms")
        print(f"  Max session creation: {max_creation*1000:.3f}ms")
        print(f"  Min session creation: {min(creation_times)*1000:.3f}ms")
        
        # Baseline expectations (should be fast)
        assert avg_creation < 0.01, f"Average creation time {avg_creation}s exceeds 10ms baseline"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

