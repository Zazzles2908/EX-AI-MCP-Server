#!/usr/bin/env python3
"""
Health Check Script for EXAI MCP Server

Validates:
1. Supabase connectivity
2. Database accessibility
3. Storage bucket access
4. WebSocket daemon status

Exit Codes:
0 - Healthy
1 - Unhealthy (system issue)
2 - Misconfiguration
3 - Service unavailable
"""

import sys
import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from supabase import create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        self.status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        self.healthy = True
        
        # Load configuration
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.ws_port = os.getenv('WS_PORT', '8079')
        
        if not self.supabase_url or not self.supabase_key:
            self._set_unhealthy("Missing Supabase configuration", exit_code=2)
    
    def _set_unhealthy(self, reason: str, exit_code: int = 1) -> None:
        """Mark health check as unhealthy with reason"""
        self.healthy = False
        self.status["status"] = "unhealthy"
        self.status["reason"] = reason
        logger.error(f"Health check failed: {reason}")
        if exit_code:
            sys.exit(exit_code)
    
    def check_supabase_connectivity(self) -> bool:
        """Check basic Supabase connectivity"""
        try:
            start_time = time.time()
            client = create_client(self.supabase_url, self.supabase_key)
            
            # Simple health check - try to get service status
            response = client.table('schema_version').select('version').limit(1).execute()
            
            duration = time.time() - start_time
            
            self.status["checks"]["supabase"] = {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Supabase connectivity check passed in {duration:.3f}s")
            return True
            
        except Exception as e:
            self.status["checks"]["supabase"] = {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self._set_unhealthy(f"Supabase connectivity failed: {str(e)}")
            return False
    
    def check_database_access(self) -> bool:
        """Check database accessibility"""
        try:
            start_time = time.time()
            client = create_client(self.supabase_url, self.supabase_key)
            
            # Try a simple query
            response = client.table('conversations').select('id').limit(1).execute()
            
            duration = time.time() - start_time
            
            self.status["checks"]["database"] = {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Database access check passed in {duration:.3f}s")
            return True
            
        except Exception as e:
            self.status["checks"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self._set_unhealthy(f"Database access failed: {str(e)}")
            return False
    
    def check_storage_access(self) -> bool:
        """Check storage bucket access"""
        try:
            start_time = time.time()
            client = create_client(self.supabase_url, self.supabase_key)
            
            # Try to get bucket info
            response = client.storage.get_bucket('user-files')
            
            duration = time.time() - start_time
            
            self.status["checks"]["storage"] = {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Storage access check passed in {duration:.3f}s")
            return True
            
        except Exception as e:
            self.status["checks"]["storage"] = {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self._set_unhealthy(f"Storage access failed: {str(e)}")
            return False
    
    def check_websocket_daemon(self) -> bool:
        """Check WebSocket daemon status"""
        try:
            start_time = time.time()
            
            # Simple socket check to see if port is open
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', int(self.ws_port)))
            sock.close()
            
            duration = time.time() - start_time
            
            if result == 0:
                self.status["checks"]["websocket"] = {
                    "status": "healthy",
                    "response_time_ms": round(duration * 1000, 2),
                    "timestamp": datetime.now().isoformat()
                }
                logger.info(f"WebSocket daemon check passed in {duration:.3f}s")
                return True
            else:
                self.status["checks"]["websocket"] = {
                    "status": "unhealthy",
                    "error": f"Port {self.ws_port} not accessible",
                    "timestamp": datetime.now().isoformat()
                }
                self._set_unhealthy(f"WebSocket daemon not responding on port {self.ws_port}")
                return False
                
        except Exception as e:
            self.status["checks"]["websocket"] = {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self._set_unhealthy(f"WebSocket daemon check failed: {str(e)}")
            return False
    
    def run_all_checks(self) -> bool:
        """Run all health checks"""
        logger.info("Starting comprehensive health check")
        
        # Run checks in order of importance
        checks = [
            self.check_supabase_connectivity,
            self.check_database_access,
            self.check_storage_access,
            self.check_websocket_daemon
        ]
        
        all_passed = True
        for check in checks:
            if not check():
                all_passed = False
        
        # Update overall status
        self.status["duration_ms"] = sum(
            check.get("response_time_ms", 0) 
            for check in self.status["checks"].values()
        )
        
        if all_passed:
            logger.info("All health checks passed")
            return True
        else:
            logger.error("Health checks failed")
            return False
    
    def output_status(self, format_type: str = "json") -> None:
        """Output health status in specified format"""
        if format_type == "json":
            print(json.dumps(self.status, indent=2))
        else:
            # Simple text output for Docker logs
            print(f"Health Status: {self.status['status']}")
            for name, check in self.status["checks"].items():
                status_symbol = "✅" if check["status"] == "healthy" else "❌"
                print(f"  {status_symbol} {name}: {check['status']}")

def main():
    """Main health check function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='EXAI MCP Server Health Check')
    parser.add_argument('--format', choices=['json', 'text'], default='text',
                        help='Output format')
    parser.add_argument('--endpoint', action='store_true',
                        help='Run as HTTP endpoint')
    
    args = parser.parse_args()
    
    if args.endpoint:
        # Run as HTTP endpoint for monitoring
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                checker = HealthChecker()
                checker.run_all_checks()
                
                self.send_response(200 if checker.healthy else 503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(checker.status).encode())
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
        logger.info("Health check endpoint started on port 8080")
        server.serve_forever()
    else:
        # Run as command-line health check
        checker = HealthChecker()
        checker.run_all_checks()
        checker.output_status(args.format)
        
        # Exit with appropriate code
        sys.exit(0 if checker.healthy else 1)

if __name__ == "__main__":
    main()

