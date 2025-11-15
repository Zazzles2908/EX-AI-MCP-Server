#!/usr/bin/env python3
"""
Configuration Validation Test
Verifies that all configuration fixes have been applied correctly
"""

import os
import sys
import json
import re
from typing import Dict, List, Tuple

class ConfigurationValidator:
    """Validates all configuration fixes"""
    
    def __init__(self):
        self.validation_results = []
        self.passed_tests = 0
        self.total_tests = 0
    
    def log_validation(self, test_name: str, success: bool, details: str = ""):
        """Log validation result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
        }
        self.validation_results.append(result)
        
        print(f"\n{'-'*60}")
        print(f"TEST: {test_name}")
        print(f"STATUS: {status}")
        if details:
            print(f"DETAILS: {details}")
        print(f"{'-'*60}")
    
    def validate_docker_restart_policy(self) -> bool:
        """Validate Docker restart policy fix"""
        docker_file = "/workspace/ex-ai-mcp-server/docker-compose.yml"
        
        try:
            with open(docker_file, 'r') as f:
                content = f.read()
            
            # Count occurrences of restart policies
            unless_stopped_matches = re.findall(r'restart:\s*unless-stopped', content)
            on_failure_matches = re.findall(r'restart:\s*on-failure', content)
            
            details = f"unless-stopped: {len(unless_stopped_matches)}, on-failure: {len(on_failure_matches)}"
            
            if len(unless_stopped_matches) == 0 and len(on_failure_matches) >= 3:
                self.log_validation(
                    "Docker Restart Policy Fix", 
                    True, 
                    f"Successfully changed all restart policies to on-failure. {details}"
                )
                return True
            else:
                self.log_validation(
                    "Docker Restart Policy Fix", 
                    False, 
                    f"Still found unless-stopped policies or insufficient on-failure policies. {details}"
                )
                return False
                
        except Exception as e:
            self.log_validation("Docker Restart Policy Fix", False, f"Error reading docker-compose.yml: {e}")
            return False
    
    def validate_kimi_models_configuration(self) -> bool:
        """Validate Kimi models configuration"""
        config_file = "/workspace/ex-ai-mcp-server/src/providers/kimi_config.py"
        
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Check for new thinking models
            kimi_k2_thinking = '"kimi-k2-thinking"' in content
            kimi_k2_thinking_turbo = '"kimi-k2-thinking-turbo"' in content
            extended_thinking_support = 'supports_extended_thinking=True' in content
            
            # Check context window
            context_256k = '262144' in content  # 256K tokens
            
            details = f"kimi-k2-thinking: {kimi_k2_thinking}, kimi-k2-thinking-turbo: {kimi_k2_thinking_turbo}, extended thinking: {extended_thinking_support}, 256K context: {context_256k}"
            
            if kimi_k2_thinking and kimi_k2_thinking_turbo and extended_thinking_support and context_256k:
                self.log_validation(
                    "Kimi Models Configuration", 
                    True, 
                    f"Successfully added missing Kimi thinking models. {details}"
                )
                return True
            else:
                missing = []
                if not kimi_k2_thinking: missing.append("kimi-k2-thinking")
                if not kimi_k2_thinking_turbo: missing.append("kimi-k2-thinking-turbo")
                if not extended_thinking_support: missing.append("extended_thinking support")
                if not context_256k: missing.append("256K context window")
                
                self.log_validation(
                    "Kimi Models Configuration", 
                    False, 
                    f"Missing configuration items: {missing}. {details}"
                )
                return False
                
        except Exception as e:
            self.log_validation("Kimi Models Configuration", False, f"Error reading config file: {e}")
            return False
    
    def validate_mcp_test_files(self) -> bool:
        """Validate MCP test files exist and have correct structure"""
        test_files = [
            "/workspace/mcp_comprehensive_test.py",
            "/workspace/mcp_proper_client.py",
            "/workspace/test_kimi_complete_mcp.py"
        ]
        
        all_valid = True
        found_files = []
        
        for test_file in test_files:
            try:
                if os.path.exists(test_file):
                    with open(test_file, 'r') as f:
                        content = f.read()
                    
                    # Check for proper MCP protocol usage
                    has_jsonrpc = '"jsonrpc": "2.0"' in content
                    has_tools_call = '"method": "tools/call"' in content
                    has_kimi_chat = 'kimi_chat_with_tools' in content
                    has_analyze_structure = '"step":' in content and '"step_number":' in content
                    
                    if has_jsonrpc and has_tools_call and has_kimi_chat and has_analyze_structure:
                        found_files.append(f"{os.path.basename(test_file)} ✅")
                    else:
                        found_files.append(f"{os.path.basename(test_file)} ⚠️ (missing protocol elements)")
                        all_valid = False
                else:
                    found_files.append(f"{os.path.basename(test_file)} ❌ (not found)")
                    all_valid = False
                    
            except Exception as e:
                found_files.append(f"{os.path.basename(test_file)} ❌ (error: {e})")
                all_valid = False
        
        details = "; ".join(found_files)
        
        if all_valid:
            self.log_validation(
                "MCP Test Files", 
                True, 
                f"All test files created with proper MCP protocol structure. {details}"
            )
            return True
        else:
            self.log_validation(
                "MCP Test Files", 
                False, 
                f"Some test files missing or incomplete. {details}"
            )
            return False
    
    def validate_router_service_enhancement(self) -> bool:
        """Validate router service has been enhanced for thinking mode"""
        router_file = "/workspace/ex-ai-mcp-server/src/router/service.py"
        
        try:
            if os.path.exists(router_file):
                with open(router_file, 'r') as f:
                    content = f.read()
                
                # Check for thinking mode enhancements
                has_thinking_check = 'supports_extended_thinking' in content
                has_capability_validation = 'capabilities' in content
                has_model_selection = 'choose_model_with_hint' in content
                
                details = f"thinking check: {has_thinking_check}, capability validation: {has_capability_validation}, model selection: {has_model_selection}"
                
                if has_thinking_check and has_capability_validation:
                    self.log_validation(
                        "Router Service Enhancement", 
                        True, 
                        f"Router service enhanced for thinking mode validation. {details}"
                    )
                    return True
                else:
                    self.log_validation(
                        "Router Service Enhancement", 
                        False, 
                        f"Router service missing thinking mode enhancements. {details}"
                    )
                    return False
            else:
                self.log_validation(
                    "Router Service Enhancement", 
                    False, 
                    "Router service file not found"
                )
                return False
                
        except Exception as e:
            self.log_validation("Router Service Enhancement", False, f"Error reading router service: {e}")
            return False
    
    def validate_model_capabilities(self) -> bool:
        """Validate ModelCapabilities structure for new models"""
        config_file = "/workspace/ex-ai-mcp-server/src/providers/kimi_config.py"
        
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Extract kimi-k2-thinking model definition
            kimi_thinking_pattern = r'"kimi-k2-thinking":\s*ModelCapabilities\([^)]+\)'
            turbo_pattern = r'"kimi-k2-thinking-turbo":\s*ModelCapabilities\([^)]+\)'
            
            kimi_thinking_match = re.search(kimi_thinking_pattern, content, re.DOTALL)
            turbo_match = re.search(turbo_pattern, content, re.DOTALL)
            
            details = f"kimi-k2-thinking found: {kimi_thinking_match is not None}, kimi-k2-thinking-turbo found: {turbo_match is not None}"
            
            if kimi_thinking_match and turbo_match:
                self.log_validation(
                    "Model Capabilities Structure", 
                    True, 
                    f"Both new thinking models have proper ModelCapabilities structure. {details}"
                )
                return True
            else:
                self.log_validation(
                    "Model Capabilities Structure", 
                    False, 
                    f"Model capabilities structure incomplete. {details}"
                )
                return False
                
        except Exception as e:
            self.log_validation("Model Capabilities Structure", False, f"Error validating capabilities: {e}")
            return False
    
    def run_all_validations(self) -> bool:
        """Run all configuration validations"""
        print("🔍 CONFIGURATION VALIDATION TEST SUITE")
        print("=" * 80)
        print("Validating all MCP protocol and system stability fixes")
        print("=" * 80)
        
        # Run all validation tests
        tests = [
            self.validate_docker_restart_policy,
            self.validate_kimi_models_configuration,
            self.validate_mcp_test_files,
            self.validate_model_capabilities,
            self.validate_router_service_enhancement
        ]
        
        for test in tests:
            test()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Validations: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL CONFIGURATION VALIDATIONS PASSED!")
            print("✅ All MCP protocol fixes have been successfully applied.")
            return True
        else:
            print(f"\n⚠️  {self.total_tests - self.passed_tests} VALIDATIONS FAILED!")
            print("🔧 Please review and fix the issues above.")
            return False

def main():
    """Main validation execution"""
    validator = ConfigurationValidator()
    success = validator.run_all_validations()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
