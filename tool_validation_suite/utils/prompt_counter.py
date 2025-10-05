"""
Prompt Counter - Track API calls and feature usage

This module tracks all prompts sent during testing, including:
- Total prompts per model
- Feature activation (web search, file upload, thinking mode, tools)
- Cost tracking per feature
- Model usage statistics

Created: 2025-10-05
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PromptCounter:
    """
    Track all prompts and feature usage during testing.
    
    Tracks:
    - Total prompts
    - Prompts per model (Kimi/GLM)
    - Prompts per tool
    - Feature activation (web search, file upload, thinking mode, tools)
    - Cost per feature
    - Token usage
    """
    
    def __init__(self, results_dir: str = "./tool_validation_suite/results/latest"):
        """Initialize the prompt counter."""
        self.results_dir = Path(results_dir)
        self.counter_file = self.results_dir / "prompt_counter.json"
        
        # Initialize counters
        self.counters = {
            "session_start": datetime.utcnow().isoformat() + "Z",
            "total_prompts": 0,
            "prompts_by_provider": {
                "kimi": 0,
                "glm": 0,
                "watcher": 0
            },
            "prompts_by_model": {},
            "prompts_by_tool": {},
            "feature_usage": {
                "web_search": {
                    "kimi": 0,
                    "glm": 0,
                    "total": 0
                },
                "file_upload": {
                    "kimi": 0,
                    "glm": 0,
                    "total": 0
                },
                "thinking_mode": {
                    "basic": 0,
                    "deep": 0,
                    "expert": 0,
                    "total": 0
                },
                "tool_use": {
                    "kimi": 0,
                    "glm": 0,
                    "total": 0
                }
            },
            "token_usage": {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "by_provider": {
                    "kimi": {"input": 0, "output": 0, "total": 0},
                    "glm": {"input": 0, "output": 0, "total": 0},
                    "watcher": {"input": 0, "output": 0, "total": 0}
                }
            },
            "cost_tracking": {
                "total_cost_usd": 0.0,
                "by_provider": {
                    "kimi": 0.0,
                    "glm": 0.0,
                    "watcher": 0.0
                },
                "by_feature": {
                    "web_search": 0.0,
                    "file_upload": 0.0,
                    "thinking_mode": 0.0,
                    "base_calls": 0.0
                }
            },
            "prompt_history": []
        }
        
        # Load pricing configuration
        self.pricing = self._load_pricing()
        
        logger.info("Prompt counter initialized")
    
    def _load_pricing(self) -> Dict[str, Any]:
        """Load pricing configuration."""
        pricing_file = Path("tool_validation_suite/config/pricing_and_models.json")
        
        try:
            with open(pricing_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load pricing config: {e}")
            return {}
    
    def record_prompt(
        self,
        provider: str,
        model: str,
        tool_name: str,
        variation: str,
        input_tokens: int,
        output_tokens: int,
        features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a prompt execution.
        
        Args:
            provider: Provider name (kimi, glm, watcher)
            model: Model name
            tool_name: Tool being tested
            variation: Test variation
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            features: Dictionary of activated features
        
        Returns:
            Prompt record with cost calculation
        """
        # Increment counters
        self.counters["total_prompts"] += 1
        self.counters["prompts_by_provider"][provider] = self.counters["prompts_by_provider"].get(provider, 0) + 1
        self.counters["prompts_by_model"][model] = self.counters["prompts_by_model"].get(model, 0) + 1
        self.counters["prompts_by_tool"][tool_name] = self.counters["prompts_by_tool"].get(tool_name, 0) + 1
        
        # Track tokens
        self.counters["token_usage"]["total_input_tokens"] += input_tokens
        self.counters["token_usage"]["total_output_tokens"] += output_tokens
        self.counters["token_usage"]["total_tokens"] += (input_tokens + output_tokens)
        
        provider_tokens = self.counters["token_usage"]["by_provider"][provider]
        provider_tokens["input"] += input_tokens
        provider_tokens["output"] += output_tokens
        provider_tokens["total"] += (input_tokens + output_tokens)
        
        # Track features
        features = features or {}
        
        if features.get("web_search"):
            self.counters["feature_usage"]["web_search"][provider] += 1
            self.counters["feature_usage"]["web_search"]["total"] += 1
        
        if features.get("file_upload"):
            self.counters["feature_usage"]["file_upload"][provider] += 1
            self.counters["feature_usage"]["file_upload"]["total"] += 1
        
        if features.get("thinking_mode"):
            level = features.get("thinking_mode_level", "basic")
            self.counters["feature_usage"]["thinking_mode"][level] += 1
            self.counters["feature_usage"]["thinking_mode"]["total"] += 1
        
        if features.get("tool_use"):
            self.counters["feature_usage"]["tool_use"][provider] += 1
            self.counters["feature_usage"]["tool_use"]["total"] += 1
        
        # Calculate cost
        cost = self._calculate_cost(provider, model, input_tokens, output_tokens, features)
        
        # Update cost tracking
        self.counters["cost_tracking"]["total_cost_usd"] += cost
        self.counters["cost_tracking"]["by_provider"][provider] += cost
        
        if features.get("web_search"):
            web_search_cost = 0.01 if provider == "glm" else 0.0
            self.counters["cost_tracking"]["by_feature"]["web_search"] += web_search_cost
        
        # Create prompt record
        prompt_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt_number": self.counters["total_prompts"],
            "provider": provider,
            "model": model,
            "tool": tool_name,
            "variation": variation,
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens
            },
            "features": features,
            "cost_usd": cost
        }
        
        # Add to history (keep last 1000)
        self.counters["prompt_history"].append(prompt_record)
        if len(self.counters["prompt_history"]) > 1000:
            self.counters["prompt_history"] = self.counters["prompt_history"][-1000:]
        
        # Save counters
        self.save()
        
        return prompt_record
    
    def _calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        features: Dict[str, Any]
    ) -> float:
        """Calculate cost for a prompt."""
        
        if not self.pricing:
            return 0.0
        
        try:
            # Get model pricing
            if provider == "kimi":
                model_pricing = self.pricing["kimi"]["models"].get(model, {}).get("pricing", {})
                # Use cache miss pricing for simplicity
                input_cost = (input_tokens / 1_000_000) * model_pricing.get("input_cache_miss", 0)
                output_cost = (output_tokens / 1_000_000) * model_pricing.get("output", 0)
                base_cost = input_cost + output_cost
                
            elif provider == "glm":
                model_pricing = self.pricing["glm"]["models"].get(model, {}).get("pricing", {})
                input_cost = (input_tokens / 1_000_000) * model_pricing.get("input", 0)
                output_cost = (output_tokens / 1_000_000) * model_pricing.get("output", 0)
                base_cost = input_cost + output_cost
                
                # Add web search cost if used
                if features.get("web_search"):
                    base_cost += 0.01
            
            else:  # watcher
                # Watcher uses GLM-4-Flash (free)
                base_cost = 0.0
            
            return round(base_cost, 6)
        
        except Exception as e:
            logger.error(f"Cost calculation error: {e}")
            return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all counters."""
        return {
            "session_start": self.counters["session_start"],
            "total_prompts": self.counters["total_prompts"],
            "prompts_by_provider": self.counters["prompts_by_provider"],
            "top_models": self._get_top_items(self.counters["prompts_by_model"], 5),
            "top_tools": self._get_top_items(self.counters["prompts_by_tool"], 10),
            "feature_usage": self.counters["feature_usage"],
            "token_usage": self.counters["token_usage"],
            "cost_tracking": self.counters["cost_tracking"]
        }
    
    def _get_top_items(self, items_dict: Dict[str, int], limit: int) -> List[Dict[str, Any]]:
        """Get top N items from a dictionary."""
        sorted_items = sorted(items_dict.items(), key=lambda x: x[1], reverse=True)
        return [{"name": k, "count": v} for k, v in sorted_items[:limit]]
    
    def save(self):
        """Save counters to file."""
        try:
            self.results_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.counter_file, "w", encoding="utf-8") as f:
                json.dump(self.counters, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved prompt counters: {self.counter_file}")
        
        except Exception as e:
            logger.error(f"Failed to save prompt counters: {e}")
    
    def load(self):
        """Load counters from file."""
        try:
            if self.counter_file.exists():
                with open(self.counter_file, "r", encoding="utf-8") as f:
                    self.counters = json.load(f)
                
                logger.info(f"Loaded prompt counters: {self.counter_file}")
        
        except Exception as e:
            logger.error(f"Failed to load prompt counters: {e}")
    
    def print_summary(self):
        """Print a formatted summary to console."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("  PROMPT COUNTER SUMMARY")
        print("="*60)
        
        print(f"\nTotal Prompts: {summary['total_prompts']}")
        
        print("\nPrompts by Provider:")
        for provider, count in summary['prompts_by_provider'].items():
            print(f"  {provider}: {count}")
        
        print("\nTop Models:")
        for item in summary['top_models']:
            print(f"  {item['name']}: {item['count']}")
        
        print("\nTop Tools:")
        for item in summary['top_tools']:
            print(f"  {item['name']}: {item['count']}")
        
        print("\nFeature Usage:")
        print(f"  Web Search: {summary['feature_usage']['web_search']['total']}")
        print(f"    - Kimi: {summary['feature_usage']['web_search']['kimi']}")
        print(f"    - GLM: {summary['feature_usage']['web_search']['glm']}")
        print(f"  File Upload: {summary['feature_usage']['file_upload']['total']}")
        print(f"    - Kimi: {summary['feature_usage']['file_upload']['kimi']}")
        print(f"    - GLM: {summary['feature_usage']['file_upload']['glm']}")
        print(f"  Thinking Mode: {summary['feature_usage']['thinking_mode']['total']}")
        print(f"    - Basic: {summary['feature_usage']['thinking_mode']['basic']}")
        print(f"    - Deep: {summary['feature_usage']['thinking_mode']['deep']}")
        print(f"    - Expert: {summary['feature_usage']['thinking_mode']['expert']}")
        print(f"  Tool Use: {summary['feature_usage']['tool_use']['total']}")
        
        print("\nToken Usage:")
        print(f"  Total Input: {summary['token_usage']['total_input_tokens']:,}")
        print(f"  Total Output: {summary['token_usage']['total_output_tokens']:,}")
        print(f"  Total: {summary['token_usage']['total_tokens']:,}")
        
        print("\nCost Tracking:")
        print(f"  Total Cost: ${summary['cost_tracking']['total_cost_usd']:.4f}")
        print(f"  Kimi: ${summary['cost_tracking']['by_provider']['kimi']:.4f}")
        print(f"  GLM: ${summary['cost_tracking']['by_provider']['glm']:.4f}")
        print(f"  Watcher: ${summary['cost_tracking']['by_provider']['watcher']:.4f}")
        
        print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    counter = PromptCounter()
    
    # Record a prompt
    counter.record_prompt(
        provider="kimi",
        model="kimi-k2-0905-preview",
        tool_name="chat",
        variation="basic_functionality",
        input_tokens=500,
        output_tokens=200,
        features={
            "web_search": True,
            "thinking_mode": True,
            "thinking_mode_level": "deep"
        }
    )
    
    # Print summary
    counter.print_summary()

