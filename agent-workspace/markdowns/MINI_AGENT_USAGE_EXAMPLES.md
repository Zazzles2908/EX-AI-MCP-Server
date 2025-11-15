# Mini-Agent Integration Examples for EX-AI MCP Server

## Basic Usage

```python
from agent-workspace.skills import register_exai_skills

# Load all available skills
skills = register_exai_skills()

# Use system diagnostics
result = skills["exai_system_diagnostics"]()
print(f"System status: {result['data']['status']}")

# Use log cleanup
result = skills["exai_log_cleanup"]()
print(f"Log health score: {result['data']['log_health_score']}/100")

# Use router testing
result = skills["exai_minimax_router_test"]()
print(f"Router status: {result['data']['summary']['overall_status']}")
```

## Advanced Usage

```python
# Load specific skills
from agent-workspace.skills import register_exai_skills

skills = register_exai_skills()

# System monitoring workflow
def system_health_check():
    diag_result = skills["exai_system_diagnostics"]()
    
    if diag_result["status"] == "success":
        system_status = diag_result["data"]["status"]
        
        if system_status == "healthy":
            print("System is healthy")
        elif system_status == "degraded":
            # Run cleanup
            cleanup_result = skills["exai_log_cleanup"]()
            print(f"Log cleanup score: {cleanup_result['data']['log_health_score']}")
        else:
            print("System needs attention")
    
    return diag_result

# Router validation workflow  
def validate_routing():
    router_result = skills["exai_minimax_router_test"]()
    
    if router_result["status"] == "success":
        summary = router_result["data"]["summary"]
        print(f"Router success rate: {summary['success_rate_percent']}%")
        
        if summary["overall_status"] == "healthy":
            print("Routing is working correctly")
        else:
            print("Router needs attention")
    
    return router_result

# Run complete system check
def full_system_check():
    print("Running full system check...")
    
    # Run all diagnostics
    results = {}
    for skill_name, skill_func in skills.items():
        try:
            result = skill_func()
            results[skill_name] = result
            print(f"{skill_name}: {result['status']}")
        except Exception as e:
            print(f"{skill_name}: ERROR - {e}")
            results[skill_name] = {"status": "error", "error": str(e)}
    
    return results
```

## Direct Skill Usage

```bash
# Run diagnostics directly
python agent-workspace/skills/exai_system_diagnostics.py

# Clean up logs directly  
python agent-workspace/skills/exai_log_cleanup.py

# Test router directly
python agent-workspace/skills/exai_minimax_router_test.py
```

## Integration with Other Systems

```python
# Integration with monitoring systems
import json
from agent-workspace.skills import register_exai_skills

def export_metrics():
    skills = register_exai_skills()
    
    # Get system metrics
    diag = skills["exai_system_diagnostics"]()
    cleanup = skills["exai_log_cleanup"]()
    router = skills["exai_minimax_router_test"]()
    
    # Create metrics for external monitoring
    metrics = {
        "timestamp": diag["timestamp"],
        "system_status": diag["data"]["status"],
        "log_health_score": cleanup["data"]["log_health_score"],
        "router_success_rate": router["data"]["summary"]["success_rate_percent"]
    }
    
    # Export to monitoring system
    with open("system_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    return metrics
```
