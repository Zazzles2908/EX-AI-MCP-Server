"""
Session Memory Tracking for AI Operations

This file creates a memory tracking system to record how I operate in different sessions.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

class SessionMemoryTracker:
    """Tracks AI operations and decisions for future reference"""
    
    def __init__(self, session_id: Optional[str] = None, project_path: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.session_start_time = datetime.now(timezone.utc)
        
        # Create memory directory in project
        self.memory_dir = self.project_path / "session_memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        # Session file path
        self.session_file = self.memory_dir / f"session_{self.session_id}.json"
        
        # Initialize session data
        self.session_data = {
            "session_id": self.session_id,
            "start_time": self.session_start_time.isoformat(),
            "project_path": str(self.project_path),
            "operations": [],
            "mcp_validation": {},
            "issues_found": [],
            "fixes_applied": [],
            "tools_tested": [],
            "file_examinations": [],
            "decisions": []
        }
        
        print(f"Session Memory Tracker initialized: {self.session_id}")
        print(f"Memory file: {self.session_file}")
        
    def record_operation(self, operation_type: str, description: str, details: Dict[str, Any] = None):
        """Record an operation performed"""
        operation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": operation_type,
            "description": description,
            "details": details or {}
        }
        
        self.session_data["operations"].append(operation)
        print(f"Recorded operation: {operation_type} - {description}")
        
    def record_mcp_validation(self, mcp_server: str, status: str, details: Dict[str, Any] = None):
        """Record MCP server validation results"""
        self.session_data["mcp_validation"][mcp_server] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "details": details or {}
        }
        
        print(f"Recorded MCP validation: {mcp_server} - {status}")
        
    def record_issue(self, severity: str, description: str, resolution: str = None):
        """Record an issue found"""
        issue = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "description": description,
            "resolution": resolution
        }
        
        self.session_data["issues_found"].append(issue)
        print(f"Recorded issue: {severity} - {description}")
        
    def record_fix(self, description: str, files_affected: List[str] = None):
        """Record a fix applied"""
        fix = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": description,
            "files_affected": files_affected or []
        }
        
        self.session_data["fixes_applied"].append(fix)
        print(f"Recorded fix: {description}")
        
    def record_tool_test(self, tool_name: str, status: str, result: str = None):
        """Record tool testing results"""
        test = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool_name,
            "status": status,
            "result": result
        }
        
        self.session_data["tools_tested"].append(test)
        print(f"Recorded tool test: {tool_name} - {status}")
        
    def record_file_examination(self, file_path: str, findings: str):
        """Record file examination results"""
        examination = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "file": file_path,
            "findings": findings
        }
        
        self.session_data["file_examinations"].append(examination)
        print(f"Recorded file examination: {file_path}")
        
    def record_decision(self, decision: str, reasoning: str):
        """Record important decisions made"""
        decision_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "reasoning": reasoning
        }
        
        self.session_data["decisions"].append(decision_record)
        print(f"Recorded decision: {decision}")
        
    def save_session(self):
        """Save session data to file"""
        try:
            self.session_data["end_time"] = datetime.now(timezone.utc).isoformat()
            self.session_data["duration_seconds"] = (
                datetime.now(timezone.utc) - self.session_start_time
            ).total_seconds()
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
                
            print(f"Session saved: {self.session_file}")
            return True
            
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
            
    def get_session_summary(self) -> str:
        """Get a summary of the session"""
        operations_count = len(self.session_data["operations"])
        issues_count = len(self.session_data["issues_found"])
        fixes_count = len(self.session_data["fixes_applied"])
        tools_tested = len(self.session_data["tools_tested"])
        
        summary = f"""
Session {self.session_id} Summary:
- Duration: {self.session_data.get("duration_seconds", 0):.0f} seconds
- Operations recorded: {operations_count}
- Issues found: {issues_count}
- Fixes applied: {fixes_count}
- Tools tested: {tools_tested}
- Files examined: {len(self.session_data["file_examinations"])}

MCP Servers Validated:
"""
        
        for server, validation in self.session_data["mcp_validation"].items():
            status = validation["status"]
            summary += f"- {server}: {status}\n"
            
        return summary


# Global session tracker instance
_session_tracker = None

def get_session_tracker(session_id: Optional[str] = None, project_path: Optional[str] = None):
    """Get or create the global session tracker"""
    global _session_tracker
    if _session_tracker is None:
        _session_tracker = SessionMemoryTracker(session_id, project_path)
    return _session_tracker

def save_all_sessions():
    """Save all active sessions"""
    global _session_tracker
    if _session_tracker:
        return _session_tracker.save_session()
    return False

# Session cleanup at module load
import atexit
atexit.register(save_all_sessions)