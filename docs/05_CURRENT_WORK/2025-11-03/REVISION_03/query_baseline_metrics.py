#!/usr/bin/env python3
"""
Supabase Baseline Metrics Query Script
Date: 2025-11-03
Purpose: Query Supabase to establish baseline metrics before validation testing

This script queries the messages table to find:
1. Last 24 hours of workflow tool calls
2. Count of calls with empty responses
3. Count of expert analysis executions
4. Distribution by tool type
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv('.env.docker')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ ERROR: Supabase credentials not found in .env.docker")
    sys.exit(1)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print("="*80)
print("📊 SUPABASE BASELINE METRICS - VALIDATION PHASE 2")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Calculate 24 hours ago
twenty_four_hours_ago = (datetime.now() - timedelta(hours=24)).isoformat()

# List of workflow tools we're interested in
WORKFLOW_TOOLS = [
    'refactor', 'debug', 'codereview', 'secaudit', 
    'thinkdeep', 'precommit', 'testgen', 'docgen',
    'planner', 'tracer', 'consensus', 'analyze'
]

print("\n" + "="*80)
print("1. TOTAL WORKFLOW TOOL CALLS (Last 24 Hours)")
print("="*80)

try:
    # Query messages for workflow tool calls
    result = supabase.table("messages").select("*").gte(
        "created_at", twenty_four_hours_ago
    ).execute()
    
    total_messages = len(result.data)
    workflow_tool_calls = []
    
    for msg in result.data:
        metadata = msg.get('metadata', {})
        tool_name = metadata.get('tool_name', '')
        
        if tool_name in WORKFLOW_TOOLS:
            workflow_tool_calls.append({
                'tool_name': tool_name,
                'created_at': msg['created_at'],
                'role': msg['role'],
                'metadata': metadata
            })
    
    print(f"Total messages in last 24h: {total_messages}")
    print(f"Workflow tool calls: {len(workflow_tool_calls)}")
    print(f"Unique tools used: {len(set(call['tool_name'] for call in workflow_tool_calls))}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*80)
print("2. DISTRIBUTION BY TOOL TYPE")
print("="*80)

try:
    tool_distribution = {}
    for call in workflow_tool_calls:
        tool_name = call['tool_name']
        tool_distribution[tool_name] = tool_distribution.get(tool_name, 0) + 1
    
    print(f"{'Tool Name':<20} {'Count':<10} {'Percentage':<10}")
    print("-" * 40)
    
    for tool_name in sorted(tool_distribution.keys(), key=lambda x: tool_distribution[x], reverse=True):
        count = tool_distribution[tool_name]
        percentage = (count / len(workflow_tool_calls) * 100) if workflow_tool_calls else 0
        print(f"{tool_name:<20} {count:<10} {percentage:>6.2f}%")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*80)
print("3. EXPERT ANALYSIS EXECUTION CHECK")
print("="*80)

try:
    # Check for expert analysis in responses
    expert_analysis_count = 0
    empty_response_count = 0
    
    for call in workflow_tool_calls:
        if call['role'] == 'assistant':
            content = call.get('metadata', {}).get('content', '')
            metadata = call.get('metadata', {})
            
            # Check if expert analysis was called
            if 'expert_analysis' in str(metadata) or 'expert_analysis' in content:
                expert_analysis_count += 1
            
            # Check for empty responses
            if not content or len(content.strip()) < 50:
                empty_response_count += 1
    
    assistant_responses = len([c for c in workflow_tool_calls if c['role'] == 'assistant'])
    
    print(f"Total assistant responses: {assistant_responses}")
    print(f"Responses with expert analysis: {expert_analysis_count}")
    print(f"Empty/minimal responses: {empty_response_count}")
    
    if assistant_responses > 0:
        expert_percentage = (expert_analysis_count / assistant_responses * 100)
        empty_percentage = (empty_response_count / assistant_responses * 100)
        print(f"Expert analysis rate: {expert_percentage:.2f}%")
        print(f"Empty response rate: {empty_percentage:.2f}%")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*80)
print("4. RECENT WORKFLOW TOOL EXECUTIONS (Last 10)")
print("="*80)

try:
    recent_calls = sorted(workflow_tool_calls, key=lambda x: x['created_at'], reverse=True)[:10]
    
    for i, call in enumerate(recent_calls, 1):
        print(f"\n  Call {i}:")
        print(f"    Tool: {call['tool_name']}")
        print(f"    Time: {call['created_at']}")
        print(f"    Role: {call['role']}")
        
        metadata = call.get('metadata', {})
        if 'model_name' in metadata:
            print(f"    Model: {metadata['model_name']}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*80)
print("5. SUMMARY STATISTICS")
print("="*80)

print(f"""
Baseline Metrics Summary:
- Time Range: Last 24 hours
- Total Workflow Tool Calls: {len(workflow_tool_calls)}
- Unique Tools Used: {len(set(call['tool_name'] for call in workflow_tool_calls))}
- Expert Analysis Calls: {expert_analysis_count}
- Empty Responses: {empty_response_count}

Most Used Tools:
""")

for tool_name in sorted(tool_distribution.keys(), key=lambda x: tool_distribution[x], reverse=True)[:5]:
    count = tool_distribution[tool_name]
    print(f"  - {tool_name}: {count} calls")

print("\n" + "="*80)
print("✅ BASELINE METRICS QUERY COMPLETE")
print("="*80)

