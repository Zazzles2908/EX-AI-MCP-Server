#!/usr/bin/env python3
"""Update P0-8 issue in Supabase to reflect downgrade to P1"""

import os
from supabase import create_client

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

# Search for P0-8 by title
result = supabase.table('exai_issues_tracker').select('*').ilike('title', '%rate limit%').execute()
print(f'Found {len(result.data)} issues matching "rate limit"')

if result.data:
    for issue in result.data:
        print(f"\nID: {issue['issue_id']}")
        print(f"Title: {issue['title']}")
        print(f"Priority: {issue['priority']}")
        print(f"Status: {issue['status']}")
        
        # Update to P1
        update_result = supabase.table('exai_issues_tracker').update({
            'priority': 'P1',
            'status': 'Root Cause Identified',
            'notes': 'DOWNGRADED FROM P0 TO P1: EXAI consultation (continuation_id: 827fbd32-bc23-4075-aca1-c5c5bb76ba93) recommended deferring rate limiting until LAN deployment phase. Low risk in localhost-only deployment. Rationale: Rate limiting is a production-scale concern, not critical for current development environment.'
        }).eq('issue_id', issue['issue_id']).execute()
        
        print(f"\n✅ Updated to P1 priority")
else:
    print("No issues found matching 'rate limit'")

