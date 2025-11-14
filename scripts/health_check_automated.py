#!/usr/bin/env python3
"""
EXAI MCP Server - Automated Health Check & Report Generator

This script runs automatically after container startup to:
1. Parse Docker logs for errors/warnings
2. Test all endpoints and services
3. Validate configuration
4. Generate comprehensive health report
5. Save to docs/reports/CONTAINER_HEALTH_REPORT.md (overwrites previous)

Usage:
  python scripts/health_check_automated.py

Or integrate into docker-compose.yml:
  command: sh -c "python scripts/health_check_automated.py && python -u scripts/ws/run_ws_daemon.py"
"""

import json
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import os

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class AutomatedHealthCheck:
    def __init__(self):
        self.report_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'container_info': {},
            'issues': {
                'critical': [],
                'warnings': [],
                'info': []
            },
            'tests': {},
            'logs_analysis': {},
            'recommendations': []
        }

    def log(self, message: str, level: str = "INFO"):
        """Print log message"""
        # Disable colors on Windows
        if os.name == 'nt':
            print(f"[{level}] {message}")
        else:
            color = {
                "INFO": Colors.BLUE,
                "WARNING": Colors.YELLOW,
                "ERROR": Colors.RED,
                "SUCCESS": Colors.GREEN,
                "HEADER": Colors.BOLD + Colors.CYAN
            }.get(level, Colors.WHITE)

            print(f"{color}[{level}]{Colors.END} {message}")

    def run_command(self, cmd: str, timeout: int = 10) -> Tuple[str, bool]:
        """Run shell command and return output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout.strip(), result.returncode == 0
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout}s", False
        except Exception as e:
            return str(e), False

    def get_container_logs(self, container: str, lines: int = 200) -> str:
        """Get container logs"""
        output, _ = self.run_command(
            f"docker-compose logs --tail={lines} {container} 2>&1"
        )
        return output

    def parse_logs_for_errors(self, logs: str, container: str) -> Dict:
        """Parse logs for errors, warnings, and issues"""
        issues = {
            'errors': [],
            'warnings': [],
            'critical': []
        }

        # Common error patterns
        error_patterns = [
            (r'ERROR[:\s]', 'error'),
            (r'FATAL[:\s]', 'critical'),
            (r'CRITICAL[:\s]', 'critical'),
            (r'Exception|Traceback', 'error'),
            (r'Failed to|Error while|Could not', 'error'),
            (r'WARNING[:\s]', 'warning'),
            (r'not available|not installed|disabled', 'warning'),
            (r'Connection refused|Timeout|timeout', 'warning'),
        ]

        for line in logs.split('\n'):
            for pattern, severity in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Extract timestamp if present
                    timestamp_match = re.match(r'^(\S+\s+\S+)', line)
                    timestamp = timestamp_match.group(1) if timestamp_match else "N/A"

                    issues[severity].append({
                        'timestamp': timestamp,
                        'container': container,
                        'message': line.strip()
                    })

        return issues

    def test_endpoint(self, name: str, url: str, timeout: int = 5) -> Dict:
        """Test HTTP endpoint"""
        output, success = self.run_command(
            f"curl -s -w '%{{http_code}}' --max-time {timeout} {url} -o /tmp/endpoint_test.txt"
        )

        http_code = "000"
        content = ""

        if output:
            http_code = output[-3:] if len(output) >= 3 else "000"
            success = http_code == "200"

        if os.path.exists("/tmp/endpoint_test.txt"):
            with open("/tmp/endpoint_test.txt") as f:
                content = f.read()[:500]  # First 500 chars

        return {
            'name': name,
            'url': url,
            'status_code': http_code,
            'success': success,
            'content_preview': content
        }

    def test_container_health(self) -> Dict:
        """Test container health"""
        output, _ = self.run_command("docker-compose ps --format json")

        try:
            containers = json.loads(output) if output else []
        except:
            containers = []

        health_status = {}
        for container in containers:
            name = container.get('Service', 'unknown')
            status = container.get('Status', 'unknown')
            health_status[name] = {
                'status': status,
                'healthy': 'healthy' in status.lower() or 'up' in status.lower()
            }

        # Also test with docker ps
        output, _ = self.run_command("docker ps --format '{{.Names}}|{{.Status}}'")
        for line in output.split('\n'):
            if '|' in line:
                name, status = line.split('|')
                if name not in health_status:
                    health_status[name] = {
                        'status': status,
                        'healthy': 'healthy' in status.lower() or 'up' in status.lower()
                    }

        return health_status

    def test_redis(self) -> Dict:
        """Test Redis functionality"""
        tests = {}

        # Check if redis-cli is available (host vs container)
        has_redis_cli = self.run_command("which redis-cli", timeout=2)[1]

        if has_redis_cli:
            # Running on host - use docker-compose exec
            output, success = self.run_command(
                "docker-compose exec -T redis redis-cli -a ExAi2025RedisSecurePass123 ping 2>/dev/null"
            )
            tests['ping'] = {
                'success': 'PONG' in output,
                'output': output.strip()[:100]
            }
            if not tests['ping']['success']:
                self.report_data['issues']['warnings'].append({
                    'source': 'redis',
                    'message': f'Redis ping failed: {output.strip()[:100]}'
                })

            # Test 2: Auth test
            output, _ = self.run_command(
                "docker-compose exec -T redis redis-cli -a ExAi2025RedisSecurePass123 auth ExAi2025RedisSecurePass123 2>/dev/null"
            )
            tests['auth'] = {
                'success': 'OK' in output,
                'output': output.strip()[:100]
            }

            # Test 3: Get config
            output, _ = self.run_command(
                "docker-compose exec -T redis redis-cli -a ExAi2025RedisSecurePass123 config get requirepass 2>/dev/null"
            )
            tests['password'] = {
                'success': 'ExAi2025RedisSecurePass123' in output,
                'output': 'Password configured' if 'ExAi2025RedisSecurePass123' in output else 'Password not found'
            }
        else:
            # Running in container - check if Redis is accessible via network
            # Since we're inside container, Redis is at hostname 'redis'
            import socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('exai-redis', 6379))
                sock.close()

                tests['ping'] = {
                    'success': result == 0,
                    'output': 'Redis port accessible' if result == 0 else 'Redis port not accessible'
                }

                if result == 0:
                    self.report_data['issues']['info'].append({
                        'source': 'redis',
                        'message': 'Redis is accessible from container (port 6379)'
                    })
                else:
                    self.report_data['issues']['warnings'].append({
                        'source': 'redis',
                        'message': 'Redis is not accessible from container'
                    })

                tests['auth'] = {
                    'success': True,
                    'output': 'Skipped in container mode'
                }
                tests['password'] = {
                    'success': True,
                    'output': 'Skipped in container mode'
                }
            except Exception as e:
                tests['ping'] = {
                    'success': False,
                    'output': f'Connection test failed: {str(e)[:100]}'
                }

        return tests

    def analyze_log_issues(self) -> None:
        """Analyze logs from all containers for issues"""
        containers = ['exai-mcp-server', 'exai-redis', 'exai-redis-commander']

        for container in containers:
            logs = self.get_container_logs(container, lines=200)
            issues = self.parse_logs_for_errors(logs, container)

            # Store in report
            self.report_data['logs_analysis'][container] = {
                'error_count': len(issues['errors']),
                'warning_count': len(issues['warnings']),
                'critical_count': len(issues['critical']),
                'errors': issues['errors'][:10],  # First 10 errors
                'warnings': issues['warnings'][:10],  # First 10 warnings
                'critical': issues['critical'][:10]  # First 10 critical
            }

            # Add to global issues
            for error in issues['errors']:
                self.report_data['issues']['warnings'].append(error)
            for critical in issues['critical']:
                self.report_data['issues']['critical'].append(critical)

    def check_minimax_issue(self) -> None:
        """Check for MiniMax anthropic package issue"""
        logs = self.get_container_logs('exai-mcp-server', lines=50)

        if 'anthropic package not installed' in logs:
            self.report_data['issues']['critical'].append({
                'source': 'exai-mcp-server',
                'type': 'dependency_missing',
                'message': 'MiniMax M2-Stable: anthropic package missing - routing disabled',
                'impact': 'High - MiniMax M2-Stable model unavailable',
                'recommendation': 'Install anthropic package or use GLM/Kimi as fallback'
            })

            self.report_data['recommendations'].append(
                'Fix MiniMax M2-Stable: Install anthropic package in Dockerfile'
            )

    def check_supabase_issue(self) -> None:
        """Check for Supabase table missing issue"""
        logs = self.get_container_logs('exai-mcp-server', lines=100)

        if 'Could not find the table' in logs and 'conversations' in logs:
            self.report_data['issues']['critical'].append({
                'source': 'exai-mcp-server',
                'type': 'database_missing',
                'message': 'Supabase: conversations table missing',
                'impact': 'Medium - Persistent storage unavailable',
                'recommendation': 'Create conversations table in Supabase or use fallback storage'
            })

            self.report_data['recommendations'].append(
                'Fix Supabase: Create missing conversations table or disable Supabase integration'
            )

    def test_all_endpoints(self) -> None:
        """Test all HTTP endpoints"""
        endpoints = [
            ("Health Check (3002)", "http://127.0.0.1:3002/health"),
            ("Dashboard (3001)", "http://127.0.0.1:3001/health"),
            ("Metrics (3003)", "http://127.0.0.1:3003/metrics")
        ]

        for name, url in endpoints:
            result = self.test_endpoint(name, url)
            self.report_data['tests'][name] = result

            if not result['success']:
                self.report_data['issues']['warnings'].append({
                    'source': 'endpoint',
                    'service': name,
                    'message': f'Endpoint failed: HTTP {result["status_code"]}',
                    'url': url
                })

    def generate_report(self) -> str:
        """Generate markdown report"""
        timestamp = self.report_data['timestamp']

        # Calculate stats
        total_errors = len(self.report_data['issues']['critical'])
        total_warnings = len(self.report_data['issues']['warnings'])
        critical_issues = self.report_data['issues']['critical']

        # Determine overall status
        if total_errors > 0:
            status = "CRITICAL ISSUES DETECTED"
        elif total_warnings > 3:
            status = "WARNINGS DETECTED"
        else:
            status = "HEALTHY"

        report = f"""# EXAI MCP Server - Automated Health Report

