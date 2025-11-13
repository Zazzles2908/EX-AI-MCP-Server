#!/usr/bin/env python3
"""
Apply Database Migrations using Supabase Python Client
Uses direct SQL execution via HTTP API
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import List, Tuple

# Configuration
PROJECT_REF = "mxaazuhlqewmkweewyaz"
API_BASE = f"https://api.supabase.com/v1/projects/{PROJECT_REF}"
ACCESS_TOKEN = os.getenv('SUPABASE_ACCESS_TOKEN')

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def print_header(text: str):
    print(f"\n{BOLD}{BLUE}{'=' * 80}{END}")
    print(f"{BOLD}{BLUE}{text:^80}{END}")
    print(f"{BOLD}{BLUE}{'=' * 80}{END}\n")

def print_success(text: str):
    print(f"{GREEN}[OK] {text}{END}")

def print_error(text: str):
    print(f"{RED}[ERROR] {text}{END}")

def print_warning(text: str):
    print(f"{YELLOW}[WARNING] {text}{END}")

def print_info(text: str):
    print(f"{BLUE}[INFO] {text}{END}")

def execute_sql(sql: str, description: str) -> bool:
    """Execute SQL using Supabase Management API."""
    url = f"{API_BASE}/database/query"
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {'query': sql}

    try:
        print_info(f"Executing: {description}")
        response = requests.post(url, headers=headers, json=data, timeout=60)

        if response.status_code in [200, 201]:
            print_success(f"Success: {description}")
            return True
        else:
            print_error(f"Failed: {description}")
            print(f"  Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {json.dumps(error_data, indent=2)[:500]}")
            except:
                print(f"  Response: {response.text[:500]}")
            return False
    except requests.exceptions.Timeout:
        print_error(f"Timeout: {description}")
        return False
    except Exception as e:
        print_error(f"Exception: {description}")
        print(f"  Error: {str(e)[:500]}")
        return False

def load_migration(filepath: Path) -> str:
    """Load migration file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print_header("EX-AI MCP Server - Database Migration Deployment")
    print_info(f"Project: {PROJECT_REF}")
    print_info(f"API: {API_BASE}")

    if not ACCESS_TOKEN:
        print_error("SUPABASE_ACCESS_TOKEN not set!")
        sys.exit(1)

    print_success(f"Access token configured")

    # Migration files in order
    migrations = [
        ('src/database/migrations/001_user_quotas.sql', 'User Quotas Table'),
        ('database/migrations/20251109_add_missing_tables.sql', 'Missing Tables (3 tables)'),
        ('database/migrations/20251109_create_core_tables.sql', 'Core Tables (file_operations, file_metadata)'),
        ('database/migrations/20251109_add_performance_indexes.sql', 'Performance Indexes (20 indexes)'),
        ('database/migrations/20251109_create_rls_and_storage.sql', 'RLS Policies & Storage Buckets'),
    ]

    print_header("APPLYING MIGRATIONS")

    success_count = 0
    failed_count = 0

    for filepath, description in migrations:
        path = Path(filepath)

        if not path.exists():
            print_error(f"File not found: {filepath}")
            failed_count += 1
            continue

        try:
            sql = load_migration(path)
            if execute_sql(sql, f"{description} ({path.name})"):
                success_count += 1
            else:
                failed_count += 1
                print_warning("Continuing with next migration...")

        except Exception as e:
            print_error(f"Error loading {filepath}: {str(e)}")
            failed_count += 1

    # Summary
    print_header("DEPLOYMENT SUMMARY")
    print(f"{BOLD}Successful: {GREEN}{success_count}{END}")
    print(f"{BOLD}Failed: {RED}{failed_count}{END}")
    print(f"{BOLD}Total: {BLUE}{len(migrations)}{END}")

    if failed_count == 0:
        print_success("All migrations applied successfully!")
        print_header("DEPLOYMENT COMPLETE!")
        print_info("The database is now fully configured.")
        print_info("You can verify with:")
        print("  - supabase projects list-tables")
        print("  - Check RLS policies")
        print("  - Test file upload functionality")
    else:
        print_error(f"{failed_count} migration(s) failed!")
        print_warning("Check errors above and retry manually.")

    print("=" * 80)

if __name__ == '__main__':
    main()
