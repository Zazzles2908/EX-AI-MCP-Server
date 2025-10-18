#!/usr/bin/env python
"""
Retrieve EXAI conversation from Supabase to verify nothing was missed.
"""
import sys
from pathlib import Path

# Add project root to path
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env
load_env()

from src.storage.supabase_client import get_storage_manager
import json

def retrieve_conversation(continuation_id: str):
    """Retrieve full conversation from Supabase"""
    print(f"\n{'='*80}")
    print(f"RETRIEVING EXAI CONVERSATION: {continuation_id}")
    print(f"{'='*80}\n")
    
    manager = get_storage_manager()
    
    if not manager.enabled:
        print("❌ Supabase is not enabled. Check your .env configuration.")
        return None
    
    # Get conversation
    print("📋 Fetching conversation metadata...")
    conversation = manager.get_conversation_by_continuation_id(continuation_id)
    
    if not conversation:
        print(f"❌ Conversation not found: {continuation_id}")
        return None
    
    print(f"✅ Found conversation: {conversation.get('id')}")
    print(f"   Title: {conversation.get('title', 'N/A')}")
    print(f"   Created: {conversation.get('created_at', 'N/A')}")
    print(f"   Updated: {conversation.get('updated_at', 'N/A')}")
    
    # Get messages
    print(f"\n📨 Fetching messages...")
    messages = manager.get_conversation_messages(conversation['id'], limit=1000)
    
    if not messages:
        print("❌ No messages found in conversation")
        return None
    
    print(f"✅ Retrieved {len(messages)} messages\n")
    
    # Display messages
    print(f"{'='*80}")
    print("CONVERSATION MESSAGES")
    print(f"{'='*80}\n")
    
    for i, msg in enumerate(messages, 1):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        created_at = msg.get('created_at', 'N/A')
        metadata = msg.get('metadata', {})
        
        print(f"\n--- Message {i} ---")
        print(f"Role: {role}")
        print(f"Created: {created_at}")
        if metadata:
            print(f"Metadata: {json.dumps(metadata, indent=2)}")
        print(f"\nContent ({len(content)} chars):")
        print("-" * 80)
        # Truncate very long messages
        if len(content) > 2000:
            print(content[:1000])
            print(f"\n... [TRUNCATED - {len(content) - 2000} more chars] ...\n")
            print(content[-1000:])
        else:
            print(content)
        print("-" * 80)
    
    return {
        'conversation': conversation,
        'messages': messages
    }


def analyze_for_gaps(data):
    """Analyze conversation for any missed action items"""
    if not data:
        return
    
    print(f"\n{'='*80}")
    print("ANALYZING FOR MISSED ITEMS")
    print(f"{'='*80}\n")
    
    messages = data['messages']
    
    # Look for assistant messages with action items
    action_keywords = [
        'must', 'critical', 'important', 'required', 'should',
        'implement', 'add', 'create', 'fix', 'update',
        'gap', 'missing', 'need', 'priority'
    ]
    
    potential_gaps = []
    
    for msg in messages:
        if msg.get('role') == 'assistant':
            content = msg.get('content', '').lower()
            
            # Check for action keywords
            found_keywords = [kw for kw in action_keywords if kw in content]
            
            if found_keywords:
                potential_gaps.append({
                    'created_at': msg.get('created_at'),
                    'keywords': found_keywords,
                    'content_preview': msg.get('content', '')[:500]
                })
    
    if potential_gaps:
        print(f"⚠️  Found {len(potential_gaps)} messages with potential action items:\n")
        for i, gap in enumerate(potential_gaps, 1):
            print(f"{i}. Created: {gap['created_at']}")
            print(f"   Keywords: {', '.join(gap['keywords'])}")
            print(f"   Preview: {gap['content_preview'][:200]}...")
            print()
    else:
        print("✅ No obvious gaps detected in conversation")


if __name__ == "__main__":
    # EXAI conversation ID from Phase 3 validation
    continuation_id = "30441b5d-87d0-4f31-864e-d40e8dcbcad2"
    
    data = retrieve_conversation(continuation_id)
    
    if data:
        analyze_for_gaps(data)
        
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Total messages: {len(data['messages'])}")
        print(f"Conversation ID: {data['conversation']['id']}")
        print(f"Continuation ID: {continuation_id}")
        print(f"\n✅ Conversation retrieval complete!")
    else:
        print("\n❌ Failed to retrieve conversation")
        sys.exit(1)