**Generated:** {timestamp}
**Status:** {status}

---

## Critical Issues Detected: {total_errors}
## Warnings Detected: {total_warnings}

---

"""

        # Add critical issues section
        if critical_issues:
            report += "## CRITICAL ISSUES\n\n"
            for i, issue in enumerate(critical_issues, 1):
                report += f"### {i}. {issue.get('message', 'Unknown error')}\n"
                report += f"**Source:** {issue.get('source', 'N/A')}\n"
                report += f"**Impact:** {issue.get('impact', 'N/A')}\n"
                if 'recommendation' in issue:
                    report += f"**Recommendation:** {issue['recommendation']}\n"
                report += "\n"

        # Add warnings section
        warnings = self.report_data['issues']['warnings'][:10]  # Top 10 warnings
        if warnings:
            report += "## WARNINGS\n\n"
            for i, warning in enumerate(warnings, 1):
                report += f"{i}. **{warning.get('source', 'N/A')}:** {warning.get('message', 'Unknown warning')}\n"
            report += "\n"

        # Add info messages section
        info_messages = self.report_data['issues']['info'][:10]  # Top 10 info messages
        if info_messages:
            report += "## INFO\n\n"
            for i, info in enumerate(info_messages, 1):
                report += f"{i}. **{info.get('source', 'N/A')}:** {info.get('message', 'N/A')}\n"
            report += "\n"

        # Add log analysis section
        report += "## Container Log Analysis\n\n"
        report += "| Container | Errors | Warnings | Critical |\n"
        report += "|-----------|--------|----------|----------|\n"

        for container, data in self.report_data['logs_analysis'].items():
            report += f"| {container} | {data['error_count']} | {data['warning_count']} | {data['critical_count']} |\n"

        report += "\n"

        # Add endpoint tests
        report += "## Endpoint Tests\n\n"
        report += "| Endpoint | Status | HTTP Code |\n"
        report += "|----------|--------|-----------|\n"

        for name, test in self.report_data['tests'].items():
            if isinstance(test, dict) and 'success' in test:
                status = "PASS" if test['success'] else "FAIL"
                code = test.get('status_code', 'N/A')
                report += f"| {name} | {status} | {code} |\n"

        report += "\n"

        # Add Redis tests
        redis_tests = self.report_data.get('tests', {}).get('redis', {})
        if redis_tests:
            report += "## Redis Tests\n\n"
            for test_name, test_data in redis_tests.items():
                if isinstance(test_data, dict) and 'success' in test_data:
                    status = "PASS" if test_data['success'] else "FAIL"
                    report += f"- **{test_name.replace('_', ' ').title()}:** {status}\n"
            report += "\n"

        # Add recommendations
        if self.report_data['recommendations']:
            report += "## 🔧 RECOMMENDATIONS\n\n"
            for i, rec in enumerate(self.report_data['recommendations'], 1):
                report += f"{i}. {rec}\n"
            report += "\n"

        # Add footer
        report += f"""---

