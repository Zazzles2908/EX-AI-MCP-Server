"""
Consolidate BEST information from all docs into system-reference/.

This script uses Kimi to analyze all markdown files and extract the best,
most accurate, and up-to-date information to consolidate into system-reference/.
"""

import os
import sys
import json
from pathlib import Path
import logging
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main consolidation workflow."""
    from tools.providers.kimi.kimi_upload import KimiUploadAndExtractTool
    from src.providers.kimi import KimiModelProvider
    
    logger.info("=" * 80)
    logger.info("SYSTEM-REFERENCE CONSOLIDATION - KIMI-POWERED")
    logger.info("=" * 80)
    
    # Load markdown inventory
    inventory_file = project_root / "docs_markdown_inventory.json"
    with open(inventory_file, 'r', encoding='utf-8') as f:
        inventory = json.load(f)
    
    total_files = len(inventory)
    logger.info(f"\n📊 Found {total_files} markdown files to analyze")
    
    # Categorize files
    categories = {
        'system_reference': [],
        'current': [],
        'architecture': [],
        'upgrades': [],
        'guides': [],
        'archive': [],
        'root': []
    }
    
    for item in inventory:
        path = item['FullName']
        if 'system-reference' in path:
            categories['system_reference'].append(path)
        elif 'current' in path:
            categories['current'].append(path)
        elif 'architecture' in path and 'archive' not in path:
            categories['architecture'].append(path)
        elif 'upgrades' in path and 'archive' not in path:
            categories['upgrades'].append(path)
        elif 'guides' in path:
            categories['guides'].append(path)
        elif 'archive' in path:
            categories['archive'].append(path)
        else:
            categories['root'].append(path)
    
    logger.info("\n📁 **CATEGORIZATION:**")
    for cat, files in categories.items():
        logger.info(f"   {cat}: {len(files)} files")
    
    # Phase 1: Upload system-reference as baseline
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1: Upload System-Reference Baseline")
    logger.info("=" * 80)
    
    upload_tool = KimiUploadAndExtractTool()
    baseline_files = categories['system_reference']
    
    logger.info(f"\n📤 Uploading {len(baseline_files)} system-reference files...")
    baseline_msgs = upload_tool._run(files=baseline_files)
    
    baseline_file_ids = []
    for msg in baseline_msgs:
        file_id = msg.get('_file_id')
        if file_id:
            baseline_file_ids.append(file_id)
    
    logger.info(f"✅ Uploaded {len(baseline_file_ids)} baseline files")
    
    # Phase 2: Analyze each category against baseline
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2: Analyze Categories Against Baseline")
    logger.info("=" * 80)
    
    provider = KimiModelProvider(api_key=os.getenv("KIMI_API_KEY"))
    all_uploaded_files = baseline_file_ids.copy()
    
    analysis_results = {}
    
    # Analyze each category
    for cat_name in ['current', 'architecture', 'upgrades']:
        if not categories[cat_name]:
            continue
        
        logger.info(f"\n📋 Analyzing category: {cat_name} ({len(categories[cat_name])} files)")
        
        # Upload category files
        cat_msgs = upload_tool._run(files=categories[cat_name])
        cat_file_ids = [msg.get('_file_id') for msg in cat_msgs if msg.get('_file_id')]
        all_uploaded_files.extend(cat_file_ids)
        
        # Ask Kimi to analyze
        prompt = f"""
You have access to:
1. **BASELINE**: docs/system-reference/ (8 files) - The current definitive design intent
2. **CATEGORY**: docs/{cat_name}/ ({len(categories[cat_name])} files) - Additional documentation

**TASK**: Compare the {cat_name} docs against the system-reference baseline and identify:

1. **BETTER INFORMATION**: Content in {cat_name} that is MORE accurate, detailed, or up-to-date than system-reference
2. **MISSING INFORMATION**: Important content in {cat_name} that is NOT in system-reference
3. **CONFLICTS**: Where {cat_name} contradicts system-reference (note which is correct)
4. **REDUNDANT**: Content in {cat_name} that duplicates system-reference (can be archived)

For each finding, provide:
- **File**: Specific file path
- **Section**: Which part of the content
- **Recommendation**: MERGE (add to system-reference), UPDATE (replace in system-reference), ARCHIVE (redundant), or CONFLICT (needs resolution)
- **Reason**: Why this action is recommended

Return as JSON:
```json
{{
  "category": "{cat_name}",
  "better_information": [
    {{"file": "...", "section": "...", "recommendation": "MERGE", "reason": "..."}}
  ],
  "missing_information": [
    {{"file": "...", "section": "...", "recommendation": "MERGE", "reason": "..."}}
  ],
  "conflicts": [
    {{"file": "...", "section": "...", "correct_version": "system-reference|{cat_name}", "reason": "..."}}
  ],
  "redundant": [
    {{"file": "...", "recommendation": "ARCHIVE", "reason": "..."}}
  ]
}}
```
"""
        
        response = provider.client.chat.completions.create(
            model="kimi-k2-0905-preview",
            messages=[
                *baseline_msgs,
                *cat_msgs,
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        analysis_results[cat_name] = result
        
        logger.info(f"✅ Analyzed {cat_name}")
    
    # Save results
    output_file = project_root / "docs" / f"CONSOLIDATION_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n💾 Saved analysis to: {output_file}")
    
    # Cleanup uploaded files
    logger.info("\n🧹 Cleaning up uploaded files...")
    for file_id in all_uploaded_files:
        try:
            provider.client.files.delete(file_id)
        except Exception as e:
            logger.warning(f"Failed to delete {file_id}: {e}")
    
    logger.info(f"✅ Deleted {len(all_uploaded_files)} files from Kimi platform")
    
    logger.info("\n" + "=" * 80)
    logger.info("CONSOLIDATION ANALYSIS COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"\nNext steps:")
    logger.info(f"1. Review analysis: {output_file}")
    logger.info(f"2. Execute merges/updates to system-reference/")
    logger.info(f"3. Archive redundant files")
    logger.info(f"4. Resolve conflicts")


if __name__ == "__main__":
    main()

