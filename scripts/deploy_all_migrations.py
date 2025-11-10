#!/usr/bin/env python3
"""
EX-AI MCP Server - Automated Database Migration Deployment
Date: 2025-11-09

This script applies all database migrations in the correct order.
Requires: SUPABASE_SERVICE_ROLE_KEY and SUPABASE_URL in environment
"""

import os
import sys
import requests
from pathlib import Path
from typing import List, Dict, Any

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def get_supabase_env() -> Dict[str, str]:
    """Get Supabase environment variables."""
    supabase_url = os.getenv('SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    project_id = os.getenv('SUPABASE_PROJECT_ID')

    if not supabase_url or not service_role_key or not project_id:
        print_error("Missing required environment variables!")
        print(f"  SUPABASE_URL: {'✅' if supabase_url else '❌'}")
        print(f"  SUPABASE_SERVICE_ROLE_KEY: {'✅' if service_role_key else '❌'}")
        print(f"  SUPABASE_PROJECT_ID: {'✅' if project_id else '❌'}")
        print(f"\nPlease set these in your .env.docker file or environment.")
        sys.exit(1)

    return {
        'url': supabase_url,
        'key': service_role_key,
        'project_id': project_id
    }

def execute_sql(env: Dict[str, str], sql: str, description: str) -> bool:
    """Execute SQL using Supabase Management API."""
    url = f"https://api.supabase.com/v1/projects/{env['project_id']}/database/query"
    headers = {
        'Authorization': f"Bearer {env['key']}",
        'Content-Type': 'application/json'
    }
    data = {
        'query': sql
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code in [200, 201]:
            return True
        else:
            print_error(f"Failed to execute: {description}")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False
    except Exception as e:
        print_error(f"Exception during {description}: {str(e)}")
        return False

def load_migration_file(filepath: Path) -> str:
    """Load migration file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print_error(f"Failed to read {filepath}: {str(e)}")
        sys.exit(1)

def apply_migration(env: Dict[str, str], filepath: Path) -> bool:
    """Apply a single migration file."""
    sql = load_migration_file(filepath)
    description = f"{filepath.name}"
    print_info(f"Applying {description}...")

    if execute_sql(env, sql, description):
        print_success(f"Successfully applied: {filepath.name}")
        return True
    else:
        print_error(f"Failed to apply: {filepath.name}")
        return False

def check_table_exists(env: Dict[str, str], table_name: str) -> bool:
    """Check if a table exists."""
    sql = f"""
    SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = '{table_name}'
    );
    """
    url = f"https://api.supabase.com/v1/projects/{env['project_id']}/database/query"
    headers = {
        'Authorization': f"Bearer {env['key']}",
        'Content-Type': 'application/json'
    }
    data = {'query': sql}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result and isinstance(result, list) and len(result) > 0:
                return result[0].get('exists', False)
    except:
        pass
    return False

def verify_deployment(env: Dict[str, str]):
    """Verify that all tables were created."""
    print_header("VERIFICATION - Checking Tables")

    required_tables = [
        'user_quotas',
        'provider_file_uploads',
        'file_id_mappings',
        'audit_logs',
        'file_operations',
        'file_metadata'
    ]

    all_exist = True
    for table in required_tables:
        exists = check_table_exists(env, table)
        status = "✅" if exists else "❌"
        print(f"  {status} {table}")
        all_exist = all_exist and exists

    if all_exist:
        print_success("All required tables verified!")
    else:
        print_error("Some tables are missing!")

    return all_exist

def main():
    print_header("EX-AI MCP Server - Database Migration Deployment")

    # Get environment
    print_info("Loading Supabase configuration...")
    env = get_supabase_env()
    print_success(f"Connected to project: {env['project_id']}")

    # Define migration order
    migrations = [
        ('src/database/migrations/001_user_quotas.sql', 'User Quotas (Existing)'),
        ('database/migrations/20251109_add_missing_tables.sql', 'Missing Tables'),
        ('database/migrations/20251109_create_core_tables.sql', 'Core Tables'),
        ('database/migrations/20251109_add_performance_indexes.sql', 'Performance Indexes'),
        ('database/migrations/20251109_create_rls_and_storage.sql', 'RLS & Storage'),
    ]

    # Check if all migration files exist
    print_header("Checking Migration Files")
    all_files_exist = True
    for filepath, description in migrations:
        path = Path(filepath)
        if path.exists():
            print_success(f"{description}: {filepath}")
        else:
            print_error(f"{description}: {filepath} NOT FOUND")
            all_files_exist = False

    if not all_files_exist:
        print_error("Some migration files are missing!")
        sys.exit(1)

    # Apply migrations
    print_header("Applying Migrations")
    success_count = 0
    failed_count = 0

    for filepath, description in migrations:
        path = Path(filepath)
        if apply_migration(env, path):
            success_count += 1
        else:
            failed_count += 1
            print_warning("Continuing with next migration...")

    # Summary
    print_header("Deployment Summary")
    print(f"{Colors.BOLD}Successful: {Colors.GREEN}{success_count}{Colors.END}")
    print(f"{Colors.BOLD}Failed: {Colors.RED}{failed_count}{Colors.END}")
    print(f"{Colors.BOLD}Total: {Colors.BLUE}{len(migrations)}{Colors.END}")

    if failed_count == 0:
        print_success("All migrations applied successfully!")
        verify_deployment(env)
        print_header("Deployment Complete! 🎉")
        print_success("The database is now fully configured.")
        print_info("You can now start using the EX-AI MCP Server.")
    else:
        print_error(f"Failed to apply {failed_count} migration(s)!")
        print_warning("Please check the errors above and retry.")
        sys.exit(1)

if __name__ == '__main__':
    main()
