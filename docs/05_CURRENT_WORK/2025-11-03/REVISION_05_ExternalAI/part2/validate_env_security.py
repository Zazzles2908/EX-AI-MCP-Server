#!/usr/bin/env python3
"""
Environment Configuration Security Validator

This script validates environment variables for security issues,
missing configurations, and potential misconfigurations.

Usage:
    python validate_env_security.py
"""

import os
import sys
import re
import json
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional


class EnvironmentValidator:
    """Validates environment configuration for security issues"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def validate(self) -> Tuple[int, List[str], List[str]]:
        """Run all validation checks and return results"""
        self._check_required_variables()
        self._check_api_keys_security()
        self._check_url_security()
        self._check_proxy_security()
        self._check_browser_security()
        self._check_development_security()
        self._check_secrets_management()
        
        total_issues = len(self.errors) + len(self.warnings)
        return total_issues, self.errors, self.warnings
    
    def _check_required_variables(self):
        """Check for required environment variables"""
        required = {
            'LLM_GATEWAY_BASE_URL': self._validate_url,
            'AGENT_NAME': self._validate_string,
        }
        
        for var_name, validator in required.items():
            value = os.getenv(var_name)
            if not validator(value):
                self.errors.append(f"Missing required environment variable: {var_name}")
    
    def _check_api_keys_security(self):
        """Check API keys for security issues"""
        api_key_patterns = {
            'RAPIDAPI_KEY': r'^[a-zA-Z0-9]{20,}$',
            'JWT_SECRET': r'^[a-zA-Z0-9]{32,}$',
            'LLM_GATEWAY_API_KEY': r'^[a-zA-Z0-9\-_]{20,}$',
        }
        
        for var_name, pattern in api_key_patterns.items():
            value = os.getenv(var_name)
            if value:
                if not re.match(pattern, value):
                    self.warnings.append(f"Weak or malformed API key: {var_name}")
                if value in ['your-api-key-here', 'default', 'admin', 'password']:
                    self.errors.append(f"Default/weak API key detected: {var_name}")
    
    def _check_url_security(self):
        """Check URLs for security issues"""
        urls_to_check = [
            'LLM_GATEWAY_BASE_URL',
            'HTTP_PROXY',
            'HTTPS_PROXY',
        ]
        
        for var_name in urls_to_check:
            url = os.getenv(var_name)
            if url:
                if not self._validate_url(url):
                    self.errors.append(f"Invalid URL format: {var_name}")
                
                # Check for insecure protocols
                parsed = urlparse(url)
                if parsed.scheme in ['http', 'ftp'] and 'localhost' not in parsed.netloc:
                    self.warnings.append(f"Insecure protocol (http) used: {var_name}")
                
                # Check for hardcoded production URLs
                if 'prod' in url.lower() and os.getenv('ENVIRONMENT', '').lower() == 'development':
                    self.warnings.append(f"Production URL in development environment: {var_name}")
    
    def _check_proxy_security(self):
        """Check proxy configuration security"""
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY']
        has_proxy = any(os.getenv(var) for var in proxy_vars)
        
        if has_proxy:
            proxy_user = os.getenv('PROXY_USERNAME')
            proxy_pass = os.getenv('PROXY_PASSWORD')
            
            if proxy_user and not proxy_pass:
                self.warnings.append("Proxy username set but password missing")
            if not proxy_user and proxy_pass:
                self.warnings.append("Proxy password set but username missing")
    
    def _check_browser_security(self):
        """Check browser configuration security"""
        disable_security = os.getenv('DISABLE_BROWSER_SECURITY', 'false').lower()
        environment = os.getenv('ENVIRONMENT', '').lower()
        
        if disable_security == 'true':
            if environment == 'production':
                self.errors.append("Browser security disabled in production environment")
            else:
                self.warnings.append("Browser security disabled - only use in development")
        
        chrome_port = os.getenv('CHROME_DEBUG_PORT')
        if chrome_port:
            try:
                port_num = int(chrome_port)
                if port_num < 1024:
                    self.warnings.append(f"Chrome debug port {port_num} requires root privileges")
                if port_num > 65535:
                    self.errors.append(f"Invalid Chrome debug port: {port_port}")
            except ValueError:
                self.errors.append(f"Invalid Chrome debug port format: {chrome_port}")
    
    def _check_development_security(self):
        """Check for development-specific security issues"""
        debug = os.getenv('DEBUG', 'false').lower()
        environment = os.getenv('ENVIRONMENT', '').lower()
        
        if debug == 'true' and environment == 'production':
            self.errors.append("Debug mode enabled in production")
        
        verbose_logging = os.getenv('VERBOSE_LOGGING', 'false').lower()
        if verbose_logging == 'true' and environment == 'production':
            self.warnings.append("Verbose logging enabled in production")
    
    def _check_secrets_management(self):
        """Check for proper secrets management"""
        env_file = os.getenv('ENV_FILE', '.env')
        
        # Check if .env file exists and warn about version control
        if os.path.exists('.env'):
            self.info.append(".env file found - ensure it's in .gitignore")
            
        # Check for common weak secrets
        weak_secrets = [
            ('password', ['password', '123456', 'admin']),
            ('secret', ['secret', 'key', 'token']),
        ]
        
        for var_name, weak_values in weak_secrets:
            for value in os.environ:
                for weak_val in weak_values:
                    if weak_val in value.lower():
                        self.warnings.append(f"Potentially weak secret in environment: {var_name}")
                        break
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _validate_string(self, value: str) -> bool:
        """Validate non-empty string"""
        return bool(value and value.strip())
    
    def _validate_api_key(self, key: str) -> bool:
        """Validate API key format"""
        return bool(key and len(key) > 10)
    
    def print_results(self):
        """Print validation results"""
        print("=" * 60)
        print("ENVIRONMENT CONFIGURATION SECURITY VALIDATION")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.info:
            print(f"\n📋 INFO ({len(self.info)}):")
            for info in self.info:
                print(f"  • {info}")
        
        # Summary
        total_issues = len(self.errors) + len(self.warnings)
        if total_issues == 0:
            print("\n✅ No security issues found!")
            return 0
        else:
            print(f"\n🔍 Found {total_issues} issues ({len(self.errors)} errors, {len(self.warnings)} warnings)")
            return 1
    
    def generate_report(self, output_file: str = 'env_security_report.json'):
        """Generate JSON security report"""
        report = {
            'timestamp': str(pd.Timestamp.now()),
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'total_info': len(self.info),
                'severity': 'HIGH' if self.errors else 'MEDIUM' if self.warnings else 'LOW'
            }
        }
        
        try:
            import pandas as pd
        except ImportError:
            report['timestamp'] = '2025-11-03 16:17:51'
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Security report saved to: {output_file}")


def main():
    """Main validation function"""
    validator = EnvironmentValidator()
    total_issues, errors, warnings = validator.validate()
    
    # Print results
    exit_code = validator.print_results()
    
    # Generate report
    validator.generate_report()
    
    # Print recommendations
    print("\n" + "=" * 60)
    print("SECURITY RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = [
        "1. Create and use .env.example for documentation",
        "2. Never commit .env files to version control",
        "3. Use strong, unique API keys and secrets",
        "4. Separate development and production configurations",
        "5. Enable environment validation at application startup",
        "6. Use secrets management tools in production",
        "7. Regularly rotate API keys and passwords",
        "8. Monitor for unauthorized configuration changes",
        "9. Implement proper access controls",
        "10. Add security monitoring and alerting"
    ]
    
    for rec in recommendations:
        print(f"  {rec}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())