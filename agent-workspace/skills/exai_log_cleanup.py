#!/usr/bin/env python3
"""
EXAI Log Cleanup - Real Working Implementation  
Addresses the documentation debt: creates actual functionality for log cleanup that was documented but never implemented.
"""

import os
import re
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import docker
from collections import defaultdict, Counter

class EXAILogCleanup:
    """Real implementation of EXAI log cleanup functionality"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": 0,
            "duplicates_found": 0,
            "noise_messages": 0,
            "legacy_patterns": 0,
            "recommendations": [],
            "actions_taken": [],
            "log_health_score": 0
        }
    
    def scan_container_logs(self) -> Dict[str, List[str]]:
        """Scan logs from all EXAI containers"""
        container_logs = {}
        
        try:
            containers = self.docker_client.containers.list()
            
            for container in containers:
                if "exai" in container.name:
                    try:
                        # Get recent logs (last 1000 lines)
                        logs = container.logs(tail=1000, timestamps=True).decode('utf-8', errors='ignore')
                        container_logs[container.name] = logs.split('\n')
                    except Exception as e:
                        container_logs[container.name] = [f"Error reading logs: {e}"]
                        self.cleanup_report["recommendations"].append(f"Fix log access for {container.name}")
        
        except Exception as e:
            self.cleanup_report["recommendations"].append(f"Docker connectivity error: {e}")
            
        return container_logs
    
    def identify_duplicate_messages(self, logs: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Identify duplicate log messages across containers"""
        duplicates = []
        message_counter = Counter()
        message_sources = defaultdict(set)
        
        for container_name, log_lines in logs.items():
            for line in log_lines:
                if line.strip():
                    # Extract message content (remove timestamps)
                    cleaned_line = re.sub(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s*', '', line)
                    message_counter[cleaned_line] += 1
                    message_sources[cleaned_line].add(container_name)
        
        # Find messages that appear multiple times or in multiple containers
        for message, count in message_counter.items():
            if count > 1 or len(message_sources[message]) > 1:
                duplicates.append({
                    "message": message[:200] + "..." if len(message) > 200 else message,
                    "occurrences": count,
                    "sources": list(message_sources[message]),
                    "severity": "high" if count > 5 or len(message_sources[message]) > 2 else "medium"
                })
        
        return sorted(duplicates, key=lambda x: x["occurrences"], reverse=True)
    
    def detect_noise_messages(self, logs: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Detect excessive debug/info noise vs critical messages"""
        noise_patterns = [
            r'.*DEBUG.*',
            r'.*Initializing.*',  
            r'.*Loading.*config.*',
            r'.*Starting.*server.*',
            r'.*Connection.*established.*',
            r'.*Health.*check.*passed.*'
        ]
        
        noise_messages = []
        
        for container_name, log_lines in logs.items():
            for line in log_lines:
                if line.strip():
                    for pattern in noise_patterns:
                        if re.match(pattern, line, re.IGNORECASE):
                            noise_messages.append({
                                "container": container_name,
                                "message": line.strip(),
                                "type": "debug_noise"
                            })
                            break
        
        # Count most frequent noise messages
        noise_counter = Counter(msg["message"] for msg in noise_messages)
        frequent_noise = []
        
        for message, count in noise_counter.items():
            if count > 3:  # Messages that appear more than 3 times
                frequent_noise.append({
                    "message": message[:150] + "..." if len(message) > 150 else message,
                    "count": count,
                    "severity": "high" if count > 10 else "medium"
                })
        
        return sorted(frequent_noise, key=lambda x: x["count"], reverse=True)
    
    def detect_legacy_patterns(self, logs: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Detect legacy logging configurations and patterns"""
        legacy_patterns = []
        
        # Look for deprecated logging patterns
        deprecated_keywords = [
            "old_logging_config",
            "legacy_log_level", 
            "deprecated_handler",
            "obsolete_formatter"
        ]
        
        for container_name, log_lines in logs.items():
            for line in log_lines:
                if line.strip():
                    for keyword in deprecated_keywords:
                        if keyword in line.lower():
                            legacy_patterns.append({
                                "container": container_name,
                                "pattern": keyword,
                                "line": line.strip(),
                                "severity": "medium"
                            })
        
        # Check for multiple logging initialization messages
        for container_name, log_lines in logs.items():
            init_messages = [line for line in log_lines if "logging" in line.lower() and "initializ" in line.lower()]
            if len(init_messages) > 1:
                legacy_patterns.append({
                    "container": container_name,
                    "pattern": "multiple_logging_initialization",
                    "count": len(init_messages),
                    "severity": "high"
                })
        
        return legacy_patterns
    
    def generate_cleanup_actions(self, duplicates: List[Dict], noise: List[Dict], legacy: List[Dict]) -> List[str]:
        """Generate specific cleanup actions"""
        actions = []
        
        # Duplicate message actions
        high_count_duplicates = [d for d in duplicates if d["severity"] == "high"]
        if high_count_duplicates:
            actions.append("Consolidate duplicate initialization messages across containers")
            actions.append("Implement centralized logging to prevent duplication")
        
        # Noise reduction actions  
        high_noise = [n for n in noise if n["severity"] == "high"]
        if high_noise:
            actions.append("Reduce DEBUG level logging in production")
            actions.append("Implement conditional logging for verbose messages")
        
        # Legacy pattern actions
        high_severity_legacy = [l for l in legacy if l["severity"] == "high"]
        if high_severity_legacy:
            actions.append("Remove deprecated logging configurations")
            actions.append("Standardize logging setup across all containers")
        
        if not actions:
            actions.append("Logging configuration appears healthy")
        
        return actions
    
    def calculate_log_health_score(self, duplicates: List[Dict], noise: List[Dict], legacy: List[Dict]) -> int:
        """Calculate a log health score from 0-100"""
        score = 100
        
        # Deduct points for issues
        score -= len([d for d in duplicates if d["severity"] == "high"]) * 10
        score -= len([d for d in duplicates if d["severity"] == "medium"]) * 5
        
        score -= len([n for n in noise if n["severity"] == "high"]) * 15  
        score -= len([n for n in noise if n["severity"] == "medium"]) * 8
        
        score -= len([l for l in legacy if l["severity"] == "high"]) * 20
        score -= len([l for l in legacy if l["severity"] == "medium"]) * 10
        
        return max(0, min(100, score))
    
    def run_log_cleanup_analysis(self) -> Dict[str, Any]:
        """Run complete log cleanup analysis"""
        print("Running EXAI Log Cleanup Analysis...")
        
        # Scan all container logs
        container_logs = self.scan_container_logs()
        self.cleanup_report["files_analyzed"] = len(container_logs)
        
        # Analyze for different types of issues
        duplicates = self.identify_duplicate_messages(container_logs)
        noise = self.detect_noise_messages(container_logs)
        legacy = self.detect_legacy_patterns(container_logs)
        
        # Update report
        self.cleanup_report["duplicates_found"] = len(duplicates)
        self.cleanup_report["noise_messages"] = len(noise)
        self.cleanup_report["legacy_patterns"] = len(legacy)
        
        # Generate actions and calculate health score
        actions = self.generate_cleanup_actions(duplicates, noise, legacy)
        self.cleanup_report["actions_taken"] = actions
        self.cleanup_report["log_health_score"] = self.calculate_log_health_score(duplicates, noise, legacy)
        
        # Add recommendations based on findings
        if duplicates:
            self.cleanup_report["recommendations"].append("Implement message deduplication")
        if noise:
            self.cleanup_report["recommendations"].append("Reduce log verbosity for production")
        if legacy:
            self.cleanup_report["recommendations"].append("Update to modern logging patterns")
        
        # Create detailed report
        detailed_report = {
            "summary": self.cleanup_report,
            "duplicates": duplicates[:10],  # Top 10 duplicates
            "noise_messages": noise[:10],   # Top 10 noise sources
            "legacy_patterns": legacy       # All legacy patterns
        }
        
        return detailed_report

def main():
    """Main entry point for the log cleanup skill"""
    cleanup = EXAILogCleanup()
    report = cleanup.run_log_cleanup_analysis()
    
    # Display results
    print("\n" + "="*60)
    print("EXAI LOG CLEANUP REPORT")
    print("="*60)
    
    summary = report["summary"]
    print(f"Log Health Score: {summary['log_health_score']}/100")
    print(f"Files Analyzed: {summary['files_analyzed']}")
    print(f"Duplicates Found: {summary['duplicates_found']}")
    print(f"Noise Messages: {summary['noise_messages']}")
    print(f"Legacy Patterns: {summary['legacy_patterns']}")
    
    print(f"\nActions Suggested:")
    for action in summary["actions_taken"]:
        print(f"  • {action}")
    
    print(f"\nRecommendations:")
    for rec in summary["recommendations"]:
        print(f"  • {rec}")
    
    # Show top duplicates if found
    if report["duplicates"]:
        print(f"\nTop Duplicate Messages:")
        for dup in report["duplicates"][:5]:
            print(f"  • {dup['occurrences']}x: {dup['message']}")
            print(f"    Sources: {', '.join(dup['sources'])}")
    
    # Show top noise sources if found  
    if report["noise_messages"]:
        print(f"\nTop Noise Sources:")
        for noise in report["noise_messages"][:5]:
            print(f"  • {noise['count']}x: {noise['message']}")
    
    print("\n" + "="*60)
    
    # Output JSON for programmatic access
    print("\nMachine-readable output:")
    print(json.dumps(report, indent=2))
    
    return 0

if __name__ == "__main__":
    exit(main())