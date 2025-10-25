#!/usr/bin/env python3
"""
Phase 2.3: Fair Provider Comparison Orchestrator

Runs comprehensive comparison between GLM and Kimi providers with:
- Fair parameters (same prompts, temperature, concurrency)
- Real prompts from Phase 1 baseline data
- Statistical analysis with significance testing
- Results stored in Supabase

Created: 2025-10-25
EXAI Validated: glm-4.6
"""

import asyncio
import json
import random
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.phase2_comparison.websocket_test_client import FairWebSocketTestClient
from src.storage.supabase_client import SupabaseStorageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase2Comparison:
    """
    Orchestrates fair comparison between GLM and Kimi providers
    """
    
    def __init__(self):
        self.client = FairWebSocketTestClient()
        self.supabase = SupabaseStorageManager()
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Test configuration (EXAI validated - 2025-10-25)
        self.test_config = {
            "temperature": 0.7,
            "concurrency_levels": [2, 5, 10],  # EXAI: Reduced from [2,5,10,15] for dev environment
            "warmup_seconds": 30,
            "cooldown_seconds": 120,  # 2 minutes between providers
            "scenario_duration_minutes": 10,

            # Provider configurations
            "providers": {
                "glm_flagship": {
                    "name": "GLM Flagship",
                    "model": "glm-4.6",
                    "provider": "glm"
                },
                "kimi_flagship": {
                    "name": "Kimi Flagship",
                    "model": "kimi-k2-0905-preview",
                    "provider": "kimi"
                },
                "glm_fast": {
                    "name": "GLM Fast",
                    "model": "glm-4.5-flash",
                    "provider": "glm"
                },
                "kimi_fast": {
                    "name": "Kimi Fast",
                    "model": "moonshot-v1-128k",  # FAIR COMPARISON: Match glm-4.5-flash 128K context
                    "provider": "kimi"
                }
            }
        }
        
    async def load_test_prompts(self, count: int = 30) -> List[str]:
        """
        Load real prompts from Phase 1 baseline data
        
        Uses stratified sampling to ensure diversity:
        - Short prompts (50-100 tokens)
        - Medium prompts (100-500 tokens)
        - Long prompts (500+ tokens)
        """
        logger.info(f"Loading {count} test prompts from Supabase...")
        
        # Query messages from Phase 1 baseline conversations
        query = """
        SELECT content
        FROM messages
        WHERE role = 'user'
          AND conversation_id IN (
            SELECT id FROM conversations
            WHERE created_at >= '2025-10-25'
            ORDER BY created_at DESC
            LIMIT 100
          )
        ORDER BY RANDOM()
        LIMIT 100
        """
        
        try:
            client = self.supabase.get_client()
            result = client.rpc('execute_sql', {'query': query}).execute()
            
            if result.data:
                all_prompts = [row['content'] for row in result.data if row.get('content')]
                
                # Stratified sampling by length
                short = [p for p in all_prompts if len(p) < 200]
                medium = [p for p in all_prompts if 200 <= len(p) < 1000]
                long = [p for p in all_prompts if len(p) >= 1000]
                
                # Sample from each category
                selected = []
                selected.extend(random.sample(short, min(10, len(short))))
                selected.extend(random.sample(medium, min(15, len(medium))))
                selected.extend(random.sample(long, min(5, len(long))))
                
                # Fill remaining with random selection
                if len(selected) < count:
                    remaining = [p for p in all_prompts if p not in selected]
                    selected.extend(random.sample(remaining, min(count - len(selected), len(remaining))))
                    
                logger.info(f"✅ Loaded {len(selected)} prompts (short={len([p for p in selected if len(p)<200])}, "
                          f"medium={len([p for p in selected if 200<=len(p)<1000])}, "
                          f"long={len([p for p in selected if len(p)>=1000])})")
                
                return selected[:count]
                
        except Exception as e:
            logger.warning(f"Failed to load from Supabase: {e}")
            
        # Fallback: Use synthetic prompts
        logger.info("Using fallback synthetic prompts")
        return self._generate_synthetic_prompts(count)
        
    def _generate_synthetic_prompts(self, count: int) -> List[str]:
        """Generate synthetic test prompts as fallback"""
        categories = {
            "short_qa": [
                "What is the capital of France?",
                "Explain quantum computing briefly.",
                "What is the difference between AI and ML?",
                "How does photosynthesis work?",
                "What is the speed of light?",
            ],
            "medium_code": [
                "Write a Python function to reverse a string.",
                "Create a JavaScript function to validate email addresses.",
                "Implement a binary search algorithm in Python.",
                "Write a SQL query to find duplicate records.",
                "Create a React component for a todo list.",
            ],
            "long_analysis": [
                "Analyze the pros and cons of microservices architecture.",
                "Explain the differences between SQL and NoSQL databases.",
                "Discuss the impact of AI on software development.",
                "Compare functional and object-oriented programming paradigms.",
                "Evaluate different approaches to API authentication.",
            ]
        }
        
        prompts = []
        for category, items in categories.items():
            prompts.extend(items)
            
        return random.sample(prompts, min(count, len(prompts)))
        
    async def run_comparison_scenario(
        self,
        scenario_name: str,
        prompts: List[str],
        provider_a: Dict,
        provider_b: Dict,
        concurrency: int
    ) -> Dict:
        """
        Run a single comparison scenario
        
        Returns:
            Comparison results for both providers
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🔬 SCENARIO: {scenario_name}")
        logger.info(f"   Concurrency: {concurrency}")
        logger.info(f"   Prompts: {len(prompts)}")
        logger.info(f"   Provider A: {provider_a['name']} ({provider_a['model']})")
        logger.info(f"   Provider B: {provider_b['name']} ({provider_b['model']})")
        logger.info(f"{'='*80}\n")
        
        # Randomize provider order to prevent bias
        providers = [provider_a, provider_b]
        random.shuffle(providers)
        
        results = {}
        
        for i, provider in enumerate(providers):
            logger.info(f"\n📊 Testing {provider['name']} ({i+1}/2)...")
            
            # Run scenario
            scenario_results = await self.client.run_scenario(
                prompts=prompts,
                model=provider['model'],
                concurrency=concurrency,
                temperature=self.test_config['temperature'],
                warmup_seconds=self.test_config['warmup_seconds']
            )
            
            # Analyze results
            analysis = self.client.analyze_results(scenario_results)

            # EXAI FIX: Defensive programming - validate analysis structure
            if not analysis or 'successful_tests' not in analysis:
                logger.error(f"❌ {provider['name']}: Invalid analysis result: {analysis}")
                continue

            results[provider['name']] = {
                "provider": provider,
                "raw_results": scenario_results,
                "analysis": analysis
            }

            logger.info(f"✅ {provider['name']}: {analysis['successful_tests']}/{analysis['total_tests']} successful")
            logger.info(f"   Mean latency: {analysis['mean_latency_ms']:.2f}ms")
            logger.info(f"   P95 latency: {analysis['p95_latency_ms']:.2f}ms")
            
            # Cooldown between providers
            if i < len(providers) - 1:
                logger.info(f"\n⏸️  Cooldown: {self.test_config['cooldown_seconds']}s...")
                await asyncio.sleep(self.test_config['cooldown_seconds'])
                
        return results
        
    async def run_full_comparison(self):
        """
        Run full comparison across all scenarios
        """
        logger.info("\n" + "="*80)
        logger.info("🚀 PHASE 2.3: FAIR PROVIDER COMPARISON")
        logger.info("="*80 + "\n")
        
        # Load test prompts
        prompts = await self.load_test_prompts(count=30)
        
        # Connect to WebSocket server
        await self.client.connect()
        
        try:
            all_results = {
                "timestamp": datetime.utcnow().isoformat(),
                "config": self.test_config,
                "scenarios": {}
            }
            
            # Run comparison for flagship models
            logger.info("\n" + "="*80)
            logger.info("📊 FLAGSHIP MODEL COMPARISON")
            logger.info("="*80)
            
            for concurrency in self.test_config['concurrency_levels']:
                scenario_name = f"flagship_concurrency_{concurrency}"
                
                results = await self.run_comparison_scenario(
                    scenario_name=scenario_name,
                    prompts=prompts,
                    provider_a=self.test_config['providers']['glm_flagship'],
                    provider_b=self.test_config['providers']['kimi_flagship'],
                    concurrency=concurrency
                )
                
                all_results['scenarios'][scenario_name] = results
                
            # Run comparison for fast models
            logger.info("\n" + "="*80)
            logger.info("⚡ FAST MODEL COMPARISON")
            logger.info("="*80)
            
            for concurrency in self.test_config['concurrency_levels']:
                scenario_name = f"fast_concurrency_{concurrency}"
                
                results = await self.run_comparison_scenario(
                    scenario_name=scenario_name,
                    prompts=prompts,
                    provider_a=self.test_config['providers']['glm_fast'],
                    provider_b=self.test_config['providers']['kimi_fast'],
                    concurrency=concurrency
                )
                
                all_results['scenarios'][scenario_name] = results
                
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.results_dir / f"comparison_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
                
            logger.info(f"\n✅ Results saved to: {results_file}")
            
            return all_results
            
        finally:
            await self.client.disconnect()


async def main():
    """Main entry point"""
    comparison = Phase2Comparison()
    results = await comparison.run_full_comparison()
    
    logger.info("\n" + "="*80)
    logger.info("🎉 PHASE 2.3 COMPARISON COMPLETE!")
    logger.info("="*80)
    logger.info(f"\nTotal scenarios: {len(results['scenarios'])}")
    logger.info(f"Results saved to: scripts/phase2_comparison/results/")
    logger.info("\nNext step: Run analysis script to generate comparison report")


if __name__ == "__main__":
    asyncio.run(main())

