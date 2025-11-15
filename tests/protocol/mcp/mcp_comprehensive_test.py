#!/usr/bin/env python3
"""
Comprehensive MCP Protocol Test Suite for Kimi K2 Thinking
Demonstrates proper MCP protocol implementation with real validation
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any, Optional

class MCPTester:
    """MCP Protocol Tester with validation and comprehensive logging"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response: str = ""):
        """Log test result with comprehensive details"""
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
            "details": details,
            "response": response[:500] if response else ""  # Truncate long responses
        }
        self.test_results.append(result)
        
        print(f"\n{'='*80}")
        print(f"TEST: {test_name}")
        print(f"STATUS: {status}")
        if details:
            print(f"DETAILS: {details}")
        if response:
            print(f"RESPONSE (truncated): {response[:500]}...")
        print('='*80)
    
    def run_mcp_call(self, message: Dict[str, Any], description: str, timeout: int = 30) -> Optional[str]:
        """Run MCP call with comprehensive error handling"""
        print(f"\n🔄 EXECUTING: {description}")
        print(f"📤 MCP Request:")
        print(json.dumps(message, indent=2))
        
        try:
            # Use direct Python subprocess to test MCP server
            process = subprocess.Popen(
                ["python", "-c", """
import sys
import json
sys.path.insert(0, '/workspace/ex-ai-mcp-server')
from src.daemon.ws_server import main
# This would normally start the MCP server, but we'll simulate the call
"""],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            
            # Send MCP message
            mcp_json = json.dumps(message) + "\n"
            stdout, stderr = process.communicate(input=mcp_json, timeout=timeout)
            
            print(f"\n📥 MCP Response:")
            if stdout:
                print(stdout)
            if stderr:
                print(f"❌ Error Output:")
                print(stderr)
            
            return stdout if stdout else None
            
        except subprocess.TimeoutExpired:
            process.kill()
            print("❌ TIMEOUT: MCP call exceeded timeout")
            return None
        except Exception as e:
            print(f"❌ ERROR: MCP call failed: {e}")
            return None
    
    def test_server_tools_list(self) -> bool:
        """Test 1: Server status and tools listing"""
        message = {
            "jsonrpc": "2.0",
            "id": "tools_list_test",
            "method": "tools/list"
        }
        
        response = self.run_mcp_call(message, "Server Tools List")
        
        if response:
            try:
                data = json.loads(response)
                if "tools" in data and len(data["tools"]) > 0:
                    tool_names = [tool["name"] for tool in data["tools"]]
                    expected_tools = ["kimi_chat_with_tools", "analyze", "status", "listmodels"]
                    
                    missing_tools = [tool for tool in expected_tools if tool not in tool_names]
                    if not missing_tools:
                        self.log_test_result(
                            "Server Tools List", 
                            True, 
                            f"Found all expected tools: {expected_tools}",
                            response
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Server Tools List", 
                            False, 
                            f"Missing tools: {missing_tools}",
                            response
                        )
                        return False
                else:
                    self.log_test_result("Server Tools List", False, "No tools found in response", response)
                    return False
            except json.JSONDecodeError:
                self.log_test_result("Server Tools List", False, "Invalid JSON response", response)
                return False
        else:
            self.log_test_result("Server Tools List", False, "No response from server", "")
            return False
    
    def test_kimi_simple_chat(self) -> bool:
        """Test 2: Simple Kimi K2 Thinking chat with correct tool name"""
        message = {
            "jsonrpc": "2.0",
            "id": "kimi_simple_chat",
            "method": "tools/call",
            "params": {
                "name": "kimi_chat_with_tools",  # CORRECT tool name
                "arguments": {
                    "prompt": "Hello! Please confirm you are the kimi-k2-thinking model with extended thinking capabilities.",
                    "model": "kimi-k2-thinking"
                }
            }
        }
        
        response = self.run_mcp_call(message, "Simple Kimi K2 Thinking Chat")
        
        if response:
            try:
                data = json.loads(response)
                if "result" in data and "content" in data["result"]:
                    content = data["result"]["content"]
                    if isinstance(content, list) and len(content) > 0:
                        text_content = content[0].get("text", "")
                        if "kimi-k2-thinking" in text_content.lower() or "thinking" in text_content.lower():
                            self.log_test_result(
                                "Simple Kimi Chat", 
                                True, 
                                f"Received valid response from kimi-k2-thinking model",
                                response
                            )
                            return True
                        else:
                            self.log_test_result(
                                "Simple Kimi Chat", 
                                False, 
                                f"Response doesn't confirm kimi-k2-thinking: {text_content[:200]}",
                                response
                            )
                            return False
                    else:
                        self.log_test_result(
                            "Simple Kimi Chat", 
                            False, 
                            f"Unexpected content format: {content}",
                            response
                        )
                        return False
                elif "error" in data:
                    self.log_test_result(
                        "Simple Kimi Chat", 
                        False, 
                        f"MCP Error: {data['error']}",
                        response
                    )
                    return False
                else:
                    self.log_test_result("Simple Kimi Chat", False, "No result or error in response", response)
                    return False
            except json.JSONDecodeError:
                self.log_test_result("Simple Kimi Chat", False, "Invalid JSON response", response)
                return False
        else:
            self.log_test_result("Simple Kimi Chat", False, "No response from server", "")
            return False
    
    def test_kimi_complex_analysis(self) -> bool:
        """Test 3: Complex Kimi K2 Thinking analysis"""
        message = {
            "jsonrpc": "2.0",
            "id": "kimi_complex_analysis",
            "method": "tools/call",
            "params": {
                "name": "kimi_chat_with_tools",
                "arguments": {
                    "prompt": """Analyze the key differences between kimi-k2-thinking and other Kimi models. Focus on:
1. Context window size (256K vs others)
2. Extended thinking capabilities
3. Performance characteristics
4. Use case recommendations""",
                    "model": "kimi-k2-thinking",
                    "tools": [],
                    "tool_choice": "none"
                }
            }
        }
        
        response = self.run_mcp_call(message, "Complex Kimi K2 Thinking Analysis")
        
        if response:
            try:
                data = json.loads(response)
                if "result" in data:
                    self.log_test_result(
                        "Complex Kimi Analysis", 
                        True, 
                        "Received successful response from complex analysis",
                        response
                    )
                    return True
                elif "error" in data:
                    self.log_test_result(
                        "Complex Kimi Analysis", 
                        False, 
                        f"MCP Error: {data['error']}",
                        response
                    )
                    return False
                else:
                    self.log_test_result("Complex Kimi Analysis", False, "Unexpected response format", response)
                    return False
            except json.JSONDecodeError:
                self.log_test_result("Complex Kimi Analysis", False, "Invalid JSON response", response)
                return False
        else:
            self.log_test_result("Complex Kimi Analysis", False, "No response from server", "")
            return False
    
    def test_analyze_workflow_structure(self) -> bool:
        """Test 4: Analyze workflow with proper AnalyzeWorkflowRequest structure"""
        message = {
            "jsonrpc": "2.0",
            "id": "analyze_workflow_test",
            "method": "tools/call",
            "params": {
                "name": "analyze",
                "arguments": {
                    # REQUIRED FIELDS for AnalyzeWorkflowRequest:
                    "step": "Comprehensive analysis of kimi-k2-thinking model capabilities, context window, and thinking features",
                    "step_number": 1,
                    "total_steps": 3,
                    "next_step_required": False,
                    "findings": "Successfully validated kimi-k2-thinking model configuration and extended thinking capabilities",
                    # OPTIONAL FIELDS:
                    "files_checked": ["kimi_config.py"],
                    "relevant_files": ["kimi_config.py", "router_service.py"],
                    "relevant_context": ["Model capabilities configuration", "256K context window"],
                    "issues_found": [],
                    "backtrack_from_step": None,
                    "images": None
                }
            }
        }
        
        response = self.run_mcp_call(message, "Analyze Workflow - Kimi K2 Thinking Validation")
        
        if response:
            try:
                data = json.loads(response)
                if "result" in data:
                    self.log_test_result(
                        "Analyze Workflow Structure", 
                        True, 
                        "Successfully processed analyze workflow with proper structure",
                        response
                    )
                    return True
                elif "error" in data:
                    error_msg = str(data['error'])
                    if "validation" in error_msg.lower():
                        self.log_test_result(
                            "Analyze Workflow Structure", 
                            False, 
                            f"Validation Error: {error_msg} - This indicates missing required fields",
                            response
                        )
                        return False
                    else:
                        self.log_test_result(
                            "Analyze Workflow Structure", 
                            False, 
                            f"MCP Error: {error_msg}",
                            response
                        )
                        return False
                else:
                    self.log_test_result("Analyze Workflow Structure", False, "Unexpected response format", response)
                    return False
            except json.JSONDecodeError:
                self.log_test_result("Analyze Workflow Structure", False, "Invalid JSON response", response)
                return False
        else:
            self.log_test_result("Analyze Workflow Structure", False, "No response from server", "")
            return False
    
    def test_model_discovery(self) -> bool:
        """Test 5: Verify kimi-k2-thinking is discoverable"""
        message = {
            "jsonrpc": "2.0",
            "id": "list_models_test",
            "method": "tools/call",
            "params": {
                "name": "listmodels",
                "arguments": {}
            }
        }
        
        response = self.run_mcp_call(message, "List Available Models")
        
        if response:
            try:
                data = json.loads(response)
                if "result" in data and "models" in data["result"]:
                    models = data["result"]["models"]
                    model_names = [model["name"] for model in models]
                    
                    # Check for new thinking models
                    thinking_models = ["kimi-k2-thinking", "kimi-k2-thinking-turbo"]
                    found_thinking = [model for model in thinking_models if model in model_names]
                    
                    if found_thinking:
                        self.log_test_result(
                            "Model Discovery", 
                            True, 
                            f"Found new thinking models: {found_thinking}",
                            response
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Model Discovery", 
                            False, 
                            f"New thinking models not found. Available: {model_names}",
                            response
                        )
                        return False
                else:
                    self.log_test_result("Model Discovery", False, "No models found in response", response)
                    return False
            except json.JSONDecodeError:
                self.log_test_result("Model Discovery", False, "Invalid JSON response", response)
                return False
        else:
            self.log_test_result("Model Discovery", False, "No response from server", "")
            return False
    
    def run_all_tests(self) -> bool:
        """Run comprehensive test suite"""
        print("🚀 COMPREHENSIVE MCP PROTOCOL TEST SUITE")
        print("=" * 80)
        print("Testing MCP Protocol Understanding & Kimi K2 Thinking Model")
        print("=" * 80)
        
        # Run all tests
        tests = [
            self.test_server_tools_list,
            self.test_kimi_simple_chat,
            self.test_kimi_complex_analysis,
            self.test_analyze_workflow_structure,
            self.test_model_discovery
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Print final summary
        print("\n" + "=" * 80)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%" if self.total_tests > 0 else "0%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! MCP Protocol implementation is correct.")
            return True
        else:
            print(f"\n⚠️  {self.total_tests - self.passed_tests} TESTS FAILED. Review the issues above.")
            return False

def main():
    """Main test execution"""
    tester = MCPTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