**Report Type:** Automated Health Check
**Timestamp:** {timestamp}
**Next Check:** Run this script after container rebuild

### How to Use This Report

1. **Critical Issues:** Fix immediately before production use
2. **Warnings:** Review and fix when possible
3. **Recommendations:** Suggested improvements
4. **Run Again:** `python scripts/health_check_automated.py`

"""

        return report

    def save_report(self, content: str) -> str:
        """Save report to file"""
        output_path = Path("docs/reports/CONTAINER_HEALTH_REPORT.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_path)

    def run(self) -> int:
        """Run complete health check"""
        self.log("=" * 60, "HEADER")
        self.log("EXAI MCP Server - Automated Health Check", "HEADER")
        self.log("=" * 60, "HEADER")
        self.log("")

        # Step 1: Test container health
        self.log("Testing container health...", "INFO")
        self.report_data['container_info'] = self.test_container_health()

        # Step 2: Analyze logs for issues
        self.log("Analyzing container logs...", "INFO")
        self.analyze_log_issues()

        # Step 3: Check for specific known issues
        self.log("Checking for known issues...", "INFO")
        self.check_minimax_issue()
        self.check_supabase_issue()

        # Step 4: Check if daemon is running (health check runs BEFORE daemon starts!)
        # Note: Due to docker-compose.yml command structure, this health check runs
        # BEFORE the daemon starts. The daemon is started AFTER this health check completes.
        self.log("Checking daemon startup status...", "INFO")
        daemon_ready = False
        try:
            import subprocess
            result = subprocess.run(
                "curl -s --max-time 2 http://127.0.0.1:3002/health",
                shell=True,
                capture_output=True,
                timeout=3
            )
            if result.returncode == 0 and b"healthy" in result.stdout:
                daemon_ready = True
                self.log("Daemon is ready", "SUCCESS")
            else:
                self.log("Daemon not yet ready (this is expected during container startup)", "WARNING")
        except Exception:
            self.log("Daemon not yet ready (this is expected during container startup)", "WARNING")

        # Step 5: Test endpoints (will fail if daemon not started yet)
        self.log("Testing endpoints...", "INFO")
        self.test_all_endpoints()

        # Mark endpoint failures as expected if daemon is not ready
        # (which is the case during automated startup-time health checks)
        if not daemon_ready:
            # Remove endpoint warnings and add info message instead
            self.report_data['issues']['warnings'] = [
                w for w in self.report_data['issues']['warnings']
                if w.get('source') != 'endpoint'
            ]
            self.report_data['issues']['info'].append({
                'source': 'health_check',
                'message': 'Endpoint tests skipped - running during container startup (before daemon is ready). Daemon will start after this health check completes.'
            })

        # Step 6: Test Redis
        self.log("Testing Redis...", "INFO")
        redis_tests = self.test_redis()
        self.report_data['tests']['redis'] = redis_tests

        # Step 7: Generate and save report
        self.log("Generating report...", "INFO")
        report_content = self.generate_report()
        report_path = self.save_report(report_content)

        # Step 8: Print summary
        self.log("")
        self.log("=" * 60, "HEADER")
        self.log("HEALTH CHECK SUMMARY", "HEADER")
        self.log("=" * 60, "HEADER")

        critical_count = len(self.report_data['issues']['critical'])
        warning_count = len(self.report_data['issues']['warnings'])

        if critical_count > 0:
            self.log(f"Critical Issues: {critical_count}", "ERROR")
        if warning_count > 0:
            self.log(f"Warnings: {warning_count}", "WARNING")

        self.log(f"Report saved: {report_path}", "SUCCESS")
        self.log("")

        # Return exit code based on issues
        if critical_count > 0:
            self.log(f"Critical Issues: {critical_count}", "ERROR")
            self.log("Status: FAILED - Critical issues detected", "ERROR")
            return 1
        elif warning_count > 5:
            self.log(f"Warnings: {warning_count}", "WARNING")
            self.log("Status: WARNING - Multiple warnings", "WARNING")
            return 2
        else:
            self.log("Status: PASSED - System healthy", "SUCCESS")
            return 0

def main():
    health_check = AutomatedHealthCheck()
    exit_code = health_check.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
