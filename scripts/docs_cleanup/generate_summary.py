"""
Generate comprehensive summary from Kimi consolidation analysis.
"""
import json
from pathlib import Path
from datetime import datetime

def generate_summary():
    """Generate summary report from analysis JSON."""
    
    # Load analysis
    analysis_file = Path("docs/COMPREHENSIVE_CONSOLIDATION_ANALYSIS.json")
    with open(analysis_file, 'r') as f:
        batches = json.load(f)
    
    # Aggregate findings
    all_superseded = []
    all_duplicates = []
    all_consolidation = []
    all_alignment = []
    
    for batch in batches:
        if isinstance(batch, dict):
            all_superseded.extend(batch.get('superseded', []))
            all_duplicates.extend(batch.get('duplicates', []))
            all_consolidation.extend(batch.get('consolidation', []))
            all_alignment.extend(batch.get('alignment_issues', []))
    
    # Generate markdown report
    report = f"""# Documentation Consolidation Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Batches Analyzed:** {len(batches)}  
**Total Files Analyzed:** {sum(b.get('files_analyzed', 0) for b in batches if isinstance(b, dict))}

---

## 🗑️ Superseded Files to Delete ({len(all_superseded)})

"""
    
    for item in all_superseded:
        if isinstance(item, dict):
            file = item.get('file', 'unknown')
            reason = item.get('reason', 'No reason provided')
            report += f"- **{file}**\n  - Reason: {reason}\n\n"
    
    report += f"""
---

## 🔄 Duplicate Pairs to Merge ({len(all_duplicates)})

"""
    
    for item in all_duplicates:
        if isinstance(item, dict):
            files = item.get('files', [])
            reason = item.get('reason', 'No reason provided')
            action = item.get('action', 'merge')
            if len(files) >= 2:
                report += f"- **Merge:** `{files[0]}` + `{files[1]}`\n"
                report += f"  - Reason: {reason}\n"
                report += f"  - Action: {action}\n\n"
    
    report += f"""
---

## 📦 Consolidation Opportunities ({len(all_consolidation)})

"""
    
    for item in all_consolidation:
        if isinstance(item, dict):
            files = item.get('files', [])
            target = item.get('target', 'unknown')
            reason = item.get('reason', 'No reason provided')
            report += f"- **Target:** `{target}`\n"
            report += f"  - Source files:\n"
            for f in files:
                report += f"    - `{f}`\n"
            report += f"  - Reason: {reason}\n\n"
    
    report += f"""
---

## ⚠️ Alignment Issues ({len(all_alignment)})

"""
    
    for item in all_alignment:
        if isinstance(item, dict):
            file = item.get('file', 'unknown')
            issue = item.get('issue', 'No issue provided')
            action = item.get('action', 'update')
            report += f"- **{file}**\n"
            report += f"  - Issue: {issue}\n"
            report += f"  - Action: {action}\n\n"
    
    report += f"""
---

## 📊 Summary Statistics

- **Total Superseded Files:** {len(all_superseded)}
- **Total Duplicate Pairs:** {len(all_duplicates)}
- **Total Consolidation Groups:** {len(all_consolidation)}
- **Total Alignment Issues:** {len(all_alignment)}
- **Total Actions Required:** {len(all_superseded) + len(all_duplicates) + len(all_consolidation) + len(all_alignment)}

---

## 🎯 Next Steps

1. **Review this summary** - Verify all recommendations
2. **Run deletion script** - `python scripts/docs_cleanup/delete_superseded.py`
3. **Manual merges** - Consolidate duplicate content
4. **Fix alignment** - Update outdated references
5. **Verify** - Ensure all changes are correct

"""
    
    # Save report
    output_file = Path("docs/CONSOLIDATION_SUMMARY.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Summary report saved to: {output_file}")
    print(f"\n📊 Quick Stats:")
    print(f"  - Superseded files: {len(all_superseded)}")
    print(f"  - Duplicate pairs: {len(all_duplicates)}")
    print(f"  - Consolidation groups: {len(all_consolidation)}")
    print(f"  - Alignment issues: {len(all_alignment)}")
    
    return output_file

if __name__ == "__main__":
    generate_summary()

