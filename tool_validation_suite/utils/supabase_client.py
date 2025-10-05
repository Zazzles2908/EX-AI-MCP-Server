"""
Supabase client for test validation suite

Provides connection and helper methods for storing test results,
watcher observations, and issue tracking in Supabase.

Dual Storage Strategy:
- JSON files: Immediate debugging, git history, offline access
- Supabase: Historical tracking, trend analysis, querying

This client uses the official Supabase Python SDK to insert data into
the database. It will gracefully disable itself if Supabase is unavailable
or if SUPABASE_TRACKING_ENABLED=false.
"""

import os
import logging
import json
from typing import Optional, Dict, List, Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv("tool_validation_suite/.env.testing")
load_dotenv(".env.testing")
load_dotenv(".env")

logger = logging.getLogger(__name__)

# Try to import Supabase SDK
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase Python SDK not available. Install with: pip install supabase")


class SupabaseClient:
    """
    Client for Supabase operations using the official Python SDK.

    This client will gracefully disable itself if:
    - SUPABASE_TRACKING_ENABLED=false
    - Supabase SDK not installed
    - Connection fails
    """

    def __init__(self):
        """Initialize Supabase client."""
        self.project_id = os.getenv("SUPABASE_PROJECT_ID", "mxaazuhlqewmkweewyaz")
        self.enabled = os.getenv("SUPABASE_TRACKING_ENABLED", "false").lower() == "true"
        self.client: Optional[Client] = None

        if not self.enabled:
            logger.debug("Supabase tracking disabled (SUPABASE_TRACKING_ENABLED=false)")
            return

        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase SDK not available. Tracking disabled.")
            self.enabled = False
            return

        # Get Supabase URL and key
        supabase_url = f"https://{self.project_id}.supabase.co"
        supabase_key = os.getenv("SUPABASE_ACCESS_TOKEN")

        if not supabase_key:
            logger.warning("SUPABASE_ACCESS_TOKEN not set. Tracking disabled.")
            self.enabled = False
            return

        try:
            self.client = create_client(supabase_url, supabase_key)
            logger.info(f"Supabase client initialized for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.enabled = False
    
    def create_test_run(
        self,
        branch_name: str,
        commit_hash: Optional[str],
        watcher_model: str,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """Create a new test run record."""
        if not self.enabled or not self.client:
            return None

        try:
            data = {
                "branch_name": branch_name,
                "commit_hash": commit_hash or "",
                "watcher_model": watcher_model,
                "notes": notes or ""
            }

            result = self.client.table("test_runs").insert(data).execute()

            if result.data and len(result.data) > 0:
                run_id = result.data[0]["id"]
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
        """Update test run with final statistics."""
        if not self.enabled or not self.client or not run_id:
            return False

        try:
            data = {
                "total_tests": total_tests,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "tests_skipped": tests_skipped,
                "pass_rate": pass_rate,
                "avg_watcher_quality": avg_watcher_quality,
                "total_duration_secs": total_duration_secs,
                "total_cost_usd": total_cost_usd
            }

            self.client.table("test_runs").update(data).eq("id", run_id).execute()
            logger.info(f"Updated test run: {run_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update test run: {e}")
            return False
    
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
        """Insert a test result record."""
        if not self.enabled or not self.client or not run_id:
            return None

        try:
            data = {
                "run_id": run_id,
                "tool_name": tool_name,
                "variation": variation,
                "provider": provider,
                "model": model,
                "status": status,
                "execution_status": execution_status,
                "duration_secs": duration_secs,
                "memory_mb": memory_mb,
                "cpu_percent": cpu_percent,
                "tokens_total": tokens_total,
                "cost_usd": cost_usd,
                "watcher_quality": watcher_quality,
                "error_message": error_message,
                "test_input": test_input,
                "test_output": test_output
            }

            result = self.client.table("test_results").insert(data).execute()

            if result.data and len(result.data) > 0:
                test_result_id = result.data[0]["id"]
                logger.debug(f"Inserted test result: {test_result_id}")
                return test_result_id
            return None
        except Exception as e:
            logger.error(f"Failed to insert test result: {e}")
            return None
    
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
        """Insert a watcher insight record."""
        if not self.enabled or not self.client or not test_result_id:
            return None

        try:
            data = {
                "test_result_id": test_result_id,
                "quality_score": quality_score,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "anomalies": anomalies,
                "recommendations": recommendations,
                "confidence_level": confidence_level,
                "raw_observation": raw_observation
            }

            result = self.client.table("watcher_insights").insert(data).execute()

            if result.data and len(result.data) > 0:
                insight_id = result.data[0]["id"]
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

