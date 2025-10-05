"""
Supabase client for test validation suite

Provides connection and helper methods for storing test results,
watcher observations, and issue tracking in Supabase.

Dual Storage Strategy:
- JSON files: Immediate debugging, git history, offline access
- Supabase: Historical tracking, trend analysis, querying
"""

import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv("tool_validation_suite/.env.testing")
load_dotenv(".env.testing")
load_dotenv(".env")

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Client for interacting with Supabase test validation database.
    
    Features:
    - Automatic connection management
    - Helper methods for CRUD operations
    - Error handling and logging
    - Optional operation (graceful degradation if Supabase unavailable)
    """
    
    def __init__(self):
        """Initialize Supabase client."""
        self.project_id = os.getenv("SUPABASE_PROJECT_ID", "mxaazuhlqewmkweewyaz")
        self.enabled = os.getenv("SUPABASE_TRACKING_ENABLED", "true").lower() == "true"
        
        if not self.enabled:
            logger.info("Supabase tracking disabled")
            return
        
        try:
            # Import supabase-mcp-full tools
            # Note: These are MCP tools, not a Python SDK
            # We'll use execute_sql for direct database operations
            logger.info(f"Supabase tracking enabled for project: {self.project_id}")
        except Exception as e:
            logger.warning(f"Supabase initialization failed: {e}. Continuing without Supabase tracking.")
            self.enabled = False
    
    def _execute_sql(self, query: str, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Execute SQL query using Supabase MCP tool.
        
        Args:
            query: SQL query to execute
            params: Optional parameters for parameterized queries
            
        Returns:
            Query results or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            # For now, we'll use simple string formatting
            # In production, use proper parameterized queries
            from supabase_mcp_full import execute_sql_supabase_mcp_full
            
            result = execute_sql_supabase_mcp_full(
                project_id=self.project_id,
                query=query
            )
            return result
        except Exception as e:
            logger.error(f"Supabase SQL execution failed: {e}")
            return None
    
    # ========== Test Runs ==========
    
    def create_test_run(
        self,
        branch_name: str,
        commit_hash: Optional[str],
        watcher_model: str,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new test run record.
        
        Args:
            branch_name: Git branch name
            commit_hash: Git commit hash
            watcher_model: Watcher model used (e.g., "glm-4.5-air")
            notes: Optional notes about this run
            
        Returns:
            Test run ID or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            query = f"""
            INSERT INTO test_runs (branch_name, commit_hash, watcher_model, notes)
            VALUES ('{branch_name}', '{commit_hash or ""}', '{watcher_model}', '{notes or ""}')
            RETURNING id;
            """
            
            from supabase_mcp_full import execute_sql_supabase_mcp_full
            result = execute_sql_supabase_mcp_full(
                project_id=self.project_id,
                query=query
            )
            
            if result and len(result) > 0:
                run_id = result[0].get('id')
                logger.info(f"Created test run: {run_id}")
                return run_id
            return None
        except Exception as e:
            logger.error(f"Failed to create test run: {e}")
            return None
    
    def update_test_run(
        self,
        run_id: int,
        total_tests: int,
        tests_passed: int,
        tests_failed: int,
        tests_skipped: int,
        pass_rate: float,
        avg_watcher_quality: Optional[float],
        total_duration_secs: Optional[int],
        total_cost_usd: Optional[float]
    ) -> bool:
        """
        Update test run with final statistics.
        
        Args:
            run_id: Test run ID
            total_tests: Total number of tests
            tests_passed: Number of passed tests
            tests_failed: Number of failed tests
            tests_skipped: Number of skipped tests
            pass_rate: Pass rate percentage
            avg_watcher_quality: Average watcher quality score
            total_duration_secs: Total duration in seconds
            total_cost_usd: Total cost in USD
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not run_id:
            return False
        
        try:
            query = f"""
            UPDATE test_runs
            SET total_tests = {total_tests},
                tests_passed = {tests_passed},
                tests_failed = {tests_failed},
                tests_skipped = {tests_skipped},
                pass_rate = {pass_rate},
                avg_watcher_quality = {avg_watcher_quality or 'NULL'},
                total_duration_secs = {total_duration_secs or 'NULL'},
                total_cost_usd = {total_cost_usd or 'NULL'}
            WHERE id = {run_id};
            """
            
            from supabase_mcp_full import execute_sql_supabase_mcp_full
            execute_sql_supabase_mcp_full(
                project_id=self.project_id,
                query=query
            )
            
            logger.info(f"Updated test run: {run_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update test run: {e}")
            return False
    
    # ========== Test Results ==========
    
    def insert_test_result(
        self,
        run_id: int,
        tool_name: str,
        variation: str,
        provider: str,
        model: str,
        status: str,
        execution_status: Optional[str],
        duration_secs: Optional[float],
        memory_mb: Optional[int],
        cpu_percent: Optional[float],
        tokens_total: Optional[int],
        cost_usd: Optional[float],
        watcher_quality: Optional[int],
        error_message: Optional[str],
        test_input: Optional[Dict],
        test_output: Optional[Dict]
    ) -> Optional[int]:
        """
        Insert a test result record.
        
        Returns:
            Test result ID or None if failed
        """
        if not self.enabled or not run_id:
            return None
        
        try:
            import json
            
            # Escape single quotes in strings
            def escape_str(s):
                if s is None:
                    return 'NULL'
                return f"'{str(s).replace(chr(39), chr(39)+chr(39))}'"
            
            test_input_json = 'NULL' if not test_input else f"'{json.dumps(test_input)}'::jsonb"
            test_output_json = 'NULL' if not test_output else f"'{json.dumps(test_output)}'::jsonb"
            
            query = f"""
            INSERT INTO test_results (
                run_id, tool_name, variation, provider, model, status,
                execution_status, duration_secs, memory_mb, cpu_percent,
                tokens_total, cost_usd, watcher_quality, error_message,
                test_input, test_output
            )
            VALUES (
                {run_id}, '{tool_name}', '{variation}', '{provider}', '{model}', '{status}',
                {escape_str(execution_status)}, {duration_secs or 'NULL'}, {memory_mb or 'NULL'}, {cpu_percent or 'NULL'},
                {tokens_total or 'NULL'}, {cost_usd or 'NULL'}, {watcher_quality or 'NULL'}, {escape_str(error_message)},
                {test_input_json}, {test_output_json}
            )
            RETURNING id;
            """
            
            from supabase_mcp_full import execute_sql_supabase_mcp_full
            result = execute_sql_supabase_mcp_full(
                project_id=self.project_id,
                query=query
            )
            
            if result and len(result) > 0:
                test_result_id = result[0].get('id')
                logger.debug(f"Inserted test result: {test_result_id}")
                return test_result_id
            return None
        except Exception as e:
            logger.error(f"Failed to insert test result: {e}")
            return None
    
    # ========== Watcher Insights ==========
    
    def insert_watcher_insight(
        self,
        test_result_id: int,
        quality_score: int,
        strengths: List[str],
        weaknesses: List[str],
        anomalies: List[str],
        recommendations: List[str],
        confidence_level: str,
        raw_observation: Dict
    ) -> Optional[int]:
        """
        Insert a watcher insight record.
        
        Returns:
            Watcher insight ID or None if failed
        """
        if not self.enabled or not test_result_id:
            return None
        
        try:
            import json
            
            # Convert lists to PostgreSQL arrays
            def to_pg_array(lst):
                if not lst:
                    return 'ARRAY[]::text[]'
                escaped = [s.replace("'", "''") for s in lst]
                return f"ARRAY[{', '.join([f\"'{s}'\" for s in escaped])}]"
            
            query = f"""
            INSERT INTO watcher_insights (
                test_result_id, quality_score, strengths, weaknesses,
                anomalies, recommendations, confidence_level, raw_observation
            )
            VALUES (
                {test_result_id}, {quality_score}, {to_pg_array(strengths)}, {to_pg_array(weaknesses)},
                {to_pg_array(anomalies)}, {to_pg_array(recommendations)}, '{confidence_level}',
                '{json.dumps(raw_observation)}'::jsonb
            )
            RETURNING id;
            """
            
            from supabase_mcp_full import execute_sql_supabase_mcp_full
            result = execute_sql_supabase_mcp_full(
                project_id=self.project_id,
                query=query
            )
            
            if result and len(result) > 0:
                insight_id = result[0].get('id')
                logger.debug(f"Inserted watcher insight: {insight_id}")
                return insight_id
            return None
        except Exception as e:
            logger.error(f"Failed to insert watcher insight: {e}")
            return None


# Singleton instance
_supabase_client = None

def get_supabase_client() -> SupabaseClient:
    """Get singleton Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client

