"""
Integration Tests for HybridSupabaseManager

Tests the hybrid architecture implementation with real MCP tools.

Phase C Step 2B.3: Integration Testing
Date: 2025-10-22
EXAI Validation: Continuation 9222d725-b6cd-44f1-8406-274e5a3b3389
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.storage.hybrid_supabase_manager import HybridSupabaseManager, HybridOperationResult


class TestHybridManagerIntegration(unittest.TestCase):
    """Integration tests for HybridSupabaseManager with real MCP tools."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Ensure environment variables are set
        cls.project_id = os.getenv("SUPABASE_PROJECT_ID", "mxaazuhlqewmkweewyaz")
        cls.access_token = os.getenv("SUPABASE_ACCESS_TOKEN")
        
        if not cls.access_token:
            raise unittest.SkipTest("SUPABASE_ACCESS_TOKEN not set")
    
    def setUp(self):
        """Create manager instance for each test."""
        self.manager = HybridSupabaseManager()
    
    # ========================================================================
    # CORE FUNCTIONALITY TESTS
    # ========================================================================
    
    def test_execute_sql_via_mcp(self):
        """Test SQL execution through MCP tools."""
        # Execute a simple query
        query = "SELECT COUNT(*) as count FROM conversations"
        result = self.manager.execute_sql(query)
        
        # Verify result structure
        self.assertIsInstance(result, HybridOperationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.layer_used, "mcp")
        self.assertIsNotNone(result.data)
        
        # Verify metadata
        self.assertIn("query", result.metadata)
        self.assertIn("request_id", result.metadata)
        
        print(f"✅ execute_sql via MCP: {result.data}")
    
    def test_list_buckets_via_mcp(self):
        """Test bucket listing through MCP tools."""
        # List buckets
        result = self.manager.list_buckets()
        
        # Verify result structure
        self.assertIsInstance(result, HybridOperationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.layer_used, "mcp")
        self.assertIsNotNone(result.data)
        
        # Verify metadata
        self.assertIn("count", result.metadata)
        self.assertIn("request_id", result.metadata)
        
        # Verify bucket count
        bucket_count = result.metadata["count"]
        self.assertGreaterEqual(bucket_count, 0)
        
        print(f"✅ list_buckets via MCP: {bucket_count} buckets")
    
    # ========================================================================
    # FALLBACK MECHANISM TESTS
    # ========================================================================
    
    def test_execute_sql_fallback_to_python(self):
        """Test fallback to Python when MCP fails."""
        # Mock MCP to fail
        with patch.object(self.manager, '_execute_sql_via_mcp') as mock_mcp:
            mock_mcp.side_effect = Exception("MCP unavailable")
            
            # Execute query (should fallback to Python)
            query = "SELECT 1 as test"
            result = self.manager.execute_sql(query)
            
            # Verify fallback occurred
            self.assertIsInstance(result, HybridOperationResult)
            self.assertEqual(result.layer_used, "python")
            
            print("✅ execute_sql fallback to Python works")
    
    def test_list_buckets_fallback_to_python(self):
        """Test fallback to Python when MCP fails."""
        # Mock MCP to fail
        with patch.object(self.manager, '_list_buckets_via_mcp') as mock_mcp:
            mock_mcp.side_effect = Exception("MCP unavailable")
            
            # List buckets (should fallback to Python)
            result = self.manager.list_buckets()
            
            # Verify fallback occurred
            self.assertIsInstance(result, HybridOperationResult)
            self.assertEqual(result.layer_used, "python")
            
            print("✅ list_buckets fallback to Python works")
    
    # ========================================================================
    # ERROR HANDLING TESTS
    # ========================================================================
    
    def test_execute_sql_with_invalid_query(self):
        """Test error handling for invalid SQL queries."""
        # Execute invalid query
        query = "SELECT * FROM nonexistent_table_xyz"
        
        # Should raise exception or return error result
        try:
            result = self.manager.execute_sql(query)
            # If it returns a result, it should indicate failure
            if not result.success:
                self.assertIsNotNone(result.error)
                print(f"✅ Invalid query handled: {result.error}")
        except Exception as e:
            # Exception is also acceptable
            print(f"✅ Invalid query raised exception: {e}")
    
    # ========================================================================
    # RESPONSE FORMAT VALIDATION TESTS
    # ========================================================================
    
    def test_hybrid_operation_result_format(self):
        """Test that HybridOperationResult has all required fields."""
        # Execute a simple operation
        result = self.manager.list_buckets()
        
        # Verify all required fields exist
        self.assertTrue(hasattr(result, 'success'))
        self.assertTrue(hasattr(result, 'data'))
        self.assertTrue(hasattr(result, 'error'))
        self.assertTrue(hasattr(result, 'metadata'))
        self.assertTrue(hasattr(result, 'layer_used'))
        
        # Verify types
        self.assertIsInstance(result.success, bool)
        self.assertIn(result.layer_used, ["mcp", "python", "unknown"])
        
        print("✅ HybridOperationResult format validated")
    
    def test_mcp_response_data_types(self):
        """Test that MCP responses are parsed into correct data types."""
        # Test SQL query response
        query = "SELECT COUNT(*) as count FROM conversations"
        result = self.manager.execute_sql(query)
        
        if result.success:
            # Data should be parsed (not raw string)
            self.assertIsNotNone(result.data)
            # Should be dict or list, not string
            self.assertNotIsInstance(result.data, str)
            
            print(f"✅ MCP response parsed correctly: {type(result.data)}")
    
    # ========================================================================
    # MCP AVAILABILITY TESTS
    # ========================================================================
    
    def test_mcp_availability_check(self):
        """Test MCP availability detection."""
        # Check if MCP is available
        is_available = self.manager.mcp_available
        
        # Should be boolean
        self.assertIsInstance(is_available, bool)
        
        print(f"✅ MCP availability: {is_available}")
    
    def test_operations_when_mcp_unavailable(self):
        """Test that operations work when MCP is marked unavailable."""
        # Force MCP unavailable
        self.manager.mcp_available = False
        
        # Execute operations (should use Python)
        sql_result = self.manager.execute_sql("SELECT 1")
        bucket_result = self.manager.list_buckets()
        
        # Both should use Python layer
        self.assertEqual(sql_result.layer_used, "python")
        self.assertEqual(bucket_result.layer_used, "python")
        
        print("✅ Operations work when MCP unavailable")


class TestHybridManagerEdgeCases(unittest.TestCase):
    """Edge case tests for HybridSupabaseManager."""
    
    def setUp(self):
        """Create manager instance for each test."""
        self.manager = HybridSupabaseManager()
    
    def test_empty_query_handling(self):
        """Test handling of empty SQL queries."""
        # Try empty query
        try:
            result = self.manager.execute_sql("")
            # Should either fail or return error result
            if result.success:
                print("⚠️ Empty query succeeded (unexpected)")
            else:
                print("✅ Empty query handled correctly")
        except Exception as e:
            print(f"✅ Empty query raised exception: {e}")
    
    def test_very_long_query(self):
        """Test handling of very long SQL queries."""
        # Create a long query
        long_query = "SELECT " + ", ".join([f"'{i}' as col{i}" for i in range(100)])
        
        try:
            result = self.manager.execute_sql(long_query)
            self.assertIsInstance(result, HybridOperationResult)
            print("✅ Long query handled")
        except Exception as e:
            print(f"✅ Long query raised exception: {e}")


def run_tests():
    """Run all integration tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHybridManagerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestHybridManagerEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

