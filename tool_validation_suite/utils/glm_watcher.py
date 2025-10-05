"""
GLM Watcher - Independent Test Observer

This module provides independent validation of test executions using GLM-4-Flash.
The watcher observes each test, analyzes quality, detects anomalies, and provides
suggestions for improvement.

Key Features:
- Independent API key (separate from main GLM testing)
- Objective quality assessment
- Anomaly detection
- Improvement suggestions
- Meta-analysis of testing process

Created: 2025-10-05
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.testing")

logger = logging.getLogger(__name__)


class GLMWatcher:
    """
    Independent test observer using GLM-4-Flash.
    
    The watcher uses a separate API key to ensure complete independence
    from the tools being tested.
    """
    
    def __init__(self):
        """Initialize the GLM Watcher."""
        self.api_key = os.getenv("GLM_WATCHER_KEY")
        self.model = os.getenv("GLM_WATCHER_MODEL", "glm-4.5-flash")
        self.base_url = os.getenv("GLM_BASE_URL", "https://api.z.ai/api/paas/v4")
        self.enabled = os.getenv("GLM_WATCHER_ENABLED", "true").lower() == "true"
        self.detail_level = os.getenv("WATCHER_DETAIL_LEVEL", "high")
        self.timeout_secs = int(os.getenv("WATCHER_TIMEOUT_SECS", "30"))
        self.save_observations = os.getenv("SAVE_WATCHER_OBSERVATIONS", "true").lower() == "true"
        self.observation_dir = Path(os.getenv("WATCHER_OBSERVATION_DIR", "./results/latest/watcher_observations"))
        
        # Create observation directory
        self.observation_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate configuration
        if self.enabled and not self.api_key:
            logger.warning("GLM Watcher enabled but no API key configured. Disabling watcher.")
            self.enabled = False
        
        logger.info(f"GLM Watcher initialized (enabled={self.enabled}, model={self.model})")
    
    def observe_test(
        self,
        tool_name: str,
        variation_name: str,
        test_input: Dict[str, Any],
        expected_behavior: str,
        actual_output: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        test_status: str
    ) -> Optional[Dict[str, Any]]:
        """
        Observe a test execution and provide independent analysis.
        
        Args:
            tool_name: Name of the tool being tested
            variation_name: Name of the test variation
            test_input: Input parameters for the test
            expected_behavior: Expected behavior description
            actual_output: Actual output from the tool
            performance_metrics: Performance metrics (time, memory, cost, etc.)
            test_status: Test status (PASS, FAIL, ERROR, etc.)
        
        Returns:
            Observation dictionary with analysis, or None if watcher disabled
        """
        if not self.enabled:
            return None
        
        try:
            # Prepare observation context
            context = self._prepare_context(
                tool_name,
                variation_name,
                test_input,
                expected_behavior,
                actual_output,
                performance_metrics,
                test_status
            )
            
            # Get watcher analysis
            analysis = self._analyze_with_glm(context)
            
            # Create observation
            observation = {
                "tool": tool_name,
                "variation": variation_name,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "test_status": test_status,
                "watcher_analysis": analysis,
                "performance_metrics": performance_metrics
            }
            
            # Save observation
            if self.save_observations:
                self._save_observation(tool_name, variation_name, observation)
            
            return observation
        
        except Exception as e:
            logger.error(f"Watcher observation failed: {e}")
            return None
    
    def _prepare_context(
        self,
        tool_name: str,
        variation_name: str,
        test_input: Dict[str, Any],
        expected_behavior: str,
        actual_output: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        test_status: str
    ) -> str:
        """Prepare context for watcher analysis."""
        
        # Truncate large outputs
        input_str = json.dumps(test_input, indent=2)[:1000]
        output_str = json.dumps(actual_output, indent=2)[:2000]
        
        if self.detail_level == "high":
            context = f"""
You are an independent test observer analyzing a tool execution in the EX-AI MCP Server.

**Tool:** {tool_name}
**Test Variation:** {variation_name}
**Test Status:** {test_status}

**Input:**
```json
{input_str}
```

**Expected Behavior:**
{expected_behavior}

**Actual Output:**
```json
{output_str}
```

**Performance Metrics:**
- Response Time: {performance_metrics.get('response_time_secs', 'N/A')}s
- Memory Usage: {performance_metrics.get('memory_mb', 'N/A')} MB
- CPU Usage: {performance_metrics.get('cpu_percent', 'N/A')}%
- API Cost: ${performance_metrics.get('cost_usd', 'N/A')}
- Tokens Used: {performance_metrics.get('tokens', 'N/A')}

**Your Task:**
Analyze this test execution objectively and provide:

1. **Quality Score (1-10):** Rate the overall quality of the tool's response
2. **Correctness:** Is the output correct? (CORRECT / INCORRECT / PARTIAL)
3. **Anomalies:** List any unusual behavior, performance issues, or unexpected results
4. **Suggestions:** Provide 2-3 specific suggestions for improvement
5. **Confidence (0.0-1.0):** Your confidence in this assessment
6. **Observations:** Brief summary of your analysis (2-3 sentences)

