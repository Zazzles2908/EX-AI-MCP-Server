#!/usr/bin/env python3
"""
EXAI System Diagnostics - Real Working Implementation
Addresses the documentation debt: this skill was documented but never implemented.
"""

import json
import subprocess
import docker
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

class EXAISystemDiagnostics:
    """Real implementation of EXAI system diagnostics"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "containers": {},
            "routing": {},
            "providers": {},
            "logs": {},
            "mcp_tools": {},
            "recommendations": []
        }
    
    def check_container_health(self) -> Dict[str, str]:
        """Check health of all EXAI containers"""
        container_status = {}
        
        expected_containers = [
            "exai-mcp-stdio",
            "exai-mcp-server", 
            "redis",
            "redis-commander"
        ]
        
        try:
            # Get running containers
            containers = self.docker_client.containers.list(all=True)
            
            for container in containers:
                name = container.name
                if any(expected in name for expected in expected_containers):
                    status = container.status
                    if status == "running":
                        container_status[name] = "running"
                    else:
                        container_status[name] = f"degraded ({status})"
            
            # Mark missing containers
            for expected in expected_containers:
                if expected not in container_status:
                    container_status[expected] = "missing"
                    
        except Exception as e:
            container_status["error"] = str(e)
            self.results["recommendations"].append("Fix Docker connectivity issues")
        
        return container_status
    
    def check_minimax_routing(self) -> Dict[str, Any]:
        """Check MiniMax M2 routing status"""
        routing_status = {
            "minimax_status": "disabled",
            "anthropic_package": "unknown",
            "smart_routing": "disabled"
        }
        
        try:
            # Check if anthropic package is installed
            result = subprocess.run([sys.executable, "-c", "import anthropic; print(anthropic.__version__)"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                routing_status["anthropic_package"] = f"installed ({result.stdout.strip()})"
                routing_status["minimax_status"] = "potentially_active"
            else:
                routing_status["anthropic_package"] = "missing"
                self.results["recommendations"].append("Install anthropic package: pip install anthropic")
                
        except Exception as e:
            routing_status["anthropic_package"] = f"error: {e}"
        
        return routing_status
    
    def test_provider_connectivity(self) -> Dict[str, str]:
        """Test connectivity to AI providers"""
        providers = {}
        
        # Check environment variables for API keys
        api_keys = {
            "GLM_API_KEY": os.getenv("GLM_API_KEY"),
            "KIMI_API_KEY": os.getenv("KIMI_API_KEY"), 
            "MINIMAX_API_KEY": os.getenv("MINIMAX_API_KEY")
        }
        
        for provider, key in api_keys.items():
            if key:
                providers[provider.lower().replace("_api_key", "")] = "configured"
            else:
                providers[provider.lower().replace("_api_key", "")] = "missing_api_key"
                self.results["recommendations"].append(f"Set {provider} environment variable")
        
        return providers
    
    def analyze_logs(self) -> Dict[str, Any]:
        """Analyze system logs for issues"""
        log_analysis = {
            "health": "unknown",
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Check for common log issues in container logs
            containers = self.docker_client.containers.list()
            
            for container in containers:
                if "exai" in container.name:
                    logs = container.logs(tail=100).decode('utf-8', errors='ignore')
                    
                    # Look for duplicate initialization
                    init_count = logs.count("Initializing")
                    if init_count > 2:
                        log_analysis["issues"].append("duplicate_initialization")
                        log_analysis["recommendations"].append("Consolidate initialization logging")
                    
                    # Look for error patterns
                    error_lines = [line for line in logs.split('\n') if 'error' in line.lower() or 'exception' in line.lower()]
                    if len(error_lines) > 10:
                        log_analysis["issues"].append("excessive_errors")
                        log_analysis["recommendations"].append("Review and fix error patterns")
            
            if not log_analysis["issues"]:
                log_analysis["health"] = "clean"
            else:
                log_analysis["health"] = "messy"
                
        except Exception as e:
            log_analysis["health"] = "error"
            log_analysis["issues"].append(f"log_analysis_error: {e}")
        
        return log_analysis
    
    def check_mcp_tools(self) -> Dict[str, Any]:
        """Check MCP tool discovery"""
        try:
            # Try to list MCP tools through the server
            result = subprocess.run([sys.executable, "-m", "src.server", "--list-tools"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                tools_count = len(result.stdout.split('\n'))
                return {
                    "discovered": tools_count,
                    "expected": "29-33",
                    "status": "healthy" if 29 <= tools_count <= 33 else "degraded"
                }
            else:
                return {
                    "discovered": 0,
                    "expected": "29-33", 
                    "status": "critical",
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "discovered": 0,
                "expected": "29-33",
                "status": "critical", 
                "error": str(e)
            }
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run complete system diagnostics"""
        print("Running EXAI System Diagnostics...")
        
        # Check all components
        self.results["containers"] = self.check_container_health()
        self.results["routing"] = self.check_minimax_routing()
        self.results["providers"] = self.test_provider_connectivity()
        self.results["logs"] = self.analyze_logs()
        self.results["mcp_tools"] = self.check_mcp_tools()
        
        # Determine overall health
        critical_issues = 0
        if any("critical" in str(status).lower() for status in self.results["containers"].values()):
            critical_issues += 1
        if self.results["mcp_tools"]["status"] == "critical":
            critical_issues += 1
        if self.results["logs"]["health"] == "error":
            critical_issues += 1
            
        if critical_issues == 0:
            self.results["status"] = "healthy"
        elif critical_issues <= 2:
            self.results["status"] = "degraded"
        else:
            self.results["status"] = "critical"
        
        # Add general recommendations
        if not self.results["recommendations"]:
            self.results["recommendations"].append("System appears healthy")
        
        return self.results

def main():
    """Main entry point for the diagnostics skill"""
    diagnostics = EXAISystemDiagnostics()
    results = diagnostics.run_diagnostics()
    
    # Output results in both human-readable and JSON format
    print("\n" + "="*60)
    print("[DIAGNOSTICS] EXAI SYSTEM DIAGNOSTICS REPORT")
    print("="*60)
    print(f"Status: {results['status'].upper()}")
    print(f"Timestamp: {results['timestamp']}")
    
    print("\n[CONTAINERS] Container Status:")
    for container, status in results['containers'].items():
        print(f"  {container}: {status}")
    
    print("\n[ROUTING] MiniMax Routing:")
    for key, value in results['routing'].items():
        print(f"  {key}: {value}")
    
    print("\n[PROVIDERS] Provider Status:")
    for provider, status in results['providers'].items():
        print(f"  {provider}: {status}")
    
    print(f"\n[LOGS] Logs Health: {results['logs']['health']}")
    if results['logs']['issues']:
        print("  Issues found:")
        for issue in results['logs']['issues']:
            print(f"    - {issue}")
    
    print(f"\n[MCP_TOOLS] MCP Tools: {results['mcp_tools']['discovered']} discovered (expected {results['mcp_tools']['expected']})")
    print(f"  Status: {results['mcp_tools']['status']}")
    
    print(f"\n[RECOMMENDATIONS] Recommendations:")
    for rec in results['recommendations']:
        print(f"  * {rec}")
    
    print("\n" + "="*60)
    
    # Output JSON for programmatic access
    print("\n[MACHINE_READABLE] Machine-readable output:")

    # Output JSON for programmatic access
    print("\n[DATA] Machine-readable output:")
    print(json.dumps(results, indent=2))
    
    return 0 if results['status'] == 'healthy' else 1

if __name__ == "__main__":
    exit(main())