Be objective, critical, and constructive. Your analysis helps validate the testing process.

Respond in JSON format:
{{
  "quality_score": <1-10>,
  "correctness": "<CORRECT|INCORRECT|PARTIAL>",
  "anomalies": ["anomaly1", "anomaly2", ...],
  "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
  "confidence": <0.0-1.0>,
  "observations": "<your observations>"
}}
"""
        elif self.detail_level == "medium":
            context = f"""
Analyze this test execution:

Tool: {tool_name}
Variation: {variation_name}
Status: {test_status}
Response Time: {performance_metrics.get('response_time_secs', 'N/A')}s
Cost: ${performance_metrics.get('cost_usd', 'N/A')}

Provide quality score (1-10), correctness assessment, and 2 suggestions.

Respond in JSON format with: quality_score, correctness, suggestions, confidence, observations.
"""
        else:  # low
            context = f"""
Quick analysis of {tool_name} - {variation_name} ({test_status}):
Quality score (1-10), correctness, 1 suggestion.

JSON format: quality_score, correctness, suggestions, confidence, observations.
"""
        
        return context
    
    def _analyze_with_glm(self, context: str) -> Dict[str, Any]:
        """Call GLM-4-Flash to analyze the test execution."""
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an objective test observer. Analyze test executions and provide constructive feedback in JSON format."
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            "temperature": 0.3,  # Low temperature for consistent analysis
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout_secs
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Try to parse JSON response
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                analysis = json.loads(content)
                return analysis
            
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Watcher response not valid JSON, using fallback")
                return {
                    "quality_score": 5,
                    "correctness": "UNKNOWN",
                    "anomalies": [],
                    "suggestions": ["Unable to parse watcher response"],
                    "confidence": 0.5,
                    "observations": content[:200]
                }
        
        except Exception as e:
            logger.error(f"GLM Watcher API call failed: {e}")
            return {
                "quality_score": 0,
                "correctness": "ERROR",
                "anomalies": [f"Watcher error: {str(e)}"],
                "suggestions": [],
                "confidence": 0.0,
                "observations": f"Watcher analysis failed: {str(e)}"
            }
    
    def _save_observation(self, tool_name: str, variation_name: str, observation: Dict[str, Any]):
        """Save observation to file."""
        
        filename = f"{tool_name}_{variation_name}.json"
        filepath = self.observation_dir / filename
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(observation, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved watcher observation: {filepath}")
        
        except Exception as e:
            logger.error(f"Failed to save watcher observation: {e}")
    
    def generate_summary(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of all watcher observations.
        
        Args:
            observations: List of all observations
        
        Returns:
            Summary dictionary with aggregated statistics
        """
        if not observations:
            return {
                "total_observations": 0,
                "average_quality_score": 0,
                "correctness_distribution": {},
                "common_anomalies": [],
                "top_suggestions": []
            }
        
        # Calculate statistics
        quality_scores = [obs["watcher_analysis"].get("quality_score", 0) for obs in observations]
        correctness_values = [obs["watcher_analysis"].get("correctness", "UNKNOWN") for obs in observations]
        
        # Aggregate anomalies and suggestions
        all_anomalies = []
        all_suggestions = []
        for obs in observations:
            all_anomalies.extend(obs["watcher_analysis"].get("anomalies", []))
            all_suggestions.extend(obs["watcher_analysis"].get("suggestions", []))
        
        # Count occurrences
        from collections import Counter
        anomaly_counts = Counter(all_anomalies)
        suggestion_counts = Counter(all_suggestions)
        correctness_counts = Counter(correctness_values)
        
        summary = {
            "total_observations": len(observations),
            "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "min_quality_score": min(quality_scores) if quality_scores else 0,
            "max_quality_score": max(quality_scores) if quality_scores else 0,
            "correctness_distribution": dict(correctness_counts),
            "common_anomalies": [{"anomaly": k, "count": v} for k, v in anomaly_counts.most_common(10)],
            "top_suggestions": [{"suggestion": k, "count": v} for k, v in suggestion_counts.most_common(10)]
        }
        
        # Save summary
        if self.save_observations:
            summary_path = self.observation_dir / "summary.json"
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return summary


# Example usage
if __name__ == "__main__":
    # Initialize watcher
    watcher = GLMWatcher()
    
    # Example test observation
    observation = watcher.observe_test(
        tool_name="chat",
        variation_name="basic_functionality",
        test_input={"prompt": "Hello, how are you?", "model": "moonshot-v1-8k"},
        expected_behavior="Should return a friendly greeting response",
        actual_output={"status": "success", "content": "Hello! I'm doing well, thank you for asking. How can I help you today?"},
        performance_metrics={"response_time_secs": 2.3, "memory_mb": 45, "cpu_percent": 12, "cost_usd": 0.02, "tokens": 25},
        test_status="PASS"
    )
    
    if observation:
        print(json.dumps(observation, indent=2))

